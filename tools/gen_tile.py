#!/usr/bin/env python3
"""
Generate a genuinely seamless Kurdish/Islamic-inspired geometric tile.

Seamlessness strategy ("torus wrap"):
  All motif geometry is authored once inside a <defs> group, then stamped
  nine times at offsets (-S,0,+S) x (-S,0,+S). The outer <svg> viewport
  clips to 0..S in both axes (SVG default overflow:hidden), so anything
  that runs off one edge is guaranteed to reappear, pixel-identical, on
  the opposite edge. This makes the tile seamless by construction rather
  than by eyeballing a crop.
"""
import math

import sys

S = 120.0          # unit cell side
# Two ink sets: dark linework for the bone ground, light linework for the
# oxblood and teal blocks. Same geometry, so the pattern reads as one
# material across both values.
PALETTES = {
    "dark":  {"ink": "#83967D", "ink2": "#1C5A5F", "out": "assets/pattern-tile.svg"},
    "light": {"ink": "#C1B0AE", "ink2": "#F4F5F0", "out": "assets/pattern-tile-light.svg"},
}
INK = PALETTES["dark"]["ink"]
INK2 = PALETTES["dark"]["ink2"]


def star_points(cx, cy, R, n=8, m=3, phase=0.0):
    """Vertices of an {n/m} star polygon drawn as a simple 2n-gon."""
    r = R * math.cos(m * math.pi / n) / math.cos((m - 1) * math.pi / n)
    pts = []
    for k in range(2 * n):
        rad = R if k % 2 == 0 else r
        a = phase + k * math.pi / n
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return pts


def poly(pts, close=True):
    d = "M " + " L ".join(f"{x:.3f} {y:.3f}" for x, y in pts)
    return d + " Z" if close else d


def rot_square(cx, cy, r):
    """Square standing on a corner (diamond)."""
    return [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]


def rosette(cx, cy, off, lobe):
    """Four-lobed quatrefoil of overlapping circles — echoes the artwork."""
    d = []
    for i in range(4):
        a = i * math.pi / 2
        lx, ly = cx + off * math.cos(a), cy + off * math.sin(a)
        d.append(
            f"M {lx - lobe:.3f} {ly:.3f} "
            f"A {lobe:.3f} {lobe:.3f} 0 1 1 {lx + lobe:.3f} {ly:.3f} "
            f"A {lobe:.3f} {lobe:.3f} 0 1 1 {lx - lobe:.3f} {ly:.3f} Z"
        )
    return " ".join(d)


def build():
    h = S / 2.0        # lattice pitch: 60
    R = 21.0           # star outer radius
    parts = []

    # Lattice nodes on a 60-grid, checkerboarded:
    #   i+j even -> eight-point star   (0,0) (60,60) (120,0) ...
    #   i+j odd  -> quatrefoil rosette (60,0) (0,60) ...
    # Diamonds sit at every square centre (30,30) (90,30) (30,90) (90,90),
    # and the 45-degree strapwork runs node-to-node straight through them.

    stars, rosettes = [], []
    for i in range(3):
        for j in range(3):
            (stars if (i + j) % 2 == 0 else rosettes).append((i * h, j * h))

    # --- strapwork first, so the motifs sit on top of it ---
    gap_star, gap_rose = R * 0.60, 17.0
    seen = set()
    for i in range(2):
        for j in range(2):
            cx, cy = (i + 0.5) * h, (j + 0.5) * h
            for dx, dy in ((1, 1), (1, -1)):
                ax, ay = cx - dx * h / 2, cy - dy * h / 2
                bx, by = cx + dx * h / 2, cy + dy * h / 2
                key = (round(ax, 2), round(ay, 2), round(bx, 2), round(by, 2))
                if key in seen:
                    continue
                seen.add(key)
                ga = gap_star if (round(ax / h) + round(ay / h)) % 2 == 0 else gap_rose
                gb = gap_star if (round(bx / h) + round(by / h)) % 2 == 0 else gap_rose
                ux, uy = dx / math.sqrt(2), dy / math.sqrt(2)
                x1, y1 = ax + ux * ga, ay + uy * ga
                x2, y2 = bx - ux * gb, by - uy * gb
                parts.append(
                    f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
                    f'stroke="{INK}" stroke-width="0.9" stroke-linecap="round"/>'
                )

    # --- diamonds at the strapwork crossings ---
    for i in range(2):
        for j in range(2):
            cx, cy = (i + 0.5) * h, (j + 0.5) * h
            parts.append(
                f'<path d="{poly(rot_square(cx, cy, 5.2))}" fill="none" '
                f'stroke="{INK}" stroke-width="1.0" stroke-linejoin="miter"/>'
            )

    # --- eight-point stars ---
    for cx, cy in stars:
        parts.append(
            f'<path d="{poly(star_points(cx, cy, R, phase=math.pi/8))}" '
            f'fill="none" stroke="{INK2}" stroke-width="1.6" '
            f'stroke-linejoin="round"/>'
        )
        pts = [
            (cx + R * 0.42 * math.cos(math.pi / 8 + k * math.pi / 4),
             cy + R * 0.42 * math.sin(math.pi / 8 + k * math.pi / 4))
            for k in range(8)
        ]
        parts.append(
            f'<path d="{poly(pts)}" fill="none" stroke="{INK2}" '
            f'stroke-width="1.0" stroke-linejoin="round"/>'
        )

    # --- quatrefoil rosettes ---
    for cx, cy in rosettes:
        parts.append(
            f'<path d="{rosette(cx, cy, 9.0, 7.6)}" fill="none" '
            f'stroke="{INK}" stroke-width="1.3"/>'
        )
        parts.append(
            f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="2.6" fill="none" '
            f'stroke="{INK}" stroke-width="1.0"/>'
        )

    motif = "\n    ".join(parts)

    # Torus wrap: stamp the motif at all nine neighbouring offsets so that
    # anything leaving one edge re-enters, identically, on the opposite one.
    uses = "\n  ".join(
        f'<use href="#m" x="{i * S:g}" y="{j * S:g}"/>'
        for i in (-1, 0, 1) for j in (-1, 0, 1)
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{S:g}" height="{S:g}" viewBox="0 0 {S:g} {S:g}">
  <title>Seamless geometric tile</title>
  <defs>
    <g id="m">
    {motif}
    </g>
  </defs>
  {uses}
</svg>
'''


if __name__ == "__main__":
    for name, pal in PALETTES.items():
        INK, INK2 = pal["ink"], pal["ink2"]
        globals()["INK"], globals()["INK2"] = INK, INK2
        open(pal["out"], "w").write(build())
        print("wrote", pal["out"])
