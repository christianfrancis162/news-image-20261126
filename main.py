#!/usr/bin/env python3
"""Entrypoint for the news-image-20261126 v3 entry.

Thursday 26 November 2026, 36 stories across 9 regions.

The entry is a single front-page image. This script places that image
(assets/entry.jpg, drawn by build-v3.py) into the output directory as
entry.png so the grader can find it. The output directory is /output
unless MAKEFUN_OUTPUT_DIR is set.

Usage:
    python3 main.py
    MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import hashlib
import os
import shutil
from pathlib import Path

ENTRY = Path(__file__).resolve().parent / "assets" / "entry.jpg"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def place_entry() -> Path:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(ENTRY, target)
    if sha256(target) != sha256(ENTRY):
        raise RuntimeError(f"copy mismatch: {ENTRY} -> {target}")
    return target


def main() -> None:
    placed = place_entry()
    print(f"Wrote {placed} ({placed.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
