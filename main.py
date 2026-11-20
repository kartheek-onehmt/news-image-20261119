"""news-image-20261119 entry: copies entry.png (drawn by tools/make_image.py) to the output directory.

Standard library only. Outside the grader, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import shutil
from pathlib import Path

src = Path(__file__).resolve().parent / "entry.png"
dst = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")) / "entry.png"
shutil.copyfile(src, dst)
