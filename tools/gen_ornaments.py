#!/usr/bin/env python3
"""Purpose-built ornaments drawn at their own viewBox, so they scale
responsively instead of being cropped out of a 1440x810 mood board."""
import math

SAGE = "#83967D"
TEAL = "#1C5A5F"
PLUM = "#4A0F14"

# Light-on-dark counterparts, for ornaments sitting on the oxblood and
# teal blocks. Geometry is identical; only the inks change.
CREAM = "#F4F5F0"
ROSE = "#C1B0AE"


def star(cx, cy, R, stroke, sw, n=8, m=3):
    r = R * math.cos(m * math.pi / n) / math.cos((m - 1) * math.pi / n)
    pts = []
    for k in range(2 * n):
        rad = R if k % 2 == 0 else r
        a = math.pi / n + k * math.pi / n
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    d = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z"
    return (f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linejoin="round"/>')


def quatrefoil(cx, cy, off, lobe, stroke, sw):
    out = []
    for i in range(4):
        a = i * math.pi / 2
        lx, ly = cx + off * math.cos(a), cy + off * math.sin(a)
        out.append(f'<circle cx="{lx:.2f}" cy="{ly:.2f}" r="{lobe:.2f}" '
                   f'fill="none" stroke="{stroke}" stroke-width="{sw}"/>')
    return "".join(out)


def diamond(cx, cy, r, stroke, sw, fill="none"):
    return (f'<path d="M {cx:.2f} {cy-r:.2f} L {cx+r:.2f} {cy:.2f} '
            f'L {cx:.2f} {cy+r:.2f} L {cx-r:.2f} {cy:.2f} Z" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="miter"/>')


def divider(a=SAGE, b=TEAL):
    W, H = 640.0, 56.0
    cy = H / 2
    cx = W / 2
    p = [f'<rect width="{W:g}" height="{H:g}" fill="none"/>']
    # rules running out to both edges, stopping clear of the ornament cluster
    inner = 138.0
    for x1, x2 in [(0, cx - inner), (cx + inner, W)]:
        p.append(f'<line x1="{x1:.2f}" y1="{cy}" x2="{x2:.2f}" y2="{cy}" '
                 f'stroke="{a}" stroke-width="1"/>')
    # centre star
    p.append(star(cx, cy, 17, b, 1.6))
    p.append(f'<circle cx="{cx}" cy="{cy}" r="4.6" fill="none" '
             f'stroke="{b}" stroke-width="1.1"/>')
    # flanking quatrefoils and diamonds
    for s in (-1, 1):
        p.append(quatrefoil(cx + s * 68, cy, 7.5, 6.6, a, 1.2))
        p.append(diamond(cx + s * 116, cy, 6.2, a, 1.1))
        p.append(f'<line x1="{cx + s*26:.2f}" y1="{cy}" '
                 f'x2="{cx + s*52:.2f}" y2="{cy}" stroke="{a}" '
                 f'stroke-width="1"/>')
        p.append(f'<line x1="{cx + s*84:.2f}" y1="{cy}" '
                 f'x2="{cx + s*108:.2f}" y2="{cy}" stroke="{a}" '
                 f'stroke-width="1"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}" '
            f'width="{W:g}" height="{H:g}"><title>Ornamental divider</title>'
            + "".join(p) + "</svg>\n")


def flourish(ink=SAGE, accent=TEAL):
    W = 200.0
    c = W / 2
    r0, R, wdt = 20.0, 88.0, 27.0
    p = []
    for k in range(4):
        ang = 45 + k * 90
        d = (f"M 0 {-r0} Q {wdt} {-(r0 + R) / 2:.2f} 0 {-R} "
             f"Q {-wdt} {-(r0 + R) / 2:.2f} 0 {-r0} Z")
        p.append(f'<path d="{d}" fill="none" stroke="{ink}" '
                 f'stroke-width="5" stroke-linejoin="round" '
                 f'transform="translate({c} {c}) rotate({ang})"/>')
    for k in range(4):
        rad = math.radians(k * 90)
        p.append(f'<circle cx="{c + 52 * math.cos(rad):.2f}" '
                 f'cy="{c + 52 * math.sin(rad):.2f}" r="6.5" fill="{ink}"/>')
    p.append(f'<circle cx="{c}" cy="{c}" r="7" fill="none" '
             f'stroke="{accent}" stroke-width="2"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {W:g}" '
            f'width="{W:g}" height="{W:g}"><title>Flourish</title>'
            + "".join(p) + "</svg>\n")


def corner(a=SAGE, b=TEAL):
    """Triangular corner fill, echoing the mood board's corner borders."""
    W = 240.0
    p = []
    n = 9
    step = W / n
    for i in range(n):
        for j in range(n - i):
            cx, cy = step / 2 + j * step, step / 2 + i * step
            if (i + j) % 2 == 0:
                p.append(diamond(cx, cy, 9.4, b, 1.5))
            else:
                p.append(quatrefoil(cx, cy, 5.8, 5.4, a, 1.2))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {W:g}" '
            f'width="{W:g}" height="{W:g}"><title>Corner ornament</title>'
            + "".join(p) + "</svg>\n")


if __name__ == "__main__":
    for suffix, inks in [("", (SAGE, TEAL)), ("-light", (ROSE, CREAM))]:
        open(f"assets/divider{suffix}.svg", "w").write(divider(*inks))
        open(f"assets/flourish{suffix}.svg", "w").write(flourish(*inks))
        open(f"assets/corner{suffix}.svg", "w").write(corner(*inks))
        print(f"wrote divider{suffix}.svg, flourish{suffix}.svg, corner{suffix}.svg")
