import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ci_push_with_rebase.sh"


def working_git():
    for candidate in dict.fromkeys(filter(None, (
        shutil.which("git"),
        "/Library/Developer/CommandLineTools/usr/bin/git",
    ))):
        try:
            result = subprocess.run([candidate, "--version"], capture_output=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            continue
        if result.returncode == 0:
            return candidate
    pytest.skip("no usable git binary")


def run(git, args, cwd, check=True):
    return subprocess.run(
        [git, *args], cwd=cwd, check=check, text=True, capture_output=True,
    )


def commit_file(git, repo, name, contents, message):
    (repo / name).write_text(contents, encoding="utf-8")
    run(git, ["add", name], repo)
    run(git, ["commit", "-m", message], repo)


def make_shallow_clone(tmp_path):
    git = working_git()
    remote = tmp_path / "remote.git"
    seed = tmp_path / "seed"
    clone = tmp_path / "clone"
    run(git, ["init", "--bare", str(remote)], tmp_path)
    run(git, ["init", str(seed)], tmp_path)
    run(git, ["config", "user.email", "test@example.com"], seed)
    run(git, ["config", "user.name", "Test User"], seed)
    commit_file(git, seed, "base.txt", "base\n", "base")
    run(git, ["branch", "-M", "main"], seed)
    run(git, ["remote", "add", "origin", str(remote)], seed)
    run(git, ["push", "-u", "origin", "main"], seed)
    run(git, ["clone", "--depth", "1", "--branch", "main", f"file://{remote}", str(clone)], tmp_path)
    run(git, ["config", "user.email", "test@example.com"], clone)
    run(git, ["config", "user.name", "Test User"], clone)
    assert run(git, ["rev-parse", "--is-shallow-repository"], clone).stdout.strip() == "true"
    return git, remote, clone


def invoke(git, clone, attempts=4):
    env = dict(os.environ, PUSH_RETRY_SLEEP="0")
    env["PATH"] = str(Path(git).parent) + os.pathsep + env.get("PATH", "")
    return subprocess.run(
        [str(SCRIPT), "main", str(attempts)], cwd=clone, env=env,
        text=True, capture_output=True,
    )


def test_clean_push_from_shallow_clone(tmp_path):
    git, remote, clone = make_shallow_clone(tmp_path)
    commit_file(git, clone, "local.txt", "local\n", "local")

    result = invoke(git, clone)

    assert result.returncode == 0, result.stdout + result.stderr
    assert run(git, ["show", "main:local.txt"], remote).stdout == "local\n"


def test_remote_advance_is_rebased_then_pushed(tmp_path):
    git, remote, clone = make_shallow_clone(tmp_path)
    commit_file(git, clone, "local.txt", "local\n", "local")
    other = tmp_path / "other"
    run(git, ["clone", "--branch", "main", str(remote), str(other)], tmp_path)
    run(git, ["config", "user.email", "test@example.com"], other)
    run(git, ["config", "user.name", "Test User"], other)
    commit_file(git, other, "remote.txt", "remote\n", "remote")
    run(git, ["push", "origin", "main"], other)

    result = invoke(git, clone)

    assert result.returncode == 0, result.stdout + result.stderr
    assert run(git, ["show", "main:local.txt"], remote).stdout == "local\n"
    assert run(git, ["show", "main:remote.txt"], remote).stdout == "remote\n"


def test_permanently_rejected_push_exits_nonzero_after_max_attempts(tmp_path):
    git, remote, clone = make_shallow_clone(tmp_path)
    hook = remote / "hooks" / "pre-receive"
    hook.write_text("#!/usr/bin/env bash\nexit 1\n", encoding="utf-8")
    hook.chmod(0o755)
    commit_file(git, clone, "rejected.txt", "rejected\n", "rejected")

    result = invoke(git, clone, attempts=2)

    assert result.returncode != 0
    assert "::error title=push-failed::could not push to main after 2 attempts" in result.stdout


def test_script_never_force_pushes():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "git push origin \"HEAD:$branch\"" in text
    assert "--force" not in text


def _advance_remote_with_conflict(git, remote, tmp_path):
    other = tmp_path / "other"
    run(git, ["clone", "--branch", "main", str(remote), str(other)], tmp_path)
    run(git, ["config", "user.email", "test@example.com"], other)
    run(git, ["config", "user.name", "Test User"], other)
    commit_file(git, other, "base.txt", "remote version\n", "remote edit")
    run(git, ["push", "origin", "main"], other)


def test_content_conflict_is_resolved_for_this_run_only_from_the_third_attempt(tmp_path):
    git, remote, clone = make_shallow_clone(tmp_path)
    commit_file(git, clone, "base.txt", "local version\n", "local edit")
    _advance_remote_with_conflict(git, remote, tmp_path)

    result = invoke(git, clone, attempts=4)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "attempt 3" in result.stdout
    assert run(git, ["show", "main:base.txt"], remote).stdout == "local version\n"


def test_conflict_with_too_few_attempts_fails_loudly_and_leaves_no_rebase_in_progress(tmp_path):
    git, remote, clone = make_shallow_clone(tmp_path)
    commit_file(git, clone, "base.txt", "local version\n", "local edit")
    _advance_remote_with_conflict(git, remote, tmp_path)

    result = invoke(git, clone, attempts=2)

    assert result.returncode != 0
    assert "push-failed" in result.stdout
    assert run(git, ["show", "main:base.txt"], remote).stdout == "remote version\n"       # nothing was clobbered
    assert not (clone / ".git" / "rebase-merge").exists() and not (clone / ".git" / "rebase-apply").exists()
