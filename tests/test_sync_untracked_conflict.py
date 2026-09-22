"""Tests for /api/sync's recovery from an UNTRACKED file blocking `git pull`.

Reproduces the exact failure reported from the running app: a local run
(a scan, or the market-motion rescore/seed scans) writes a fresh per-ticker
cache file that the automated workflow's own commit also happens to create,
so `git pull --ff-only` refuses with "untracked working tree files would be
overwritten by merge" — a different git error than a conflict on a file it
already tracks, and the existing `git checkout -- data/` recovery does
nothing for it (checkout never touches untracked files), so the retry used
to fail with the identical error.
"""
import shutil
import subprocess
from pathlib import Path

import pytest

import dashboard


def _working_git():
    for candidate in (shutil.which("git"), "/Library/Developer/CommandLineTools/usr/bin/git"):
        if candidate and subprocess.run([candidate, "--version"], capture_output=True).returncode == 0:
            return candidate
    pytest.skip("no usable git binary")


def _run(git, args, cwd):
    return subprocess.run([git, *args], cwd=cwd, capture_output=True, text=True, check=True)


def _init_identity(git, repo):
    _run(git, ["config", "user.email", "test@example.com"], repo)
    _run(git, ["config", "user.name", "Test User"], repo)


@pytest.fixture
def repo_with_untracked_conflict(tmp_path):
    """A local clone whose `git pull` is blocked by an untracked file at the
    exact path the remote's newest commit also creates, plus a second,
    harmless untracked file elsewhere that must survive untouched."""
    git = _working_git()
    remote = tmp_path / "remote.git"
    seed = tmp_path / "seed"
    other = tmp_path / "other"
    local = tmp_path / "local"

    # The seed commit deliberately does NOT include RMBI's cache file at all —
    # reproducing the real case exactly: a ticker neither side has ever fetched
    # before, so the file exists nowhere in git history when `local` diverges.
    _run(git, ["init", "--bare", "--initial-branch=main", str(remote)], tmp_path)
    _run(git, ["clone", str(remote), str(seed)], tmp_path)
    _init_identity(git, seed)
    (seed / "data").mkdir()
    (seed / "data" / "fundamentals_cache").mkdir()
    (seed / "data" / "fundamentals_cache" / "other_ticker.json").write_text('{"v": "unrelated"}\n')
    _run(git, ["add", "."], seed)
    _run(git, ["commit", "-m", "base"], seed)
    _run(git, ["push", "origin", "HEAD:main"], seed)

    _run(git, ["clone", str(remote), str(local)], tmp_path)
    _init_identity(git, local)

    # The automated workflow is the FIRST to commit RMBI's cache file...
    _run(git, ["clone", str(remote), str(other)], tmp_path)
    _init_identity(git, other)
    (other / "data" / "fundamentals_cache" / "RMBI_fundamentals.json").write_text('{"v": "from-github"}\n')
    _run(git, ["add", "."], other)
    _run(git, ["commit", "-m", "chore: update fundamental cache"], other)
    _run(git, ["push", "origin", "HEAD:main"], other)

    # ...while THIS machine, meanwhile, ran a local scan that independently
    # re-fetched the same ticker and left it sitting there UNTRACKED.
    (local / "data" / "fundamentals_cache" / "RMBI_fundamentals.json").write_text('{"v": "local-untracked"}\n')
    # A second, unrelated untracked file that git's error never names — the
    # fix must never touch this one.
    (local / "data" / "market_motion").mkdir(parents=True)
    (local / "data" / "market_motion" / "unrelated.json").write_text('{"keep": "me"}\n')

    return git, remote, local


def test_sync_recovers_from_untracked_file_conflict(repo_with_untracked_conflict, monkeypatch):
    git, remote, local = repo_with_untracked_conflict
    pre = subprocess.run([git, "pull", "--ff-only"], cwd=local, capture_output=True, text=True)
    assert pre.returncode != 0
    assert "untracked working tree files would be overwritten" in (pre.stdout + pre.stderr)

    monkeypatch.setattr(dashboard, "PROJECT_ROOT", local)
    monkeypatch.setattr(dashboard, "_git_binary", lambda: git)
    monkeypatch.chdir(local)
    client = dashboard.app.test_client()

    body = client.post("/api/sync").get_json()

    assert body["success"] is True, body["output"]
    assert (local / "data" / "fundamentals_cache" / "RMBI_fundamentals.json").read_text() == '{"v": "from-github"}\n'
    # the unrelated untracked file git's error never named must survive untouched
    assert (local / "data" / "market_motion" / "unrelated.json").read_text() == '{"keep": "me"}\n'


