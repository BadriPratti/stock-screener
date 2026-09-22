import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.screening import market_motion
from src.screening.market_motion_publisher import publish_frames


def _git_binary():
    candidate = Path("/Library/Developer/CommandLineTools/usr/bin/git")
    return str(candidate) if candidate.exists() else (shutil.which("git") or "git")


def _git(cwd, *args, check=True):
    result = subprocess.run(
        [_git_binary(), *args], cwd=cwd,
        capture_output=True, text=True, encoding="utf-8",
    )
    if check and result.returncode:
        raise AssertionError(result.stderr or result.stdout)
    return result


def _repo(tmp_path):
    remote = tmp_path / "remote.git"
    seed = tmp_path / "seed"
    clone = tmp_path / "clone"
    _git(tmp_path, "init", "--bare", str(remote))
    _git(tmp_path, "init", "-b", "main", str(seed))
    _git(seed, "config", "user.name", "Test User")
    _git(seed, "config", "user.email", "test@example.invalid")
    (seed / "tracked.txt").write_text("base\n", encoding="utf-8")
    _git(seed, "add", "tracked.txt")
    _git(seed, "commit", "-m", "base")
    _git(seed, "remote", "add", "origin", str(remote))
    _git(seed, "push", "-u", "origin", "main")
    _git(remote, "symbolic-ref", "HEAD", "refs/heads/main")
    _git(tmp_path, "clone", str(remote), str(clone))
    _git(clone, "config", "user.name", "Test User")
    _git(clone, "config", "user.email", "test@example.invalid")
    return remote, seed, clone


def _write_frame(repo, minute=35, ticker="AAA"):
    generated = datetime(2026, 9, 18, 13, minute, tzinfo=timezone.utc)
    frame = market_motion.build_frame(
        run_kind=market_motion.RUN_KIND_INTRADAY,
        generated_at=generated,
        session_date="2026-09-18",
        points=[market_motion.make_point(
            ticker, market_motion.EVAL_QUALIFIED, score=90, rs=0.2,
        )],
        scope={"mode": "tracked_roster", "completed": True},
    )
    return market_motion.write_frame(frame, repo / "data" / "market_motion")


def test_publish_uses_one_frame_only_commit_and_preserves_local_changes(tmp_path):
    remote, _, clone = _repo(tmp_path)
    frame_path = _write_frame(clone)
    frame_bytes = frame_path.read_bytes()
    old_tip = _git(clone, "rev-parse", "origin/main").stdout.strip()
    (clone / "tracked.txt").write_text("dirty worktree\n", encoding="utf-8")
    (clone / "staged.txt").write_text("staged\n", encoding="utf-8")
    _git(clone, "add", "staged.txt")
    cached_before = _git(clone, "diff", "--cached", "--binary").stdout

    result = publish_frames(clone)

    assert result["status"] == "published"
    assert result["published"] == [frame_path.relative_to(clone).as_posix()]
    remote_tip = _git(remote, "rev-parse", "main").stdout.strip()
    assert _git(remote, "rev-parse", f"{remote_tip}^").stdout.strip() == old_tip
    changed = _git(remote, "diff-tree", "--no-commit-id", "--name-only", "-r", remote_tip).stdout.splitlines()
    assert changed == result["published"]
    assert _git(clone, "symbolic-ref", "--short", "HEAD").stdout.strip() == "main"
    assert _git(clone, "diff", "--cached", "--binary").stdout == cached_before
    assert (clone / "tracked.txt").read_bytes() == b"dirty worktree\n"
    assert frame_path.read_bytes() == frame_bytes
    assert _git(clone, "pull", "--ff-only").returncode == 0


def test_pull_failure_restores_published_frame(tmp_path):
    _, _, clone = _repo(tmp_path)
    frame_path = _write_frame(clone)
    before = frame_path.read_bytes()
    result = publish_frames(clone, pull_fn=lambda: (False, "synthetic sync failure"))
    assert result["status"] == "published"
    assert "local sync pending" in result["reason"]
    assert frame_path.read_bytes() == before


def test_non_fast_forward_race_refetches_rebuilds_and_succeeds(tmp_path):
    remote, seed, clone = _repo(tmp_path)
    frame_path = _write_frame(clone)
    marker = tmp_path / "advanced-once"
    hook = clone / ".git" / "hooks" / "pre-push"
    hook.write_text(
        "#!/bin/sh\n"
        f"if [ ! -f '{marker}' ]; then\n"
        f"  touch '{marker}'\n"
        f"  printf 'race\\n' > '{seed / 'race.txt'}'\n"
        f"  '{_git_binary()}' -C '{seed}' add race.txt\n"
        f"  '{_git_binary()}' -C '{seed}' commit -m race\n"
        f"  '{_git_binary()}' -C '{seed}' push origin main\n"
        "fi\n",
        encoding="utf-8",
    )
    hook.chmod(0o755)

    result = publish_frames(clone, max_attempts=3)

    assert result["status"] == "published"
    assert marker.exists()
    tip = _git(remote, "rev-parse", "main").stdout.strip()
    assert _git(remote, "show", f"{tip}:race.txt").stdout == "race\n"
    assert json.loads(_git(remote, "show", f"{tip}:{frame_path.relative_to(clone).as_posix()}").stdout)


def test_permanent_remote_rejection_soft_fails_and_keeps_frame(tmp_path):
    remote, _, clone = _repo(tmp_path)
    frame_path = _write_frame(clone)
    before = frame_path.read_bytes()
    hook = remote / "hooks" / "pre-receive"
    hook.write_text("#!/bin/sh\necho rejected by test >&2\nexit 1\n", encoding="utf-8")
    hook.chmod(0o755)
    result = publish_frames(clone)
    assert result["status"] == "failed"
    assert "git push failed" in result["reason"]
    assert frame_path.read_bytes() == before


def test_existing_remote_path_is_diverged_and_not_overwritten(tmp_path):
    remote, seed, clone = _repo(tmp_path)
    remote_path = _write_frame(seed, ticker="REMOTE")
    _git(seed, "add", remote_path.relative_to(seed).as_posix())
    _git(seed, "commit", "-m", "remote frame")
    _git(seed, "push")
    local_path = _write_frame(clone, ticker="LOCAL")
    result = publish_frames(clone)
    assert result["status"] == "nothing_to_publish"
    assert "diverged" in result["reason"]
    assert json.loads(local_path.read_text())["points"][0]["ticker"] == "LOCAL"
    remote_text = _git(remote, "show", f"main:{remote_path.relative_to(seed).as_posix()}").stdout
    assert json.loads(remote_text)["points"][0]["ticker"] == "REMOTE"


def test_invalid_frames_are_reported_and_never_published(tmp_path):
    _, _, clone = _repo(tmp_path)
    invalid = clone / "data" / "market_motion" / "snapshots" / "intraday_rescore" / "bad.json"
    invalid.parent.mkdir(parents=True)
    invalid.write_text("{broken", encoding="utf-8")
    result = publish_frames(clone)
    assert result["status"] == "nothing_to_publish"
    assert "skipped invalid" in result["reason"]


def test_source_uses_only_approved_low_level_mutating_commands():
    source = Path(__file__).parents[1].joinpath(
        "src", "screening", "market_motion_publisher.py",
    ).read_text(encoding="utf-8")
    forbidden_argv = (
        '["add",', '["commit",', '["checkout",', '["reset",',
        '["stash",', '["rebase",', '"--force"',
    )
    assert not any(token in source for token in forbidden_argv)
