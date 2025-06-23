"""
Discover locally-cached Hugging Face model repositories.

A repo lives under:
    <cache_root>/models--{namespace}--{repo_name}/snapshots/<hash>/...
Only the *top-level* repo directory (models--namespace--repo_name) is scanned;
individual snapshot hashes are ignored.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import os
import json
from typing import List, Dict

from .cache_path import get_hf_cache_path


def _folder_size_bytes(path: Path) -> int:
    """Sum size of all files under *path* (recursive)."""
    total = 0
    for root, _, files in os.walk(path):
        for fname in files:
            try:
                total += (Path(root) / fname).stat().st_size
            except OSError:
                # File might disappear during walk; skip quietly.
                continue
    return total


def _parse_repo_id(folder_name: str) -> str | None:
    """
    Convert 'models--<namespace>--<repo_name>' → '<namespace>/<repo_name>'.
    Returns None if pattern doesn't match.
    """
    if not folder_name.startswith("models--"):
        return None
    try:
        _, namespace, repo_name = folder_name.split("--", 2)
        return f"{namespace}/{repo_name}"
    except ValueError:
        return None


def scan_cache(cache_root: Path | None = None) -> List[Dict]:
    """
    Walk the Hugging Face cache and return metadata records.

    Parameters
    ----------
    cache_root : Path | None
        Root cache directory; defaults to get_hf_cache_path().

    Returns
    -------
    List[Dict]
        Each dict = {repo_id, path, size_mb, last_access} sorted by last_access (desc).
    """
    root = cache_root or get_hf_cache_path()
    if not root.exists():
        return []

    records: list[dict] = []
    for repo_dir in root.glob("models--*"):
        if not repo_dir.is_dir():
            continue

        repo_id = _parse_repo_id(repo_dir.name)
        if repo_id is None:
            continue

        size_mb = round(_folder_size_bytes(repo_dir) / 1_048_576, 2)
        last_access_ts = repo_dir.stat().st_atime  # POSIX atime; Windows fine too
        last_access_iso = (
            datetime.fromtimestamp(last_access_ts, tz=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

        records.append(
            {
                "repo_id": repo_id,
                "path": repo_dir.as_posix(),
                "size_mb": size_mb,
                "last_access": last_access_iso,
            }
        )

    # Newest first
    return sorted(records, key=lambda r: r["last_access"], reverse=True)


def build_index(
    cache_root: Path | None = None,
    output_file: Path | None = None,
) -> List[Dict]:
    """
    Scan the Hugging Face cache, write a pretty-printed JSON index, and
    return the records.

    Parameters
    ----------
    cache_root : Path | None
        Root cache directory. Defaults to get_hf_cache_path().
    output_file : Path | None
        Where to write JSON. Defaults to <cache_root>/index.json.

    Returns
    -------
    list[dict]
        Same list returned by scan_cache(), for immediate use/printing.
    """
    root = cache_root or get_hf_cache_path()
    records = scan_cache(root)

    # Resolve output file path
    out_path = output_file or (root / "index.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    return records 