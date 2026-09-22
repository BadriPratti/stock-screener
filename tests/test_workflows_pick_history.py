import shutil
import subprocess
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
DAILY = ROOT / ".github" / "workflows" / "daily_screening_git_storage.yml"
MIDDAY = ROOT / ".github" / "workflows" / "midday_quick_scan.yml"


def _load(path):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _step(workflow, job_name, step_name):
    return next(step for step in workflow["jobs"][job_name]["steps"] if step.get("name") == step_name)


def test_workflows_serialize_with_themselves_but_never_with_each_other():
    # A group shared across the two workflows would let a midday run cancel a
    # PENDING daily run (GitHub keeps one pending run per group); losing the
    # daily scan is the worst outcome, so each workflow only queues behind itself.
    daily, midday = _load(DAILY), _load(MIDDAY)
    assert daily["concurrency"] == {"group": "screening-daily", "cancel-in-progress": False}
    assert midday["concurrency"] == {"group": "screening-midday", "cancel-in-progress": False}
    assert daily["concurrency"]["group"] != midday["concurrency"]["group"]


def test_daily_workflow_wires_full_run_and_stages_history_before_commit():
    workflow = _load(DAILY)
    scan = _step(workflow, "screen-stocks", "Run optimized stock screening")["run"]
    steps = workflow["jobs"]["screen-stocks"]["steps"]
    names = [step.get("name") for step in steps]
    history = _step(workflow, "screen-stocks", "Stage pick history")
    motion = _step(workflow, "screen-stocks", "Stage market motion")

    assert "--run-kind daily-full" in scan
    assert "--enable-llm-agents" in scan
    assert history["continue-on-error"] is True
    assert "git add data/pick_history/" in history["run"]
    assert "::warning" in history["run"], "a failed staging must surface as a run annotation, not a silent green"
    assert "|| true" not in history["run"] and "2>/dev/null" not in history["run"], (
        "never swallow the error silently - that is exactly how an ignored ledger path would go unnoticed"
    )
    assert names.index("Stage pick history") < names.index("Commit updated fundamental cache")
    assert motion["continue-on-error"] is True
    assert "git add data/market_motion/" in motion["run"]
    assert "::warning" in motion["run"]
    assert "|| true" not in motion["run"] and "2>/dev/null" not in motion["run"]
    assert names.index("Stage market motion") < names.index("Commit updated fundamental cache")
    assert workflow["jobs"]["screen-stocks"]["timeout-minutes"] == 120

    upload = _step(workflow, "screen-stocks", "Upload screening results")
    assert "data/pick_history/" in upload["with"]["path"], (
        "the ledger snapshot must be in the run artifacts so a failed push does not lose it"
    )
    assert "data/market_motion/" in upload["with"]["path"]


def test_midday_workflow_is_sample_and_never_references_history():
    workflow = _load(MIDDAY)
    scan = _step(workflow, "quick-scan", "Run quick test scan (100 stocks)")["run"]

    assert "--run-kind midday-sample" in scan
    assert "--test-mode" in scan
    assert "pick_history" not in MIDDAY.read_text(encoding="utf-8")


def test_both_workflows_use_rebase_push_script_and_keep_write_permission():
    for path, job_name in ((DAILY, "screen-stocks"), (MIDDAY, "quick-scan")):
        workflow = _load(path)
        push = _step(workflow, job_name, "Push changes")
        text = path.read_text(encoding="utf-8")
        assert workflow["jobs"][job_name]["permissions"] == {"contents": "write"}
        assert push["if"] == "steps.commit.outputs.has_changes == 'true'"
        assert "scripts/ci_push_with_rebase.sh" in push["run"]
        assert "ad-m/github-push-action" not in text


def _working_git_or_skip():
    candidates = [shutil.which("git"), "/Library/Developer/CommandLineTools/usr/bin/git"]
    errors = []
    for candidate in dict.fromkeys(path for path in candidates if path):
        try:
            probe = subprocess.run(
                [candidate, "--version"], cwd=ROOT, capture_output=True, text=True, timeout=10,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            errors.append(f"{candidate}: {exc}")
            continue
        if probe.returncode == 0:
            return candidate
        errors.append(f"{candidate}: {probe.stderr.strip() or probe.stdout.strip()}")
    pytest.skip("No usable git binary for check-ignore: " + "; ".join(errors))


def test_pick_history_snapshots_are_tracked_but_atomic_temp_files_are_ignored():
    git = _working_git_or_skip()
    snapshot = "data/pick_history/snapshots/daily_full/2026-09-18.json"
    temp = "data/pick_history/snapshots/daily_full/.2026-09-18.json.abc.tmp"

    tracked = subprocess.run([git, "check-ignore", "-q", snapshot], cwd=ROOT)
    ignored_temp = subprocess.run([git, "check-ignore", "-q", temp], cwd=ROOT)

    assert tracked.returncode == 1
    assert ignored_temp.returncode == 0
