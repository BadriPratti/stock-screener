"""Capture and replay immutable price inputs for backtest experiments."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


SCHEMA_VERSION = 1
DEFAULT_STORE = Path(__file__).resolve().parents[2] / "data" / "backtest_manifests"
_REQUIRED_PARAMETERS = {
    "universe_size",
    "lookback_months",
    "step_days",
    "top_n",
    "max_hold_days",
    "investment_per_trade",
    "seed",
    "audit_fundamentals",
    "audit_sample_size",
}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ManifestError(ValueError):
    """Raised when a frozen-input manifest is missing, invalid, or corrupt."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_commit(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, check=True,
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _manifest_location(reference: str | Path, store_root: Path, *, capture: bool) -> tuple[Path, str]:
    text = str(reference)
    if capture and text == "auto":
        manifest_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:12]
        directory = store_root / manifest_id
        return directory / "manifest.json", manifest_id

    candidate = Path(text)
    is_path = candidate.is_absolute() or len(candidate.parts) > 1 or candidate.suffix == ".json"
    if is_path:
        manifest_path = candidate if candidate.suffix == ".json" else candidate / "manifest.json"
        manifest_id = manifest_path.parent.name
    else:
        manifest_id = text
        manifest_path = store_root / manifest_id / "manifest.json"
    if not manifest_id or manifest_id in {".", ".."}:
        raise ManifestError("Manifest id must be a non-empty directory name")
    return manifest_path, manifest_id


def _write_frame(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=True, index_label="Date", date_format="%Y-%m-%dT%H:%M:%S.%f", float_format="%.17g")


def _read_frame(path: Path) -> pd.DataFrame:
    try:
        frame = pd.read_csv(path, index_col="Date", parse_dates=["Date"])
    except Exception as exc:
        raise ManifestError(f"Could not read frozen price history {path}: {exc}") from exc
    frame.index.name = None
    return frame


def _file_record(path: Path, manifest_dir: Path, rows: int) -> dict[str, Any]:
    return {
        "path": path.relative_to(manifest_dir).as_posix(),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "rows": rows,
    }


def validate_manifest(manifest: Any) -> None:
    if not isinstance(manifest, dict):
        raise ManifestError("Manifest root must be a JSON object")
    required = {
        "schema_version", "manifest_id", "created_at", "git_commit", "universe",
        "random_seed", "parameters", "date_grid", "data_settings", "files",
        "price_histories",
    }
    missing = sorted(required - manifest.keys())
    if missing:
        raise ManifestError(f"Manifest is missing required fields: {', '.join(missing)}")
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise ManifestError(
            f"Unsupported manifest schema_version {manifest['schema_version']!r}; expected {SCHEMA_VERSION}"
        )
    if not isinstance(manifest["manifest_id"], str) or not manifest["manifest_id"]:
        raise ManifestError("manifest_id must be a non-empty string")
    try:
        datetime.fromisoformat(manifest["created_at"].replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise ManifestError("created_at must be an ISO-8601 timestamp") from exc
    if manifest["git_commit"] is not None and not re.fullmatch(r"[0-9a-f]{40}", manifest["git_commit"]):
        raise ManifestError("git_commit must be a 40-character lowercase hash or null")
    universe = manifest["universe"]
    if not isinstance(universe, list) or any(not isinstance(ticker, str) or not ticker for ticker in universe):
        raise ManifestError("universe must be a list of non-empty ticker strings")
    if len(universe) != len(set(universe)):
        raise ManifestError("universe contains duplicate tickers")
    if not isinstance(manifest["parameters"], dict):
        raise ManifestError("parameters must be an object")
    missing_params = sorted(_REQUIRED_PARAMETERS - manifest["parameters"].keys())
    if missing_params:
        raise ManifestError(f"Manifest parameters are missing: {', '.join(missing_params)}")
    integer_params = ("universe_size", "lookback_months", "step_days", "top_n", "max_hold_days", "audit_sample_size")
    if any(not isinstance(manifest["parameters"][name], int) for name in integer_params):
        raise ManifestError("Count and duration parameters must be integers")
    if any(manifest["parameters"][name] <= 0 for name in integer_params):
        raise ManifestError("Count and duration parameters must be positive")
    if not isinstance(manifest["parameters"]["investment_per_trade"], (int, float)):
        raise ManifestError("investment_per_trade must be numeric")
    if manifest["parameters"]["seed"] is not None and not isinstance(manifest["parameters"]["seed"], int):
        raise ManifestError("seed must be an integer or null")
    if not isinstance(manifest["parameters"]["audit_fundamentals"], bool):
        raise ManifestError("audit_fundamentals must be boolean")
    if manifest["random_seed"] != manifest["parameters"]["seed"]:
        raise ManifestError("random_seed does not match parameters.seed")
    if not isinstance(manifest["date_grid"], list) or not manifest["date_grid"] or any(
        not isinstance(value, str) for value in manifest["date_grid"]
    ):
        raise ManifestError("date_grid must be a non-empty list of ISO date strings")
    try:
        for value in manifest["date_grid"]:
            datetime.fromisoformat(value)
    except ValueError as exc:
        raise ManifestError("date_grid contains an invalid date") from exc
    if not isinstance(manifest["files"], dict) or "spy" not in manifest["files"]:
        raise ManifestError("files must contain a SPY file record")
    histories = manifest["price_histories"]
    if not isinstance(histories, dict) or set(histories) != set(universe):
        raise ManifestError("price_histories must contain exactly one record per universe ticker")
    for ticker, record in histories.items():
        if not isinstance(record, dict) or record.get("status") not in {"stored", "fetch_error"}:
            raise ManifestError(f"Invalid price-history status for {ticker}")
        if record["status"] == "fetch_error" and not isinstance(record.get("error"), str):
            raise ManifestError(f"Fetch error for {ticker} must include an error string")
        if record["status"] == "stored" and not isinstance(record.get("usable"), bool):
            raise ManifestError(f"Stored history for {ticker} must declare whether it was usable")

    records = [manifest["files"]["spy"]]
    records.extend(record for record in histories.values() if record.get("status") == "stored")
    for record in records:
        if not isinstance(record, dict):
            raise ManifestError("Every frozen file record must be an object")
        if not isinstance(record.get("path"), str) or Path(record["path"]).is_absolute() or ".." in Path(record["path"]).parts:
            raise ManifestError("Frozen file paths must be relative and may not traverse directories")
        if not _SHA256_RE.fullmatch(str(record.get("sha256", ""))):
            raise ManifestError(f"Invalid SHA-256 for frozen file {record.get('path')!r}")
        if not isinstance(record.get("bytes"), int) or record["bytes"] < 0:
            raise ManifestError(f"Invalid byte count for frozen file {record.get('path')!r}")
        if not isinstance(record.get("rows"), int) or record["rows"] < 0:
            raise ManifestError(f"Invalid row count for frozen file {record.get('path')!r}")


def capture_manifest(
    reference: str | Path,
    *,
    universe: list[str],
    spy: pd.DataFrame,
    histories: dict[str, pd.DataFrame],
    usable_tickers: set[str],
    fetch_errors: dict[str, str],
    parameters: dict[str, Any],
    date_grid: list[str],
    repo_root: Path,
    store_root: Path = DEFAULT_STORE,
) -> tuple[dict[str, Any], Path]:
    manifest_path, manifest_id = _manifest_location(reference, store_root, capture=True)
    manifest_dir = manifest_path.parent
    if manifest_path.exists() or manifest_dir.exists() and any(manifest_dir.iterdir()):
        raise ManifestError(f"Refusing to overwrite existing manifest directory: {manifest_dir}")
    manifest_dir.mkdir(parents=True, exist_ok=True)

    spy_path = manifest_dir / "spy.csv"
    _write_frame(spy, spy_path)
    price_records: dict[str, dict[str, Any]] = {}
    for index, ticker in enumerate(universe):
        if ticker in histories:
            history_path = manifest_dir / "histories" / f"{index:05d}.csv"
            _write_frame(histories[ticker], history_path)
            price_records[ticker] = {
                "status": "stored", "usable": ticker in usable_tickers,
                **_file_record(history_path, manifest_dir, len(histories[ticker])),
            }
        else:
            price_records[ticker] = {"status": "fetch_error", "error": fetch_errors.get(ticker, "no usable history")}

    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": manifest_id,
        "created_at": created_at,
        "git_commit": _git_commit(repo_root),
        "universe": universe,
        "random_seed": parameters["seed"],
        "parameters": parameters,
        "date_grid": date_grid,
        "data_settings": {
            "provider": "yfinance",
            "provider_version": importlib.metadata.version("yfinance"),
            "history_arguments": {"period": "2y", "auto_adjust": True, "actions": True},
            "format": "csv",
            "float_format": "%.17g",
        },
        "files": {"spy": _file_record(spy_path, manifest_dir, len(spy))},
        "price_histories": price_records,
    }
    validate_manifest(manifest)
    with manifest_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return manifest, manifest_path


