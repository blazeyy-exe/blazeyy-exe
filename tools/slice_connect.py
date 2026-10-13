"""Regenerate the complete, non-clickable connect banner image.

Run from the repo root after editing source/connect.svg:
    python tools/slice_connect.py
"""
from pathlib import Path
import re

root = Path(__file__).resolve().parent.parent
source = (root / "source" / "connect.svg").read_text(encoding="utf-8")
source, count = re.subn(r"<a\b[^>]*>.*?</a>", "", source, flags=re.DOTALL)
assert count == 4, f"expected 4 invisible SVG link overlays, found {count}"
(root / "assets" / "connect-banner.svg").write_text(source, encoding="utf-8")
print("wrote assets/connect-banner.svg")
