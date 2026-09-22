#!/usr/bin/env python3
"""One-time, deterministic backfill of the pick-history ledger from git.

Only the explicitly accepted sessions below are ever imported: the five
automated full-universe daily runs (2026-09-14 .. 2026-09-18). Nothing is
inferred from commit messages. Excluded on purpose: the 2026-09-09 manual
100-stock test scan, the manual local commit c741acb0, the July test reports,
and every midday 100-stock sample commit.

Every accepted session is built and validated BEFORE any file is written, so a
bad entry can never leave a partial ledger. Re-running is byte-identical, and a
backfill never overwrites a live-recorded session unless --force is given.

Usage:
    python scripts/backfill_pick_history.py [--root data/pick_history] [--dry-run] [--force]
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.screening import pick_history  # noqa: E402

SHORTLIST_PATH = "data/daily_scans/shortlist_latest.json"
TOP20_PATH = "data/daily_scans/top20_latest.json"
CLT_GIT = "/Library/Developer/CommandLineTools/usr/bin/git"
BOT_AUTHOR = "github-actions[bot]"
MIN_FULL_UNIVERSE = 1000
MAX_TIMESTAMP_SKEW_SECONDS = 5

ACCEPTED_SESSIONS = (
    {"session_date": "2026-09-14", "commit": "25b3fc3f5904da286ff308d37767569a62aeb77e",
     "report": "data/daily_scans/optimized_scan_20260914_231020.txt"},
    {"session_date": "2026-09-15", "commit": "40b6d251c6a0f322cdd8077da24f6f04231bc2d0",
     "report": "data/daily_scans/optimized_scan_20260915_173119.txt"},
    {"session_date": "2026-09-16", "commit": "3b798ef7619ee78805c828cc95d0890935ed7c05",
     "report": "data/daily_scans/optimized_scan_20260916_172610.txt"},
    {"session_date": "2026-09-17", "commit": "9d9fe4eea7d9058f071feab97e1562f379976856",
     "report": "data/daily_scans/optimized_scan_20260917_173505.txt"},
    {"session_date": "2026-09-18", "commit": "919bf881d82366fe66f4493367296b52e19155e4",
     "report": "data/daily_scans/optimized_scan_20260918_170746.txt"},
)


class BackfillError(Exception):
    pass


def find_git():
    for candidate in (shutil.which("git"), CLT_GIT):
        if not candidate:
            continue
        try:
            subprocess.run([candidate, "--version"], capture_output=True, check=True, cwd=PROJECT_ROOT)
            return candidate
        except (OSError, subprocess.CalledProcessError):
            continue
    raise BackfillError("no working git binary found")


def make_git_runner(git_binary):
    def run_git(*args):
        proc = subprocess.run([git_binary, *args], capture_output=True, text=True, cwd=PROJECT_ROOT)
        if proc.returncode != 0:
            raise BackfillError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
        return proc.stdout
    return run_git


def _report_header(text, label):
    match = re.search(rf"^{label}:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _to_int(value):
    if value is None:
        return None
    digits = re.sub(r"[^\d]", "", value)
    return int(digits) if digits else None


def _parse_ts(value):
    return datetime.fromisoformat(value.replace(" ", "T")).replace(tzinfo=timezone.utc)


def collect_session(entry, run_git):
    """Build and validate one snapshot from git. Raises BackfillError on any doubt."""
    label = entry["session_date"]
    sha = entry["commit"]

    meta = run_git("show", "-s", "--format=%an", sha).strip()
    if meta != BOT_AUTHOR:
        raise BackfillError(f"{label}: commit {sha[:8]} author is {meta!r}, not the automated {BOT_AUTHOR!r}")

    shortlist_doc = json.loads(run_git("show", f"{sha}:{SHORTLIST_PATH}"))
    top20_doc = json.loads(run_git("show", f"{sha}:{TOP20_PATH}"))
    report_text = run_git("show", f"{sha}:{entry['report']}")

    total_universe = _to_int(_report_header(report_text, "Total Universe"))
    analyzed = _to_int(_report_header(report_text, "Analyzed"))
    report_generated = _report_header(report_text, "Generated")
    if total_universe is None or total_universe < MIN_FULL_UNIVERSE:
        raise BackfillError(f"{label}: report universe {total_universe!r} is not a full-universe scan")
    if not report_generated:
        raise BackfillError(f"{label}: report has no Generated header")

    for name, doc in (("shortlist", shortlist_doc), ("top20", top20_doc)):
        if doc.get("result") != "success":
            raise BackfillError(f"{label}: {name} result is {doc.get('result')!r}, expected 'success'")
        skew = abs((_parse_ts(doc["generated"]) - _parse_ts(report_generated)).total_seconds())
        if skew > MAX_TIMESTAMP_SKEW_SECONDS:
            raise BackfillError(f"{label}: {name} generated {doc['generated']} is {skew:.0f}s from report {report_generated}")

    session_date = pick_history.session_date_et(shortlist_doc["generated"])
    if session_date != label:
        raise BackfillError(f"{label}: timestamps resolve to ET session {session_date}")

    snapshot = pick_history.build_snapshot(
        session_date=session_date,
        generated_at=shortlist_doc["generated"],
        provenance="backfill",
        scope={"total_universe": total_universe, "analyzed": analyzed, "completed": True},
        shortlist=shortlist_doc["shortlist"],
        top20=top20_doc["top20"],
        source={"source_commit": sha, "report_path": entry["report"]},
    )
    pick_history.validate_snapshot(snapshot)
    return snapshot


def backfill(root, run_git, dry_run=False, force=False, sessions=ACCEPTED_SESSIONS):
    snapshots = [collect_session(entry, run_git) for entry in sessions]

    for snapshot in snapshots:
        path = pick_history.snapshot_path(snapshot["session_date"], snapshot["run_kind"], root)
        if path.exists() and not force:
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                existing = {}
            if existing.get("provenance") == "live":
                raise BackfillError(f"{snapshot['session_date']}: refusing to overwrite a live session (use --force)")

    written = []
    if not dry_run:
        for snapshot in snapshots:
            written.append(pick_history.write_snapshot(snapshot, root=root))
    return snapshots, written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", default=str(pick_history.DEFAULT_LEDGER_ROOT))
    parser.add_argument("--dry-run", action="store_true", help="validate everything, write nothing")
    parser.add_argument("--force", action="store_true", help="allow overwriting live-recorded sessions")
    args = parser.parse_args(argv)

    try:
        snapshots, written = backfill(Path(args.root), make_git_runner(find_git()),
                                      dry_run=args.dry_run, force=args.force)
    except BackfillError as exc:
        print(f"backfill aborted, nothing written: {exc}", file=sys.stderr)
        return 1

    verb = "validated" if args.dry_run else "wrote"
    for snapshot in snapshots:
        sl = [r["ticker"] for r in snapshot["lists"]["shortlist"]]
        print(f"{snapshot['session_date']}  universe={snapshot['scope']['total_universe']:>5}  "
              f"shortlist={','.join(sl)}  top20={len(snapshot['lists']['top20'])}")
    print(f"{verb} {len(snapshots)} sessions" + ("" if args.dry_run else f" under {args.root}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
