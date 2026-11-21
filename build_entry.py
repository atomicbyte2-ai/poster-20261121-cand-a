#!/usr/bin/env python3
"""poster-20261121-cand-a — "VELMARA — The City That Sails at Dusk".

Generates entry.png deterministically with PIL: a travel poster for an
invented lagoon city whose houses drift on the water at dusk, anchored by
one landmark — a tall sailing lighthouse whose light is a warm gold sail.
Flat vector-style drawing with PIL shapes only (no photos). All paths
resolve from this script's own directory.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = 1024
H = 1024

# palette: deep dusk indigo + teal water + warm gold light
INDIGO_TOP = (16, 18, 48)
INDIGO_MID = (38, 40, 88)
VIOLET = (74, 58, 118)
DUSK = (150, 92, 110)
GOLD_BAND = (232, 164, 76)
CREAM = (250, 238, 208)
GOLD = (244, 190, 92)
GOLD_DEEP = (214, 140, 52)
TEAL_DEEP = (14, 74, 84)
TEAL = (22, 104, 110)
TEAL_LIGHT = (52, 148, 146)
TOWER = (24, 26, 52)
HOUSE = (18, 22, 46)
WINDOW = (255, 205, 110)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, x0, y0, x1, y1, stops):
    """Vertical gradient through (position, colour) stops."""
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0 - 1))
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                tt = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                col = lerp(c0, c1, tt)
                break
        else:
            col = stops[-1][1]
        draw.line([(x0, y), (x1, y)], fill=col)


def glow_layer(size, cx, cy, radius, colour, peak=150):
    """Radial glow as an RGBA layer: soft concentric discs."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    g = ImageDraw.Draw(layer)
    steps = 24
    for i in range(steps, 0, -1):
        r = radius * i / steps
        a = int(peak * (1 - i / steps) ** 2)
        g.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour + (a,))
    return layer