def load_manifest(
    reference: str | Path, *, store_root: Path = DEFAULT_STORE
) -> tuple[dict[str, Any], pd.DataFrame, dict[str, pd.DataFrame], Path]:
    manifest_path, requested_id = _manifest_location(reference, store_root, capture=False)
    if not manifest_path.is_file():
        raise ManifestError(f"Manifest file does not exist: {manifest_path}")
    try:
        with manifest_path.open(encoding="utf-8") as handle:
            manifest = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"Could not read manifest {manifest_path}: {exc}") from exc
    validate_manifest(manifest)
    if Path(str(reference)).suffix != ".json" and manifest["manifest_id"] != requested_id:
        raise ManifestError(
            f"Manifest id mismatch: requested {requested_id!r}, file declares {manifest['manifest_id']!r}"
        )

    manifest_dir = manifest_path.parent.resolve()

    def checked_path(record: dict[str, Any]) -> Path:
        path = (manifest_dir / record["path"]).resolve()
        if path.parent != manifest_dir and manifest_dir not in path.parents:
            raise ManifestError(f"Frozen file escapes manifest directory: {record['path']}")
        if not path.is_file():
            raise ManifestError(f"Frozen file does not exist: {path}")
        actual_size = path.stat().st_size
        if actual_size != record["bytes"]:
            raise ManifestError(
                f"Frozen file size mismatch for {record['path']}: expected {record['bytes']}, got {actual_size}"
            )
        actual_hash = sha256_file(path)
        if actual_hash != record["sha256"]:
            raise ManifestError(
                f"Frozen file hash mismatch for {record['path']}: expected {record['sha256']}, got {actual_hash}"
            )
        return path

    spy_record = manifest["files"]["spy"]
    spy = _read_frame(checked_path(spy_record))
    if len(spy) != spy_record["rows"]:
        raise ManifestError("Frozen SPY row count does not match its manifest record")
    histories: dict[str, pd.DataFrame] = {}
    for ticker in manifest["universe"]:
        record = manifest["price_histories"][ticker]
        if record["status"] != "stored":
            continue
        history = _read_frame(checked_path(record))
        if len(history) != record["rows"]:
            raise ManifestError(f"Frozen row count does not match for {ticker}")
        if record.get("usable", True):
            histories[ticker] = history
    return manifest, spy, histories, manifest_path
