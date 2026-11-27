#!/usr/bin/env python3
"""Entrypoint for the news-image-20261126 v4 entry.

Thursday 26 November 2026, 40 stories across 9 regions, 13 drawn scenes.

The entry is a single front-page image. This script places that image
(assets/entry.jpg, drawn by build-v4.py) into the output directory as
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

# v4 asset: 1024x1024 JPEG, 40 stories, 13 drawn scenes, world map,
# UTC timeline and date check — drawn in-session by build-v4.py.
ENTRY = Path(__file__).resolve().parent / "assets" / "entry.jpg"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_output_dir() -> Path:
    """Return the output directory: MAKEFUN_OUTPUT_DIR, else /output.

    A relative value is resolved against the current working directory
    so the copy always lands in a well-defined place.
    """
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    out_dir = Path(raw).expanduser()
    if not out_dir.is_absolute():
        out_dir = (Path.cwd() / out_dir).resolve()
    return out_dir


def place_entry() -> Path:
    if not ENTRY.is_file():
        raise FileNotFoundError(f"source image missing: {ENTRY}")
    out_dir = resolve_output_dir()
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
