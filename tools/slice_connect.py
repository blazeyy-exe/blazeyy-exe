"""Regenerates the clickable connect banner from source/connect.svg.

GitHub does not allow links inside SVG images, so the banner is cut into
horizontal slices. Each card slice is wrapped in a normal <a> link in README.md,
which makes the cards real, clickable buttons while looking identical to the
original single banner.

Run from the repo root after editing source/connect.svg (text, photo, cards, etc.):
    python tools/slice_connect.py

What it does differently from a fixed-offset cut
------------------------------------------------
* Card positions are READ from the artwork (the <a><rect .../> blocks), so moving
  or resizing a card in the source can never leave the slices out of sync.
* Every cut ("seam") is placed in empty space, never through a card. The old cut
  sat exactly on each card's top edge, splitting its 1px border across two
  images, which is what made the joins visible.
* Seams between cards go in the middle of the gutter, so each card's clickable
  slice has equal padding above and below it.
* The result is validated (slices tile the banner exactly, no seam touches a
  card) and the matching README markup is printed at the end.
"""
import math, pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
raw = (root / "source" / "connect.svg").read_text(encoding="utf-8")

# Names of the card slices, top to bottom (must match the <a> cards in the SVG).
CARDS = ["linkedin", "github", "instagram", "esahara"]
# Seam above the first card / below the last one, measured from the card edge.
# Chosen to fall on empty rows: above card 1 it sits between the "LET'S" and
# "CONNECT." lines of the heading; below the last card it sits above the footer text.
HEADER_PAD = 16     # seam = first card top - 16
FOOTER_PAD = 12     # seam = last card bottom + 12

# ---- read the geometry from the artwork -------------------------------------
root_attrs = re.search(r'width="(\d+)" height="(\d+)" viewBox="0 0 \1 \2"', raw)
assert root_attrs, "unexpected root <svg> attributes"
W, TOTAL = int(root_attrs.group(1)), int(root_attrs.group(2))

link_cards = re.findall(
    r'<a\b[^>]*href="([^"]*)"[^>]*>\s*<rect x="[\d.]+" y="([\d.]+)" width="[\d.]+" height="([\d.]+)"', raw)
assert len(link_cards) == len(CARDS), (
    f"found {len(link_cards)} linked cards in the SVG but {len(CARDS)} names in CARDS")
hrefs = [c[0] for c in link_cards]
tops = [float(c[1]) for c in link_cards]
bottoms = [float(c[1]) + float(c[2]) for c in link_cards]

# ---- work out the seams ------------------------------------------------------
seams = [math.floor(tops[0] - HEADER_PAD)]
seams += [math.floor((bottoms[i] + tops[i + 1]) / 2) for i in range(len(CARDS) - 1)]
seams += [math.ceil(bottoms[-1] + FOOTER_PAD)]
bounds = [0] + seams + [TOTAL]
names = ["header"] + CARDS + ["footer"]

# ---- sanity checks -----------------------------------------------------------
assert all(a < b for a, b in zip(bounds, bounds[1:])), "slices must be non-empty and in order"
for s in seams:
    for t, b in zip(tops, bottoms):
        assert not (t - 1 <= s <= b + 1), f"seam at y={s} touches a card ({t}-{b})"

# ---- cut ---------------------------------------------------------------------
src = re.sub(r"</?a\b[^>]*>", "", raw)          # links live in README.md, not inside the SVG
out_dir = root / "assets"
out_dir.mkdir(exist_ok=True)

def cut(name, y0, y1):
    h = y1 - y0
    out, n = re.subn(rf'width="{W}" height="{TOTAL}" viewBox="0 0 {W} {TOTAL}"',
                     f'width="{W}" height="{h}" viewBox="0 {y0} {W} {h}"', src, count=1)
    assert n == 1, "unexpected root <svg> attributes"
    (out_dir / f"connect-{name}.svg").write_text(out, encoding="utf-8")
    return h

heights = [cut(n, y0, y1) for n, y0, y1 in zip(names, bounds, bounds[1:])]
assert sum(heights) == TOTAL

print(f"wrote {len(names)} slices to assets/")
for n, y0, y1 in zip(names, bounds, bounds[1:]):
    print(f"  connect-{n}.svg  y {y0:>3} -> {y1:<3} (h={y1 - y0})")

# ---- README markup -----------------------------------------------------------
# align="top" matters: inline images normally sit on the text baseline, which
# leaves a gap under each image. Top alignment removes it, so the slices touch.
alts = {"linkedin": "LinkedIn", "github": "GitHub", "instagram": "Instagram", "esahara": "eSahara"}
lines = ['<img align="top" src="assets/connect-header.svg" width="100%" alt="Let\'s connect. Build something that matters.">']
for n, href in zip(CARDS, hrefs):
    lines.append(f'<a href="{href}"><img align="top" src="assets/connect-{n}.svg" width="100%" alt="{alts[n]}"></a>')
lines.append('<img align="top" src="assets/connect-footer.svg" width="100%" alt="Good people. Good ideas. Let\'s talk.">')
print("\nREADME.md markup (keep these lines together, no blank lines between them):\n")
print("<p>\n" + "\n".join(lines) + "\n</p>")