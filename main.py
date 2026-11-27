#!/usr/bin/env python3
"""News image entry for Thursday 26 November 2026.

Copies the front-page image stored beside this script
(assets/entry.jpg) into the output directory as entry.png,
byte-for-byte. The output directory defaults to /output and
can be overridden with the MAKEFUN_OUTPUT_DIR environment
variable, for example::

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
from pathlib import Path


def main() -> None:
    here = Path(__file__).resolve().parent
    source = here / "assets" / "entry.jpg"
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    destination = out_dir / "entry.png"
    shutil.copyfile(source, destination)
    if destination.stat().st_size != source.stat().st_size:
        raise RuntimeError(
            f"copy size mismatch: {source} -> {destination}"
        )
    print(f"Wrote {destination} ({destination.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
