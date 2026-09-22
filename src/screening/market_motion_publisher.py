"""Publish immutable market-motion frames without changing the checkout state."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Callable

from src.screening.market_motion import validate_frame


def _default_git_binary() -> str:
    command_line_git = Path("/Library/Developer/CommandLineTools/usr/bin/git")
    return str(command_line_git) if command_line_git.exists() else (shutil.which("git") or "git")


def _result(status: str, published: list[str] | None = None, reason: str | None = None,
            commit: str | None = None) -> dict[str, Any]:
    return {
        "status": status,
        "published": published or [],
        "reason": reason,
        "commit": commit,
    }


def _trim(value: str | None) -> str:
    return " ".join((value or "").strip().split())


def _atomic_restore(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


def _safe_relative(path: Path, repo: Path, frames_dir: PurePosixPath) -> str:
    relative = path.relative_to(repo).as_posix()
    parts = PurePosixPath(relative).parts
    if not parts or PurePosixPath(*parts[:len(frames_dir.parts)]) != frames_dir:
        raise ValueError(f"frame path escaped {frames_dir.as_posix()}")
    if ".." in parts:
        raise ValueError("frame path contains a parent traversal")
    return relative


def publish_frames(
    repo_root: str | os.PathLike[str],
    *,
    git_binary: str | None = None,
    branch: str = "main",
    remote: str = "origin",
    max_attempts: int = 3,
    pull_fn: Callable[[], tuple[bool, str]] | None = None,
    frames_dir: str = "data/market_motion",
) -> dict[str, Any]:
    """Publish new valid frame files through Git's low-level object commands.

    The checkout's ordinary index, checked-out revision, and files are not used
    to construct the pushed revision. After a successful push, identical local
    files are temporarily removed for a fast-forward sync and restored if that
    sync does not reproduce them byte-for-byte.
    """
    try:
        repo = Path(repo_root).resolve()
        frame_root_rel = PurePosixPath(frames_dir)
        if frame_root_rel.is_absolute() or ".." in frame_root_rel.parts or not frame_root_rel.parts:
            return _result("failed", reason="frames_dir must be a repository-relative path")
        frame_root = repo.joinpath(*frame_root_rel.parts)
        snapshots = frame_root / "snapshots"
        binary = git_binary or _default_git_binary()
        attempts = max(1, int(max_attempts))
        notes: list[str] = []

        valid: dict[str, tuple[Path, dict[str, Any]]] = {}
        if snapshots.is_dir():
            for path in sorted(snapshots.rglob("*.json")):
                if path.name.startswith(".") or any(part.startswith(".") for part in path.relative_to(snapshots).parts):
                    continue
                try:
                    if not path.is_file():
                        continue
                    relative = _safe_relative(path.resolve(), repo, frame_root_rel)
                    frame = json.loads(path.read_text(encoding="utf-8"))
                    validate_frame(frame)
                except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
                    try:
                        display = path.relative_to(repo).as_posix()
                    except ValueError:
                        display = path.name
                    notes.append(f"skipped invalid {display}: {_trim(str(exc))}")
                    continue
                valid[relative] = (path, frame)

        def git(args: list[str], *, env: dict[str, str] | None = None,
                input_text: str | None = None) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [binary, *args], cwd=repo, env=env, input=input_text,
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=120, check=False,
            )

        def fail(command: str, proc: subprocess.CompletedProcess[str]) -> dict[str, Any]:
            detail = _trim(proc.stderr) or _trim(proc.stdout) or f"exit {proc.returncode}"
            return _result("failed", reason=f"{command} failed: {detail}")

        candidate_paths: list[str] = []
        candidate_frames: dict[str, dict[str, Any]] = {}
        commit_sha: str | None = None
        for attempt in range(attempts):
            fetched = git(["fetch", remote, branch])
            if fetched.returncode != 0:
                return fail("git fetch", fetched)
            tip = f"{remote}/{branch}"
            tree = git(["ls-tree", "-r", "--name-only", tip, "--", frame_root_rel.as_posix()])
            if tree.returncode != 0:
                return fail("git ls-tree", tree)
            remote_paths = {line for line in tree.stdout.splitlines() if line}

            candidate_paths = []
            candidate_frames = {}
            for relative, (path, frame) in valid.items():
                if relative not in remote_paths:
                    candidate_paths.append(relative)
                    candidate_frames[relative] = frame
                    continue
                shown = git(["show", f"{tip}:{relative}"])
                try:
                    same = shown.returncode == 0 and shown.stdout.encode("utf-8") == path.read_bytes()
                except OSError:
                    same = False
                if not same:
                    note = f"diverged {relative}: remote path already exists"
                    if note not in notes:
                        notes.append(note)

            if not candidate_paths:
                return _result("nothing_to_publish", reason="; ".join(notes) or None)
            candidate_paths.sort()

            with tempfile.TemporaryDirectory(prefix="market-motion-index-") as temp_dir:
                index_path = str(Path(temp_dir) / "index")
                env = os.environ.copy()
                env["GIT_INDEX_FILE"] = index_path
                read = git(["read-tree", tip], env=env)
                if read.returncode != 0:
                    return fail("git read-tree", read)
                for relative in candidate_paths:
                    hashed = git(["hash-object", "-w", "--", relative])
                    if hashed.returncode != 0:
                        return fail("git hash-object", hashed)
                    blob = hashed.stdout.strip()
                    updated = git(
                        ["update-index", "--add", "--cacheinfo", f"100644,{blob},{relative}"],
                        env=env,
                    )
                    if updated.returncode != 0:
                        return fail("git update-index", updated)
                written = git(["write-tree"], env=env)
                if written.returncode != 0:
                    return fail("git write-tree", written)

                dates = sorted({candidate_frames[p]["session_date"] for p in candidate_paths})
                span = dates[0] if len(dates) == 1 else f"{dates[0]}..{dates[-1]}"
                message = f"chore: market-motion frames ({len(candidate_paths)}) {span}"
                identity_env = os.environ.copy()
                name = git(["config", "user.name"])
                email = git(["config", "user.email"])
                if name.returncode != 0 or not name.stdout.strip():
                    identity_env["GIT_AUTHOR_NAME"] = "market-motion"
                    identity_env["GIT_COMMITTER_NAME"] = "market-motion"
                if email.returncode != 0 or not email.stdout.strip():
                    identity_env["GIT_AUTHOR_EMAIL"] = "market-motion@localhost"
                    identity_env["GIT_COMMITTER_EMAIL"] = "market-motion@localhost"
                created = git(
                    ["commit-tree", written.stdout.strip(), "-p", tip, "-m", message], env=identity_env,
                )
                if created.returncode != 0:
                    return fail("git commit-tree", created)
                commit_sha = created.stdout.strip()

            pushed = git(["push", remote, f"{commit_sha}:refs/heads/{branch}"])
            if pushed.returncode == 0:
                break
            rejection = f"{pushed.stdout}\n{pushed.stderr}".lower()
            raced = any(marker in rejection for marker in (
                "non-fast-forward", "fetch first", "stale info", "failed to push some refs",
            )) and "hook declined" not in rejection
            if raced and attempt + 1 < attempts:
                continue
            return fail("git push", pushed)
        else:
            return _result("failed", reason="git push retry limit reached")

        saved: dict[str, bytes] = {}
        for relative in candidate_paths:
            path = repo.joinpath(*PurePosixPath(relative).parts)
            remote_blob = git(["rev-parse", f"{commit_sha}:{relative}"])
            local_blob = git(["hash-object", "--", relative])
            if remote_blob.returncode != 0 or local_blob.returncode != 0:
                continue
            if remote_blob.stdout.strip() != local_blob.stdout.strip():
                continue
            try:
                saved[relative] = path.read_bytes()
                path.unlink()
            except OSError:
                saved.pop(relative, None)

        sync_ok = True
        sync_output = ""
        try:
            if pull_fn is None:
                pulled = git(["pull", "--ff-only", remote, branch])
                sync_ok = pulled.returncode == 0
                sync_output = _trim(pulled.stderr) or _trim(pulled.stdout)
            else:
                sync_ok, sync_output = pull_fn()
                sync_ok = bool(sync_ok)
        except Exception as exc:
            sync_ok = False
            sync_output = str(exc)

        for relative, data in saved.items():
            path = repo.joinpath(*PurePosixPath(relative).parts)
            try:
                matches = path.is_file() and path.read_bytes() == data
            except OSError:
                matches = False
            if not matches:
                sync_ok = False
                _atomic_restore(path, data)
        if not sync_ok:
            detail = _trim(sync_output)
            notes.append("local sync pending" + (f": {detail}" if detail else ""))

        return _result(
            "published", candidate_paths, "; ".join(notes) or None, commit_sha,
        )
    except Exception as exc:
        return _result("failed", reason=_trim(str(exc)) or exc.__class__.__name__)
