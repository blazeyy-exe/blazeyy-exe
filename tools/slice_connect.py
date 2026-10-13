"""Regenerates the clickable connect banner from source/connect.svg.

GitHub does not allow links inside SVG images, so the banner is cut into
horizontal slices. Each card slice is wrapped in a normal <a> link in README.md,
which makes the cards real, clickable buttons while looking identical to the
original single banner.

Run from the repo root after editing source/connect.svg (text, photo, etc.):
    python tools/slice_connect.py
"""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
src = (root / "source" / "connect.svg").read_text(encoding="utf-8")
src = re.sub(r"</?a\b[^>]*>", "", src)          # links live in README.md, not inside the SVG
H, C, W, TOTAL = 148, 107, 1200, 640            # header height, card pitch, width, total height
cards = ["linkedin", "github", "instagram", "esahara"]

def cut(name, y, h):
    out, n = re.subn(r'width="1200" height="640" viewBox="0 0 1200 640"',
                     f'width="{W}" height="{h}" viewBox="0 {y} {W} {h}"', src, count=1)
    assert n == 1, "unexpected root <svg> attributes"
    (root / "assets" / f"connect-{name}.svg").write_text(out, encoding="utf-8")

cut("header", 0, H)
for i, n in enumerate(cards):
    cut(n, H + C * i, C)
cut("footer", H + C * len(cards), TOTAL - (H + C * len(cards)))
print("wrote 6 slices to assets/")
