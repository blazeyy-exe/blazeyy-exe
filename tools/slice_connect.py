"""Regenerate the sliced connect banner and its button-only link targets.

Run from the repo root after editing source/connect.svg:
    python tools/slice_connect.py
"""
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent.parent
source = (root / "source" / "connect.svg").read_text(encoding="utf-8")
source = re.sub(r"</?a\b[^>]*>", "", source)

width = 1200
header_height = 148
card_height = 107
total_height = 640
cards = ["linkedin", "portfolio", "instagram", "email"]
segments = [("left", 0, 507), ("button", 507, 647), ("edge", 1154, 46)]


def cut(name, x, y, slice_width, slice_height):
    pattern = r'(<svg\b[^>]*?\bwidth=")\d+(" height=")\d+(" viewBox=")[^"]+(")'
    replacement = (
        rf"\g<1>{slice_width}\g<2>{slice_height}"
        rf"\g<3>{x} {y} {slice_width} {slice_height}\g<4>"
    )
    output, count = re.subn(pattern, replacement, source, count=1)
    assert count == 1, "unexpected root <svg> attributes"
    (root / "assets" / f"connect-{name}.svg").write_text(output, encoding="utf-8")


cut("header", 0, 0, width, header_height)
for index, name in enumerate(cards):
    y = header_height + card_height * index
    cut(name, 0, y, width, card_height)
    for segment, x, segment_width in segments:
        cut(f"{name}-{segment}", x, y, segment_width, card_height)

footer_y = header_height + card_height * len(cards)
cut("footer", 0, footer_y, width, total_height - footer_y)
print("wrote connect banner slices to assets/")
