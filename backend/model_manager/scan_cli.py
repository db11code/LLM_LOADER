"""
Simple CLI entry-point for model-manager utilities.

Usage
-----
python -m backend.model_manager.scan_cli scan-cache \
    [--cache-root PATH] \
    [--output FILE]

Notes
-----
* Only std-lib: argparse, json, pathlib, sys.
* Exits with code 0 on success, 1 on any exception.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from backend.model_manager.discovery import (
    build_index,
    get_hf_cache_path,
)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="llm-scan",
        description="Local LLM cache utilities",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # scan-cache -------------------------------------------------------------
    scan = sub.add_parser(
        "scan-cache",
        help="Scan HF cache and emit index.json",
    )
    scan.add_argument(
        "--cache-root",
        type=Path,
        default=None,
        help="Override Hugging Face cache root",
    )
    scan.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path for index.json (defaults to <cache-root>/index.json)",
    )

    return parser.parse_args(argv)


# ──────────────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv or sys.argv[1:])

    if args.cmd == "scan-cache":
        cache_root: Path | None = args.cache_root or None
        cache_root = cache_root or get_hf_cache_path()

        try:
            records = build_index(cache_root, args.output)
            print(json.dumps(records, indent=2))
            sys.exit(0)
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"[scan-cache] error: {exc}\n")
            sys.exit(1)


if __name__ == "__main__":
    main() 