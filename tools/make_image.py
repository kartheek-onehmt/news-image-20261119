"""Draws entry.png: one image summing up the world news of Thursday 19 November 2026.

Run locally (needs Pillow): python3 tools/make_image.py
The entry program (main.py) only copies the finished entry.png, so the sandbox needs nothing installed.
Stories are taken from that day's reporting (Wikipedia current events, AP/AFP/Al Jazeera via
Foreign Exchanges' world roundup); each one appears in at least two of those sources.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
ROOT = Path(__file__).resolve().parent.parent
FONTS = Path("/System/Library/Fonts/Supplemental")

PAPER = (246, 241, 230)
INK = (24, 24, 28)
GREY = (92, 92, 100)
RULE = (190, 182, 165)
RED = (196, 40, 40)
FIRE = (240, 120, 30)
GOLD = (222, 170, 40)
BLUE = (40, 80, 160)
SEA = (60, 110, 170)

REGION_COLOURS = {
    "WORLD COURT": (110, 60, 140),
    "ASIA-PACIFIC": (200, 70, 50),
    "EUROPE": (40, 90, 170),
    "MIDDLE EAST": (190, 120, 20),
    "GULF": (20, 120, 130),
    "ASIA": (170, 50, 90),
    "AFRICA": (40, 130, 70),
    "AMERICAS": (30, 110, 160),
}


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


BLACK = "Arial Black.ttf"
BOLD = "Arial Bold.ttf"
REG = "Arial.ttf"


def wrap(draw, text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def text_block(draw, x, y, text, fnt, width, fill, gap=4):
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + gap
    return y


# ---------- icons: each draws inside the box (x0, y0, x1, y1) ----------

def burst(d, cx, cy, r, colour=FIRE, inner=GOLD, points=10):
    import math
    pts = []
    for i in range(points * 2):
        a = math.pi * i / points
        rr = r if i % 2 == 0 else r * 0.5
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=colour)
    d.ellipse((cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3), fill=inner)


def icon_scales(d, box):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    top, bottom = y0 + 10, y1 - 8
    d.rectangle((cx - 5, top + 10, cx + 5, bottom - 14), fill=INK)
    d.rectangle((cx - 40, bottom - 14, cx + 40, bottom), fill=INK)
    d.ellipse((cx - 11, top, cx + 11, top + 22), fill=INK)
    beam_y = top + 30
    d.line((cx - 95, beam_y + 14, cx + 95, beam_y - 14), fill=INK, width=8)
    for px, py in ((cx - 95, beam_y + 14), (cx + 95, beam_y - 14)):
        d.line((px, py, px - 34, py + 58), fill=INK, width=3)
        d.line((px, py, px + 34, py + 58), fill=INK, width=3)
        d.chord((px - 42, py + 36, px + 42, py + 80), 0, 180, fill=GOLD, outline=INK, width=3)


def person(d, cx, base, colour, scale=1.0):
    r = 17 * scale
    d.ellipse((cx - r, base - 92 * scale, cx + r, base - 92 * scale + 2 * r), fill=(70, 55, 45))
    d.rounded_rectangle((cx - 34 * scale, base - 52 * scale, cx + 34 * scale, base), radius=int(18 * scale), fill=colour)
    d.polygon([(cx - 6 * scale, base - 52 * scale), (cx + 6 * scale, base - 52 * scale), (cx, base - 22 * scale)], fill=(240, 240, 240))


def icon_summit(d, box):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    base = y1 - 30
    # three leaders, coloured after their flags: US blue, China red, Russia blue/white
    person(d, cx - 110, base, (30, 50, 120))
    person(d, cx, base - 6, (200, 30, 30), 1.08)
    person(d, cx + 110, base, (60, 90, 170))
    d.rounded_rectangle((cx - 170, base - 4, cx + 170, base + 18), radius=8, fill=(120, 80, 50))
    # small flags on the table
    def flag(fx, stripes):
        h = 18 / len(stripes)
        for i, c in enumerate(stripes):
            d.rectangle((fx, base - 34 + i * h, fx + 26, base - 34 + (i + 1) * h), fill=c)
        d.line((fx, base - 34, fx, base - 4), fill=INK, width=2)
    flag(cx - 160, [(178, 34, 52), (255, 255, 255), (60, 59, 110)])
    d.rectangle((cx + 52, base - 34, cx + 78, base - 16), fill=(222, 41, 16))
    d.text((cx + 54, base - 37), "★", font=font("Arial Unicode.ttf", 12), fill=(255, 222, 0))
    d.line((cx + 52, base - 34, cx + 52, base - 4), fill=INK, width=2)
    flag(cx + 134, [(255, 255, 255), (0, 57, 166), (213, 43, 30)])


def icon_bridge(d, box):
    x0, y0, x1, y1 = box
    deck = y1 - 42
    d.rectangle((x0 + 14, deck + 22, x1 - 14, y1 - 4), fill=SEA)
    d.rectangle((x0 + 14, deck - 8, x1 - 14, deck + 4), fill=INK)
    span = (x1 - x0 - 28) / 4
    for i in range(4):
        ax = x0 + 14 + i * span
        d.arc((ax, deck - 40, ax + span, deck + 40), 180, 360, fill=INK, width=5)
        d.rectangle((ax + span - 4, deck, ax + span + 4, deck + 24), fill=INK)
    burst(d, x0 + 14 + span * 2.5, deck - 20, 34)
    # missile trail toward the right
    d.line((x1 - 30, y0 + 10, x0 + (x1 - x0) * 0.3, y0 + 30), fill=GREY, width=3)
    burst(d, x0 + (x1 - x0) * 0.25, y0 + 34, 18, colour=RED)


def icon_tower(d, box):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2 + 20
    bottom = y1 - 4
    d.polygon([(cx - 28, bottom), (cx + 28, bottom), (cx + 14, y0 + 10), (cx - 6, y0 + 4)], fill=(60, 70, 90))
    for yy in range(int(y0 + 22), int(bottom - 6), 12):
        d.line((cx - 20, yy, cx + 18, yy), fill=(130, 150, 180), width=2)
    for bx, bh in ((cx - 110, 60), (cx - 75, 90), (cx + 50, 70), (cx + 85, 45)):
        d.rectangle((bx, bottom - bh, bx + 30, bottom), fill=(120, 125, 140))
    d.line((x0 + 10, y0 + 70, cx - 16, y0 + 34), fill=GREY, width=3)
    burst(d, cx - 6, y0 + 32, 26)


def icon_tanker(d, box):
    x0, y0, x1, y1 = box
    water = y1 - 22
    d.rectangle((x0 + 6, water, x1 - 6, y1 - 2), fill=SEA)
    d.polygon([(x0 + 30, water - 30), (x1 - 40, water - 30), (x1 - 20, water - 52), (x1 - 20, water - 30), (x1 - 52, water + 4), (x0 + 40, water + 4)], fill=(150, 40, 40))
    d.rectangle((x0 + 30, water - 46, x1 - 40, water - 30), fill=(70, 70, 75))
    d.rectangle((x1 - 80, water - 80, x1 - 48, water - 46), fill=(235, 235, 235))
    d.ellipse((x0 + 40, y0 - 10, x0 + 110, y0 + 14), fill=(90, 90, 95))
    d.ellipse((x0 + 90, y0 - 16, x0 + 170, y0 + 8), fill=(125, 125, 130))
    for fx, fr in ((x0 + 80, 30), (x0 + 125, 22)):
        burst(d, fx, water - 50, fr)


def icon_chair(d, box):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2 - 30
    bottom = y1 - 4
    d.rounded_rectangle((cx - 34, y0 + 6, cx + 34, bottom - 52), radius=10, fill=(140, 30, 40))
    d.rectangle((cx - 44, bottom - 56, cx + 44, bottom - 40), fill=(110, 25, 30))
    d.rectangle((cx - 40, bottom - 40, cx - 32, bottom), fill=INK)
    d.rectangle((cx + 32, bottom - 40, cx + 40, bottom), fill=INK)
    # emblem of state: a gold soyombo-like disc
    d.ellipse((cx - 14, y0 + 22, cx + 14, y0 + 50), fill=GOLD)
    # exit arrow
    ax = cx + 60
    d.line((ax, y0 + 60, ax + 70, y0 + 60), fill=RED, width=10)
    d.polygon([(ax + 70, y0 + 44), (ax + 98, y0 + 60), (ax + 70, y0 + 76)], fill=RED)


def icon_envoy(d, box):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    bottom = y1 - 4
    # door frame with a figure walking out
    d.rectangle((cx - 110, y0 + 4, cx - 30, bottom), outline=INK, width=6)
    d.rectangle((cx - 104, y0 + 10, cx - 36, bottom), fill=(80, 140, 200))
    person(d, cx + 30, bottom, (40, 40, 50), 0.95)
    d.rectangle((cx + 58, bottom - 40, cx + 82, bottom - 14), fill=(120, 80, 40))  # briefcase
    d.line((cx + 100, y0 + 50, cx + 150, y0 + 50), fill=RED, width=9)
    d.polygon([(cx + 150, y0 + 36), (cx + 174, y0 + 50), (cx + 150, y0 + 64)], fill=RED)
    d.text((cx + 96, y0 + 66), "72h", font=font(BLACK, 22), fill=RED)


def icon_ballot(d, box):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    bottom = y1 - 4
    d.rectangle((cx - 26, y0 - 6, cx + 26, bottom - 44), fill=(255, 255, 255), outline=INK, width=3)
    d.text((cx - 10, y0 - 6), "3", font=font(BLACK, 34), fill=RED)
    d.rectangle((cx - 70, bottom - 48, cx + 70, bottom), fill=(30, 80, 150))
    d.rectangle((cx - 40, bottom - 52, cx + 40, bottom - 44), fill=INK)
    d.text((cx - 32, bottom - 38), "2027", font=font(BLACK, 22), fill=(255, 255, 255))


# ---------- layout ----------

def panel(d, box, region, headline, sub, icon, icon_h, head_size, sub_size):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(252, 249, 242), outline=RULE, width=2)
    pad = 14
    icon(d, (x0 + pad, y0 + pad, x1 - pad, y0 + pad + icon_h))
    ty = y0 + pad + icon_h + 10
    tag = font(BLACK, 14)
    tw = d.textlength(region, font=tag)
    d.rectangle((x0 + pad, ty, x0 + pad + tw + 12, ty + 22), fill=REGION_COLOURS[region])
    d.text((x0 + pad + 6, ty + 2), region, font=tag, fill=(255, 255, 255))
    ty += 30
    ty = text_block(d, x0 + pad, ty, headline, font(BLACK, head_size), x1 - x0 - 2 * pad, INK, gap=2)
    text_block(d, x0 + pad, ty + 4, sub, font(BOLD, sub_size), x1 - x0 - 2 * pad, GREY, gap=3)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # masthead
    d.rectangle((0, 0, W, 112), fill=INK)
    d.text((24, 12), "THE WORLD ON", font=font(BLACK, 26), fill=GOLD)
    d.text((24, 40), "THURSDAY 19 NOVEMBER 2026", font=font(BLACK, 50), fill=(255, 255, 255))
    d.rectangle((0, 112, W, 118), fill=RED)

    m, g = 18, 14
    top = 130
    lead_h = 360
    lead_w = (W - 2 * m - g) // 2
    panel(d, (m, top, m + lead_w, top + lead_h), "WORLD COURT",
          "UN court rules Myanmar committed genocide against the Rohingya",
          "ICJ's first finding that a state is guilty of genocide",
          icon_scales, 160, 32, 19)
    panel(d, (m + lead_w + g, top, W - m, top + lead_h), "ASIA-PACIFIC",
          "Trump, Xi and Putin hold first three-way summit",
          "APEC, Shenzhen: joint declaration on nuclear war, oil and UN reform",
          icon_summit, 160, 32, 19)

    small_w = (W - 2 * m - 2 * g) // 3
    small_h = (H - (top + lead_h + g) - m - g) // 2
    rows = [
        [("EUROPE", "Russian strikes hit Kyiv; Ukraine hits Kerch bridge",
          "Austrian and Dutch embassies damaged", icon_bridge),
         ("MIDDLE EAST", "Houthi missiles hit Riyadh's PIF Tower",
          "Damage in finance district, no injuries", icon_tower),
         ("GULF", "Tanker on fire after hitting mine near Hormuz",
          "Iran's navy reports the blast", icon_tanker)],
        [("ASIA", "Mongolia's president Khurelsukh resigns",
          "Parliament accepts; vote within 4 months", icon_chair),
         ("AFRICA", "Somalia expels UAE ambassador",
          "Accuses Abu Dhabi of undermining sovereignty", icon_envoy),
         ("AMERICAS", "Bukele files to run for a third term",
          "El Salvador's 2027 presidential race", icon_ballot)],
    ]
    for r, row in enumerate(rows):
        y = top + lead_h + g + r * (small_h + g)
        for c, (region, head, sub, icon) in enumerate(row):
            x = m + c * (small_w + g)
            panel(d, (x, y, x + small_w, y + small_h), region, head, sub, icon, 92, 21, 14)

    out = ROOT / "entry.png"
    img.save(out, optimize=True)
    print(out, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