def letterspaced(draw, cx, y, text, fnt, fill, tracking):
    """Draw text centred on cx with extra tracking between letters."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking
    return total


def house(draw, x, y, w, h, win_seed):
    """A small drifting house on the water: dark body, pitched roof,
    warm lit windows; returns the waterline y for its reflection."""
    rnd = random.Random(win_seed)
    draw.polygon([(x, y), (x + w / 2, y - h * 0.55), (x + w, y)],
                 fill=(HOUSE[0] - 4, HOUSE[1] - 4, HOUSE[2] - 2))
    draw.rectangle([x, y, x + w, y + h], fill=HOUSE)
    # lit windows
    cols = max(1, int(w // 22))
    rows = max(1, int(h // 24))
    for r in range(rows):
        for c in range(cols):
            if rnd.random() < 0.72:
                wx = x + 6 + c * 22
                wy = y + 7 + r * 24
                draw.rectangle([wx, wy, wx + 10, wy + 12], fill=WINDOW)
    # tiny chimney
    draw.rectangle([x + w - 14, y - h * 0.55 - 8, x + w - 6, y - h * 0.55 + 6],
                   fill=HOUSE)
    return y + h


def reflection(draw, x, y0, y1, colour, alpha, jag):
    """Vertical streak reflection under (x, y0..y1) with slight jitter."""
    rnd = random.Random(jag)
    for yy in range(y0, y1, 4):
        wob = rnd.randint(-3, 3)
        a = int(alpha * (1 - (yy - y0) / max(1, (y1 - y0))))
        draw.line([(x - 14 + wob, yy), (x + 14 + wob, yy)],
                  fill=colour + (a,), width=3)


def main():
    img = Image.new("RGB", (W, H), INDIGO_TOP)
    d = ImageDraw.Draw(img, "RGBA")

    horizon = 640  # waterline

    # --- sky: indigo -> violet -> dusk rose -> gold band at horizon
    vgrad(d, 0, 0, W, horizon, [
        (0.00, INDIGO_TOP),
        (0.45, INDIGO_MID),
        (0.75, VIOLET),
        (0.92, DUSK),
        (1.00, GOLD_BAND),
    ])

    # --- stars in the upper sky
    rnd = random.Random(20261121)
    for _ in range(110):
        sx = rnd.randint(8, W - 8)
        sy = rnd.randint(8, 300)
        r = rnd.choice([1, 1, 1, 2])
        a = rnd.randint(90, 220)
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 244, 214, a))
    # a few brighter stars with a cross sparkle
    for sx, sy in [(120, 90), (880, 140), (700, 60), (300, 200)]:
        d.line([(sx - 7, sy), (sx + 7, sy)], fill=(255, 244, 214, 230), width=2)
        d.line([(sx, sy - 7), (sx, sy + 7)], fill=(255, 244, 214, 230), width=2)

    # --- low sun glow behind the lighthouse, on the horizon
    sun_cx, sun_cy = 640, horizon - 30
    img.paste(Image.alpha_composite(img.convert("RGBA"),
              glow_layer((W, H), sun_cx, sun_cy, 260, (255, 190, 90), 170)),
              (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([sun_cx - 58, sun_cy - 58, sun_cx + 58, sun_cy + 58],
              fill=(255, 214, 130, 255))
    d.ellipse([sun_cx - 40, sun_cy - 40, sun_cx + 40, sun_cy + 40],
              fill=(255, 232, 170, 255))

    # --- distant headland silhouettes left and right of the horizon
    d.polygon([(0, horizon), (0, horizon - 46), (90, horizon - 96),
               (210, horizon - 40), (300, horizon - 62), (380, horizon),
               (380, horizon), (0, horizon)], fill=(30, 28, 62, 255))
    d.polygon([(W, horizon), (W, horizon - 38), (930, horizon - 78),
               (830, horizon - 30), (760, horizon - 52), (700, horizon)],
              fill=(30, 28, 62, 255))

    # --- water: teal gradient, lighter toward the gold horizon
    vgrad(d, 0, horizon, W, H, [
        (0.00, (38, 120, 122)),
        (0.35, TEAL),
        (1.00, TEAL_DEEP),
    ])
    # gold shimmer band on the water just below the horizon
    for yy in range(horizon + 2, horizon + 60, 5):
        a = int(110 * (1 - (yy - horizon) / 60))
        d.line([(0, yy), (W, yy)], fill=(244, 190, 92, a), width=2)

    # --- the sailing lighthouse (slightly right of centre)
    lx = 640  # tower centre x
    base_y = horizon + 6
    top_y = 380  # kept below the sub-copy so mast and sail never touch the name
    # light beam fanning left across the dusk sky: one warm, narrow beam
    d.polygon([(lx - 6, top_y + 14), (60, top_y + 8), (60, top_y + 92)],
              fill=(255, 214, 130, 60))
    # the gold sail: one tall triangular sail, the lighthouse's light
    sail = [(lx + 4, top_y - 100), (lx + 4, top_y + 10), (lx + 168, top_y + 10)]
    img.paste(Image.alpha_composite(img.convert("RGBA"),
              glow_layer((W, H), lx + 70, top_y - 40, 150, (255, 190, 90), 110)),
              (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon(sail, fill=(250, 198, 100, 255), outline=(255, 232, 170, 255))
    # sail seams
    d.line([(lx + 4, top_y - 66), (lx + 118, top_y + 10)],
           fill=(214, 140, 52, 255), width=3)
    d.line([(lx + 4, top_y - 33), (lx + 68, top_y + 10)],
           fill=(214, 140, 52, 255), width=3)
    # mast
    d.line([(lx + 4, top_y - 108), (lx + 4, top_y + 12)],
           fill=(24, 26, 52, 255), width=6)
    # lamp room + gallery at the top of the tower
    d.rectangle([lx - 34, top_y, lx + 34, top_y + 16], fill=(20, 22, 46, 255))
    d.rectangle([lx - 20, top_y - 26, lx + 20, top_y], fill=(255, 214, 130, 255))
    d.ellipse([lx - 26, top_y - 34, lx + 26, top_y - 18],
              fill=(255, 232, 170, 255))
    # tapered tower
    d.polygon([(lx - 30, top_y + 16), (lx + 30, top_y + 16),
               (lx + 52, base_y), (lx - 52, base_y)], fill=TOWER)
    # gold bands on the tower
    for by, bw in [(top_y + 70, 37), (top_y + 140, 43), (top_y + 205, 48)]:
        d.polygon([(lx - bw, by), (lx + bw, by), (lx + bw + 3, by + 16),
                   (lx - bw - 3, by + 16)], fill=(GOLD_DEEP[0], GOLD_DEEP[1],
                   GOLD_DEEP[2], 255))
    # lit windows up the tower
    for wy in range(top_y + 50, base_y - 30, 52):
        d.rectangle([lx - 7, wy, lx + 7, wy + 16], fill=WINDOW)
    # rock base the lighthouse stands on
    d.polygon([(lx - 78, base_y), (lx - 58, base_y - 26), (lx - 20, base_y - 34),
               (lx + 30, base_y - 30), (lx + 66, base_y - 22), (lx + 84, base_y)],
              fill=(16, 18, 40, 255))

    # --- lighthouse reflection in the water
    for yy in range(base_y + 4, H - 40, 5):
        t = (yy - base_y) / (H - 40 - base_y)
        wob = random.Random(yy).randint(-6, 6)
        half = int(46 * (1 - t * 0.4))
        a = int(120 * (1 - t))
        d.line([(lx - half + wob, yy), (lx + half + wob, yy)],
               fill=(244, 190, 92, a), width=3)
    # sun reflection
    for yy in range(horizon + 4, H - 120, 5):
        t = (yy - horizon) / (H - 120 - horizon)
        wob = random.Random(yy * 3).randint(-10, 10)
        a = int(90 * (1 - t))
        d.line([(sun_cx - 34 + wob, yy), (sun_cx + 34 + wob, yy)],
               fill=(255, 214, 130, a), width=3)

    # --- drifting houses on the lagoon (left, mid, right; one near, one far)
    houses = [
        (150, 700, 74, 46, 11),
        (300, 742, 58, 38, 22),
        (880, 712, 66, 42, 33),
        (470, 800, 92, 56, 44),
        (790, 830, 80, 50, 55),
        (120, 860, 96, 58, 66),
    ]
    for (hx, hy, hw, hh, seed) in houses:
        wl = house(d, hx, hy, hw, hh, seed)
        # warm reflection under each house
        for yy in range(wl + 3, min(wl + 66, H - 8), 5):
            t = (yy - wl) / 66
            wob = random.Random(yy + seed).randint(-4, 4)
            a = int(100 * (1 - t))
            d.line([(hx + 6 + wob, yy), (hx + hw - 6 + wob, yy)],
                   fill=(255, 205, 110, a), width=3)

    # --- a few small boats with lanterns drifting between the houses
    for (bx, by, s) in [(250, 880, 1.0), (620, 905, 0.8), (920, 880, 0.9)]:
        bw = int(52 * s)
        d.polygon([(bx, by), (bx + bw, by), (bx + bw - 10, by + 12),
                   (bx + 10, by + 12)], fill=(18, 22, 46, 255))
        d.line([(bx + bw / 2, by - 26 * s), (bx + bw / 2, by)],
               fill=(18, 22, 46, 255), width=3)
        d.ellipse([bx + bw / 2 - 5, by - 32 * s, bx + bw / 2 + 5, by - 22 * s],
                  fill=(255, 205, 110, 255))

    # --- place name: giant letterspaced cream serif across the top third
    name_font = font(SERIF_B, 118)
    # auto-fit: shrink until it fits inside the margins
    while d.textlength("VELMARA", font=name_font) + 6 * 26 > W - 120:
        name_font = font(SERIF_B, name_font.size - 4)
    # soft shadow for legibility, then the cream letters
    letterspaced(d, W // 2 + 4, 92, "VELMARA", name_font, (10, 12, 34, 200), 26)
    letterspaced(d, W // 2, 88, "VELMARA", name_font, CREAM, 26)

    # --- sub-copy under the name, same family, letterspaced
    sub = "WHERE THE HOUSES DRIFT WITH THE TIDE"
    sub_font = font(SERIF, 30)
    while d.textlength(sub, font=sub_font) + 8 * (len(sub) - 1) > W - 140:
        sub_font = font(SERIF, sub_font.size - 2)
    letterspaced(d, W // 2, 232, sub, sub_font, (250, 238, 208, 235), 8)

    # --- thin gold rule under the sub-copy (short, centred, clear of the mast)
    d.line([(W // 2 - 90, 292), (W // 2 + 90, 292)],
           fill=(244, 190, 92, 255), width=3)

    # --- thin cream frame inset, poster feel
    d.rectangle([22, 22, W - 23, H - 23], outline=(250, 238, 208, 170), width=3)

    img.save(OUT, optimize=True)
    print(f"wrote {OUT} {W}x{H}")


if __name__ == "__main__":
    main()
