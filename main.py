#!/usr/bin/env python3
"""Place the news-image-20261126 v4 entry image into the output directory.

The entry is a single front page for Thursday 26 November 2026: 40
verified stories across 9 regions, 13 drawn scenes, a world map, a UTC
timeline and a date check. The image itself (assets/entry.jpg) is drawn
by build-v4.py; this script only puts it where the grader looks for it,
as entry.png, verifying the copy byte-for-byte.

The output directory is /output unless MAKEFUN_OUTPUT_DIR is set.

Usage:
    python3 main.py
    MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import hashlib
import os
import shutil
from pathlib import Path

# The v4 front page: a 1024x1024 JPEG, 40 stories, 13 drawn scenes,
# world map, UTC timeline and date check — drawn in-session by build-v4.py.
ENTRY = Path(__file__).resolve().parent / "assets" / "entry.jpg"

CHUNK = 1 << 20  # 1 MiB read chunks for hashing


def file_sha256(path: Path) -> str:
    """SHA-256 hex digest of a file, read in 1 MiB chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_output_dir() -> Path:
    """Return the output directory: MAKEFUN_OUTPUT_DIR, else /output.

    A relative value is resolved against the current working directory,
    so the copy always lands in a well-defined place. A leading "~" is
    expanded to the user's home directory.
    """
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    out_dir = Path(raw).expanduser()
    if not out_dir.is_absolute():
        out_dir = (Path.cwd() / out_dir).resolve()
    return out_dir


def place_entry() -> Path:
    """Copy the entry image to the output directory as entry.png.

    Raises FileNotFoundError if the source image is missing, and
    RuntimeError if the copy does not hash identically to the source.
    """
    if not ENTRY.is_file():
        raise FileNotFoundError(f"source image missing: {ENTRY}")
    if ENTRY.stat().st_size == 0:
        raise RuntimeError(f"source image is empty: {ENTRY}")
    out_dir = resolve_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(ENTRY, target)
    if file_sha256(target) != file_sha256(ENTRY):
        raise RuntimeError(f"copy mismatch: {ENTRY} -> {target}")
    return target


def main() -> None:
    placed = place_entry()
    print(f"Wrote {placed} ({placed.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
