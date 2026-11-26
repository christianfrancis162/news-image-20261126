#!/usr/bin/env python3
"""News image entry for 26 November 2026 (Python 3.13, standard library only).

Copies the front-page image beside this file to /output/entry.png.
Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

OUT_DIR.mkdir(parents=True, exist_ok=True)
# A plain copy: byte-for-byte identical on every run, no network, no randomness.
shutil.copyfile(HERE / "assets" / "entry.jpg", OUT_DIR / "entry.png")