def test_sync_leaves_the_conflict_alone_when_the_file_is_outside_data(tmp_path, monkeypatch):
    """If the parsed path can't be confirmed both inside data/ AND actually
    untracked, the recovery must do nothing rather than guess — verified here
    with a conflicting file at the repo ROOT (outside data/, e.g. a README the
    automated workflow also happens to touch), so the containment check
    rejects it and the original conflict is reported back to the user
    unchanged, not silently swallowed by deleting something it shouldn't."""
    git = _working_git()
    remote = tmp_path / "remote.git"
    seed = tmp_path / "seed"
    other = tmp_path / "other"
    local = tmp_path / "local"

    _run(git, ["init", "--bare", "--initial-branch=main", str(remote)], tmp_path)
    _run(git, ["clone", str(remote), str(seed)], tmp_path)
    _init_identity(git, seed)
    (seed / "README_CACHE.md").write_text("base\n")
    _run(git, ["add", "."], seed)
    _run(git, ["commit", "-m", "base"], seed)
    _run(git, ["push", "origin", "HEAD:main"], seed)

    _run(git, ["clone", str(remote), str(local)], tmp_path)
    _init_identity(git, local)

    _run(git, ["clone", str(remote), str(other)], tmp_path)
    _init_identity(git, other)
    (other / "NOTES.md").write_text("from github\n")
    _run(git, ["add", "."], other)
    _run(git, ["commit", "-m", "add notes"], other)
    _run(git, ["push", "origin", "HEAD:main"], other)

    # Untracked at the repo root, outside data/ — must never be deleted.
    (local / "NOTES.md").write_text("local untracked, outside data/\n")

    monkeypatch.setattr(dashboard, "PROJECT_ROOT", local)
    monkeypatch.setattr(dashboard, "_git_binary", lambda: git)
    monkeypatch.chdir(local)
    client = dashboard.app.test_client()

    body = client.post("/api/sync").get_json()

    assert body["success"] is False
    assert "untracked working tree files" in body["output"]
    assert (local / "NOTES.md").read_text() == "local untracked, outside data/\n"


class TestSafeUntrackedConflictPaths:
    """Unit tests for the path-safety filter in isolation, with fabricated
    git output — this is what actually enforces "only data/, never
    position/, never outside the project, and only if truly untracked",
    independent of any real git invocation."""

    GIT_ERROR = (
        "From github.com:BadriPratti/stock-screener\n"
        " * branch            main       -> FETCH_HEAD\n"
        "error: The following untracked working tree files would be overwritten by merge:\n"
        "\t{path}\n"
        "Please move or remove them before you merge.\n"
        "Aborting\n"
    )

    def test_returns_none_for_an_unrelated_error(self, tmp_path):
        assert dashboard._safe_untracked_conflict_paths("fatal: not a git repository", tmp_path, "git") is None

    def test_rejects_a_path_outside_data(self, tmp_path):
        (tmp_path / "position").mkdir()
        (tmp_path / "position" / "accounts.csv").write_text("real account data\n")
        error = self.GIT_ERROR.format(path="position/accounts.csv")
        assert dashboard._safe_untracked_conflict_paths(error, tmp_path, "git") == []

    def test_rejects_path_traversal_out_of_the_project(self, tmp_path):
        error = self.GIT_ERROR.format(path="data/../../etc/passwd")
        assert dashboard._safe_untracked_conflict_paths(error, tmp_path, "git") == []

    def test_rejects_a_path_that_is_actually_tracked(self, tmp_path):
        git = _working_git()
        _run(git, ["init", "--initial-branch=main", str(tmp_path)], tmp_path)
        _init_identity(git, tmp_path)
        (tmp_path / "data").mkdir()
        tracked = tmp_path / "data" / "committed.json"
        tracked.write_text("{}\n")
        _run(git, ["add", "."], tmp_path)
        _run(git, ["commit", "-m", "seed"], tmp_path)

        error = self.GIT_ERROR.format(path="data/committed.json")
        assert dashboard._safe_untracked_conflict_paths(error, tmp_path, git) == []
        assert tracked.exists()

    def test_accepts_a_genuinely_untracked_file_inside_data(self, tmp_path):
        git = _working_git()
        _run(git, ["init", "--initial-branch=main", str(tmp_path)], tmp_path)
        _init_identity(git, tmp_path)
        (tmp_path / "data" / "fundamentals_cache").mkdir(parents=True)
        loose = tmp_path / "data" / "fundamentals_cache" / "RMBI_fundamentals.json"
        loose.write_text("{}\n")

        error = self.GIT_ERROR.format(path="data/fundamentals_cache/RMBI_fundamentals.json")
        result = dashboard._safe_untracked_conflict_paths(error, tmp_path, git)
        assert result == [loose.resolve()]
