"""Draws entry.png: a 41-story front page of Thursday 19 November 2026, laid out for 1024x1024.

Run locally (needs Pillow): python3 tools/front_page.py
main.py only copies the finished entry.png, so the sandbox needs nothing installed.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
ROOT = Path(__file__).resolve().parent.parent
SUP = Path("/System/Library/Fonts/Supplemental")

PAPER = (250, 245, 234)
CARD = (255, 252, 245)
INK = (26, 30, 44)
GREY = (90, 92, 100)
RULE = (196, 188, 170)
RED = (190, 40, 40)
FIRE = (240, 120, 30)
GOLD = (232, 180, 50)
SEA = (60, 110, 170)
SKY = (196, 224, 240)

REGIONS = {
    "ASIA": (214, 100, 30),
    "MIDDLE EAST": (188, 44, 44),
    "EUROPE": (44, 90, 170),
    "AFRICA": (48, 138, 60),
    "AMERICAS": (122, 62, 172),
    "OCEANIA": (28, 138, 138),
    "GLOBAL": (78, 84, 96),
}


def F(name, size):
    return ImageFont.truetype(str(SUP / name), size)


SERIF_B = "Georgia Bold.ttf"
SERIF = "Georgia.ttf"
SERIF_I = "Georgia Italic.ttf"
SANS_B = "Arial Bold.ttf"
SANS = "Arial.ttf"
NARROW = "Arial Narrow.ttf"
NARROW_B = "Arial Narrow Bold.ttf"

# ---------- the day's stories (place, headline, line, source, region) ----------

LEAD = [
    ("SHENZHEN · SUMMIT", "Trump, Xi and Putin hold first three-way summit",
     "About 90 minutes at APEC; a four-point declaration on UN reform, oil supply and nuclear risk.",
     "CFR · RFE/RL", "ASIA"),
    ("THE HAGUE · JUSTICE", "World Court: Myanmar committed genocide",
     "The ICJ's first-ever finding of genocide by a state, over the 2017 campaign against the Rohingya.",
     "AP · Reuters", "GLOBAL"),
    ("NEW YORK · MARKETS", "Anthropic soars, then fades, in Nasdaq debut",
     "Opened at $111.50 against an $83 IPO price; closed at $97.17, up 17%.",
     "Bloomberg · CNN", "AMERICAS"),
]

SECOND = [
    ("NEW YORK", "Dow sheds 1,101 as AI sell-off hits day six", "S&P 500 down 2%", "AP", "AMERICAS"),
    ("MOGADISHU", "Somalia expels the UAE's ambassador", "72 hours to leave", "AFP", "AFRICA"),
    ("CRIMEA", "Kerch Bridge hit for a third time this week", "Rail traffic halted", "BBC · AP", "EUROPE"),
    ("RIYADH", "Houthi strike damages Riyadh's tallest tower", "PIF Tower; no casualties", "NYT", "MIDDLE EAST"),
    ("ANDHRA PRADESH", "Cyclone Akvan turns very severe", "Landfall due Friday", "IMD", "ASIA"),
    ("SEOUL", "Top court voids ex-PM Han's conviction", "Martial-law case sent back", "Yonhap", "ASIA"),
    ("COPENHAGEN", "Denmark backs Arctic pact with U.S.", "Unanimous Greenland vote", "AP", "EUROPE"),
    ("GAZA", "Israel ends one-day Nuseirat raid", "About 6,000 displaced", "Foreign Exchanges", "MIDDLE EAST"),
    ("WORLDWIDE", "GTA VI finally goes on sale", "13 years after GTA V", "Rockstar", "GLOBAL"),
    ("WASHINGTON", "Trump fires his cyber chief", "Sean Cairncross out", "Just Security", "AMERICAS"),
]

ALSO = [
    ("Kyiv", "Russian strike damages Austrian, Dutch embassies", "EUROPE"),
    ("Ukraine", "Russian attacks kill 25, injure 79 in a day", "EUROPE"),
    ("Berlin", "Kyiv's backers meet; Putin rules out ceasefire talk", "EUROPE"),
    ("Belgrade", "Čupić elected Speaker, becomes interim president", "EUROPE"),
    ("London", "UK–EU reset deal near after deal with France", "EUROPE"),
    ("Baghdad", "Deal ends Jurf al-Sakhar standoff", "MIDDLE EAST"),
    ("Tehran", "Trump on Iran: “see what happens” after Jan. 1", "MIDDLE EAST"),
    ("Taiz", "Water output nearly halved; 800,000 cut off", "MIDDLE EAST"),
    ("Ulaanbaatar", "Parliament accepts the president's resignation", "ASIA"),
    ("Yongbyon", "IAEA: North Korea expanding enrichment plant", "ASIA"),
    ("Chattogram", "Yunus family home set on fire", "ASIA"),
    ("Khyber Pakhtunkhwa", "Army says 22 militants killed", "ASIA"),
    ("Tokyo", "Takaichi says she held talks with Putin", "ASIA"),
    ("Shenzhen", "Trump leaves China without meeting Kim", "ASIA"),
    ("Port Vila", "Vanuatu calls for COP process reform", "OCEANIA"),
    ("American Samoa", "Firm leases 31.5m acres of seabed", "OCEANIA"),
    ("Wellington", "Bumrah strikes second ball of first Test", "OCEANIA"),
    ("Phoenix", "Arizona probes AI agents in banks", "AMERICAS"),
    ("Georgetown", "U.S. official floated ceding Essequibo", "AMERICAS"),
    ("Washington", "Supreme Court asked to halt Venezuelans' TPS", "AMERICAS"),
    ("Mexico City", "Study: 460,000 killed since 2006", "AMERICAS"),
    ("Port-au-Prince", "34 gang members killed in Martissant", "AMERICAS"),
    ("Austin", "Musk calls $446m political spending foolish", "AMERICAS"),
    ("Denver", "Russian arrested for spying on Palantir staff", "AMERICAS"),
    ("Illinois", "Terror charges over Hindu temple plot", "AMERICAS"),
    ("Washington", "Judge extends block on “triumphal arch”", "AMERICAS"),
    ("Nyala", "Army bombs RSF intelligence HQ", "AFRICA"),
    ("Bududa", "Landslide survivors take case to UN", "AFRICA"),
]

STATS = [
    ("3", "leaders at one table"),
    ("$97.17", "Anthropic's first close"),
    ("−1,101", "Dow points lost"),
    ("730,000", "Rohingya driven out, 2017"),
    ("72 hrs", "for the UAE envoy to leave"),
    ("25", "killed in Ukraine in a day"),
]

# ---------- helpers ----------


def wrap(d, text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if d.textlength(trial, font=fnt) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    lines.append(line)
    return lines


def block(d, x, y, text, fnt, width, fill, gap=2, max_lines=None):
    lines = wrap(d, text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + gap
    return y


def badge(d, x, y, n, colour, r=9):
    d.ellipse((x, y, x + 2 * r, y + 2 * r), fill=colour)
    f = F(SANS_B, 11 if n < 10 else 10)
    tw = d.textlength(str(n), font=f)
    d.text((x + r - tw / 2, y + r - 7), str(n), font=f, fill=(255, 255, 255))


def burst(d, cx, cy, r, colour=FIRE, inner=GOLD, points=9):
    pts = []
    for i in range(points * 2):
        a = math.pi * i / points
        rr = r if i % 2 == 0 else r * 0.5
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=colour)
    d.ellipse((cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3), fill=inner)


def flag(d, x, y, w, h, kind):
    if kind == "us":
        for i in range(7):
            d.rectangle((x, y + i * h / 7, x + w, y + (i + 1) * h / 7), fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
        d.rectangle((x, y, x + w * 0.42, y + h * 4 / 7), fill=(60, 59, 110))
    elif kind == "cn":
        d.rectangle((x, y, x + w, y + h), fill=(222, 41, 16))
        star(d, x + w * 0.25, y + h * 0.33, h * 0.24, (255, 222, 0))
    elif kind == "ru":
        for i, c in enumerate([(255, 255, 255), (0, 57, 166), (213, 43, 30)]):
            d.rectangle((x, y + i * h / 3, x + w, y + (i + 1) * h / 3), fill=c)
    elif kind == "dk":
        d.rectangle((x, y, x + w, y + h), fill=(200, 16, 46))
        d.rectangle((x + w * 0.3, y, x + w * 0.42, y + h), fill=(255, 255, 255))
        d.rectangle((x, y + h * 0.42, x + w, y + h * 0.58), fill=(255, 255, 255))
    elif kind == "so":
        d.rectangle((x, y, x + w, y + h), fill=(65, 137, 221))
        star(d, x + w / 2, y + h / 2, h * 0.3, (255, 255, 255))
    elif kind == "kr":
        d.rectangle((x, y, x + w, y + h), fill=(255, 255, 255), outline=RULE)
        cx, cy, r = x + w / 2, y + h / 2, h * 0.25
        d.pieslice((cx - r, cy - r, cx + r, cy + r), 180, 360, fill=(205, 46, 58))
        d.pieslice((cx - r, cy - r, cx + r, cy + r), 0, 180, fill=(0, 71, 160))
    d.rectangle((x, y, x + w, y + h), outline=(60, 60, 60))


def star(d, cx, cy, r, colour):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + math.pi * i / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=colour)


def tag(d, x, y, text, fill=RED):
    f = F(SANS_B, 9)
    tw = d.textlength(text, font=f)
    d.rectangle((x, y, x + tw + 8, y + 13), fill=fill)
    d.text((x + 4, y + 1), text, font=f, fill=(255, 255, 255))


# ---------- pictures: each fills box (x0, y0, x1, y1) ----------


def pic_summit(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(250, 232, 200))
    d.rectangle((x0, y1 - 16, x1, y1), fill=(214, 200, 176))
    cx = (x0 + x1) / 2
    for i, (k, label) in enumerate((("us", "U.S."), ("cn", "CHINA"), ("ru", "RUSSIA"))):
        px = cx + (i - 1) * 96
        flag(d, px - 16, y0 + 6, 32, 20, k)
        d.ellipse((px - 12, y1 - 62, px + 12, y1 - 38), fill=(84, 64, 50))
        d.rounded_rectangle((px - 26, y1 - 40, px + 26, y1 - 16), radius=10, fill=(52, 46, 52))
        d.rectangle((px - 32, y1 - 30, px + 32, y1 - 14), fill=(255, 255, 255), outline=INK)
        f = F(SANS_B, 9)
        d.text((px - d.textlength(label, font=f) / 2, y1 - 28), label, font=f, fill=INK)


def pic_court(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=SKY)
    d.rectangle((x0, y1 - 12, x1, y1), fill=(206, 214, 190))
    bx = x0 + 30
    d.polygon([(bx, y0 + 42), (bx + 75, y0 + 14), (bx + 150, y0 + 42)], fill=(150, 60, 45))
    d.rectangle((bx + 8, y0 + 42, bx + 142, y1 - 12), fill=(176, 76, 56))
    for r in range(2):
        for c in range(6):
            d.rectangle((bx + 16 + c * 21, y0 + 52 + r * 22, bx + 28 + c * 21, y0 + 66 + r * 22), fill=(250, 236, 210))
    cx = x1 - 62
    d.rectangle((cx - 3, y0 + 30, cx + 3, y1 - 18), fill=INK)
    d.rectangle((cx - 22, y1 - 20, cx + 22, y1 - 14), fill=INK)
    d.line((cx - 40, y0 + 34, cx + 40, y0 + 34), fill=INK, width=4)
    for px in (cx - 40, cx + 40):
        d.line((px, y0 + 34, px - 14, y0 + 60), fill=INK, width=2)
        d.line((px, y0 + 34, px + 14, y0 + 60), fill=INK, width=2)
        d.chord((px - 18, y0 + 50, px + 18, y0 + 70), 0, 180, fill=GOLD, outline=INK)
    tag(d, x1 - 92, y0 + 6, "GENOCIDE")


def pic_ipo(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(22, 50, 42))
    for gy in range(int(y0 + 20), int(y1), 18):
        d.line((x0 + 6, gy, x1 - 6, gy), fill=(44, 76, 66))
    d.text((x0 + 10, y0 + 6), "ANT", font=F(SERIF_B, 18), fill=GOLD)
    d.text((x0 + 58, y0 + 11), "NASDAQ · FIRST DAY", font=F(SANS_B, 9), fill=(160, 210, 180))
    pts = [(x0 + 30, y1 - 16, "IPO $83"), (x0 + 110, y0 + 38, "OPEN $111.50"), (x0 + 200, y0 + 66, "LOW $92.72"), (x1 - 34, y0 + 56, "CLOSE $97.17")]
    d.line([(p[0], p[1]) for p in pts], fill=(120, 220, 140), width=4)
    f = F(SANS_B, 9)
    for i, (px, py, label) in enumerate(pts):
        d.ellipse((px - 5, py - 5, px + 5, py + 5), fill=GOLD)
        tx = px - d.textlength(label, font=f) / 2
        tx = max(x0 + 4, min(tx, x1 - 4 - d.textlength(label, font=f)))
        ty = py + 7 if i in (0, 2) else py - 17
        if i == 1:
            tx, ty = px + 9, py - 5
        d.text((tx, ty), label, font=f, fill=(240, 240, 240))


def pic_dow(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(40, 26, 26))
    pts = [(x0 + 10, y0 + 12), (x0 + 40, y0 + 22), (x0 + 60, y0 + 18), (x0 + 95, y0 + 34), (x0 + 120, y0 + 30), (x1 - 22, y1 - 12)]
    d.line(pts, fill=(240, 100, 80), width=3)
    d.polygon([(x1 - 10, y1 - 6), (x1 - 30, y1 - 8), (x1 - 18, y1 - 24)], fill=(240, 100, 80))
    d.text((x0 + 8, y1 - 24), "−1,101", font=F(SERIF_B, 16), fill=(240, 100, 80))


def pic_somalia(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=SKY)
    d.rectangle((x0 + 20, y0 + 26, x0 + 110, y1), fill=(236, 226, 200), outline=GREY)
    for c in range(4):
        d.rectangle((x0 + 28 + c * 20, y0 + 34, x0 + 40 + c * 20, y0 + 44), fill=(110, 130, 160))
    d.line((x0 + 98, y0 + 4, x0 + 98, y0 + 26), fill=INK, width=2)
    flag(d, x0 + 99, y0 + 4, 20, 13, "so")
    cx, cy, r = x1 - 34, y0 + 30, 20
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255), outline=RED, width=3)
    d.line((cx, cy, cx, cy - 13), fill=INK, width=2)
    d.line((cx, cy, cx + 10, cy + 4), fill=INK, width=2)
    tag(d, x1 - 62, y1 - 16, "72 HOURS")


def pic_bridge(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(250, 206, 150))
    d.rectangle((x0, y1 - 18, x1, y1), fill=SEA)
    deck = y1 - 26
    d.rectangle((x0, deck, x1, deck + 4), fill=INK)
    for ax in (x0 + 10, x0 + 70):
        d.arc((ax, deck - 30, ax + 70, deck + 30), 180, 360, fill=INK, width=3)
    for px in range(int(x0 + 6), int(x1), 14):
        d.line((px, deck + 4, px, y1 - 18), fill=INK, width=1)
    burst(d, x1 - 40, deck - 10, 16)


def pic_riyadh(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(26, 30, 60))
    for sx, sy in ((x0 + 12, y0 + 8), (x0 + 50, y0 + 14), (x1 - 20, y0 + 10), (x0 + 90, y0 + 6)):
        d.point((sx, sy), fill=(255, 255, 255))
    for bx, bh in ((x0 + 8, 30), (x0 + 30, 44), (x0 + 52, 24), (x1 - 52, 36), (x1 - 28, 28)):
        d.rectangle((bx, y1 - bh, bx + 18, y1), fill=(60, 66, 110))
    cx = (x0 + x1) / 2 + 6
    d.polygon([(cx - 12, y1), (cx + 12, y1), (cx + 7, y0 + 10), (cx - 3, y0 + 6)], fill=(110, 120, 170))
    d.line((x1 - 10, y0 + 6, cx + 6, y0 + 22), fill=(255, 220, 160), width=1)
    burst(d, cx + 2, y0 + 22, 10)


def pic_cyclone(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(110, 160, 210))
    d.polygon([(x0, y0), (x0 + 50, y0), (x0 + 38, y1), (x0, y1)], fill=(230, 214, 170))
    d.text((x0 + 4, y0 + 3), "ANDHRA PRADESH", font=F(SANS_B, 7), fill=INK)
    cx, cy = x1 - 50, (y0 + y1) / 2 + 2
    for a in (0, 120, 240):
        d.arc((cx - 26, cy - 26, cx + 26, cy + 26), a, a + 80, fill=(255, 255, 255), width=6)
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=INK)
    for k in range(3):
        d.line((cx - 34 - k * 10, cy + 2 + k * 3, cx - 40 - k * 10, cy + 4 + k * 3), fill=RED, width=2)


def pic_seoul(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(232, 216, 186))
    flag(d, x0 + 10, y0 + 10, 34, 22, "kr")
    d.line((x1 - 70, y1 - 8, x1 - 30, y0 + 30), fill=(110, 70, 40), width=5)
    d.rounded_rectangle((x1 - 50, y0 + 14, x1 - 12, y0 + 34), radius=4, fill=(110, 70, 40))
    f = F(SANS_B, 11)
    d.rectangle((x0 + 50, y0 + 38, x0 + 140, y0 + 54), outline=RED, width=2)
    d.text((x0 + 54, y0 + 39), "OVERTURNED", font=f, fill=RED)


def pic_arctic(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=SKY)
    d.polygon([(x0, y1), (x0 + 40, y0 + 34), (x0 + 80, y1 - 12), (x0 + 120, y0 + 30), (x1 - 20, y1 - 6), (x1, y0 + 44), (x1, y1)], fill=(255, 255, 255), outline=(160, 180, 200))
    for i, k in enumerate(("dk", "us")):
        fx = x0 + 14 + i * 40
        d.line((fx, y0 + 6, fx, y0 + 40), fill=INK, width=2)
        flag(d, fx + 1, y0 + 6, 28, 18, k)
    tag(d, x1 - 78, y0 + 8, "UNANIMOUS")


def pic_gaza(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(244, 224, 176))
    for i in range(6):
        tx = x0 + 10 + i * 26
        d.polygon([(tx, y1 - 6), (tx + 11, y1 - 26 - (i % 2) * 6), (tx + 22, y1 - 6)], fill=(214, 214, 220) if i % 2 else (170, 160, 140))
    d.polygon([(x0, y1), (x0 + 30, y0 + 30), (x0 + 60, y1)], fill=(160, 140, 110))
    d.text((x0 + 8, y0 + 6), "6,000", font=F(SERIF_B, 15), fill=RED)
    d.text((x0 + 60, y0 + 10), "DISPLACED", font=F(SANS_B, 9), fill=RED)


def pic_gta(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(80, 40, 120))
    d.ellipse((x1 - 50, y0 + 6, x1 - 16, y0 + 40), fill=(220, 110, 170))
    d.text((x1 - 54, y0 + 30), "VI", font=F(SERIF_B, 22), fill=(240, 120, 180))
    cx, cy = x0 + 56, (y0 + y1) / 2 + 4
    d.rounded_rectangle((cx - 42, cy - 16, cx + 42, cy + 18), radius=16, fill=(250, 250, 250))
    d.rectangle((cx - 28, cy - 2, cx - 14, cy + 2), fill=INK)
    d.rectangle((cx - 23, cy - 7, cx - 19, cy + 7), fill=INK)
    for dx, dy, c in ((20, -5, (220, 60, 60)), (28, 2, (60, 160, 60)), (12, 2, (60, 100, 220))):
        d.ellipse((cx + dx - 3, cy + dy - 3, cx + dx + 3, cy + dy + 3), fill=c)


def pic_cyber(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(18, 28, 48))
    f = F(SANS, 8)
    for i, (px, py) in enumerate(((10, 8), (30, 30), (150, 10), (160, 40), (60, 50))):
        d.text((x0 + px, y0 + py), "01"[i % 2], font=f, fill=(70, 90, 130))
    cx, cy = (x0 + x1) / 2 - 10, (y0 + y1) / 2
    d.polygon([(cx - 22, cy - 22), (cx + 22, cy - 22), (cx + 22, cy + 2), (cx, cy + 24), (cx - 22, cy + 2)], fill=(50, 100, 200))
    d.rectangle((cx - 8, cy - 4, cx + 8, cy + 10), fill=(255, 255, 255))
    d.arc((cx - 6, cy - 14, cx + 6, cy), 180, 360, fill=(255, 255, 255), width=3)
    tag(d, x1 - 44, y1 - 18, "FIRED")


LEAD_PICS = [pic_summit, pic_court, pic_ipo]
SECOND_PICS = [pic_dow, pic_somalia, pic_bridge, pic_riyadh, pic_cyclone,
               pic_seoul, pic_arctic, pic_gaza, pic_gta, pic_cyber]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 16

    # masthead
    d.text((M, 8), "WORLD EDITION", font=F(SANS_B, 11), fill=RED)
    right = "41 STORIES · EVERY REGION · ALL FROM THIS ONE DAY"
    fr = F(SANS_B, 11)
    d.text((W - M - d.textlength(right, font=fr), 8), right, font=fr, fill=INK)
    d.line((M, 25, W - M, 25), fill=INK, width=2)
    title = "Thursday 19 November 2026"
    ft = F(SERIF_B, 66)
    d.text(((W - d.textlength(title, font=ft)) / 2, 26), title, font=ft, fill=INK)
    sub = "Trump, Xi and Putin share one table · The World Court finds genocide in Myanmar · Anthropic's first day on Nasdaq"
    fs = F(SERIF_I, 15)
    d.text(((W - d.textlength(sub, font=fs)) / 2, 104), sub, font=fs, fill=RED)
    d.line((M, 126, W - M, 126), fill=INK, width=1)

    # region chips, counted from the stories themselves
    counts = {r: 0 for r in REGIONS}
    for s in LEAD + SECOND:
        counts[s[4]] += 1
    for s in ALSO:
        counts[s[2]] += 1
    assert sum(counts.values()) == 41
    cw = (W - 2 * M - 6 * 4) / 7
    for i, (r, c) in enumerate(REGIONS.items()):
        x = M + i * (cw + 4)
        d.rectangle((x, 131, x + cw, 147), fill=c)
        label = f"{r} {counts[r]}"
        f = F(SANS_B, 11)
        d.text((x + (cw - d.textlength(label, font=f)) / 2, 132), label, font=f, fill=(255, 255, 255))

    # the day in numbers
    sw = (W - 2 * M) / 6
    for i, (num, label) in enumerate(STATS):
        x = M + i * sw
        if i:
            d.line((x, 152, x, 186), fill=RULE)
        d.text((x + 8, 150), num, font=F(SERIF_B, 20), fill=RED)
        d.text((x + 8, 173), label, font=F(SANS, 11), fill=GREY)
    d.line((M, 191, W - M, 191), fill=INK, width=2)

    # three lead stories
    g = 10
    lw = (W - 2 * M - 2 * g) / 3
    top, lh = 198, 232
    for i, (place, head, line, src, region) in enumerate(LEAD):
        x = M + i * (lw + g)
        d.rectangle((x, top, x + lw, top + lh), fill=CARD, outline=INK)
        LEAD_PICS[i](d, (x + 1, top + 1, x + lw - 1, top + 92))
        y = top + 98
        badge(d, x + 8, y, i + 1, REGIONS[region])
        d.text((x + 32, y + 3), place, font=F(SANS_B, 11), fill=REGIONS[region])
        y = block(d, x + 8, y + 22, head, F(SERIF_B, 20), lw - 16, INK, gap=1)
        y = block(d, x + 8, y + 3, line, F(SERIF, 12), lw - 16, GREY, gap=2, max_lines=3)
        fsrc = F(SERIF_I, 11)
        d.text((x + lw - 8 - d.textlength("— " + src, font=fsrc), top + lh - 16), "— " + src, font=fsrc, fill=GREY)

    # ten second-tier stories, two rows of five
    sw2 = (W - 2 * M - 4 * 8) / 5
    sh = 160
    for i, (place, head, line, src, region) in enumerate(SECOND):
        r, c = divmod(i, 5)
        x = M + c * (sw2 + 8)
        y0 = top + lh + 8 + r * (sh + 8)
        d.rectangle((x, y0, x + sw2, y0 + sh), fill=CARD, outline=INK)
        SECOND_PICS[i](d, (x + 1, y0 + 1, x + sw2 - 1, y0 + 62))
        y = y0 + 67
        badge(d, x + 6, y, i + 4, REGIONS[region], r=8)
        d.text((x + 26, y + 2), place, font=F(SANS_B, 10), fill=REGIONS[region])
        y = block(d, x + 6, y + 19, head, F(SERIF_B, 15), sw2 - 12, INK, gap=1, max_lines=3)
        block(d, x + 6, y + 2, f"{line} — {src}", F(SERIF_I, 11), sw2 - 12, GREY, gap=1, max_lines=2)

    # also on this day: 28 one-liners in three columns
    y = top + lh + 8 + 2 * (sh + 8) + 2
    d.text((M, y), "ALSO ON THURSDAY 19 NOVEMBER 2026", font=F(SANS_B, 12), fill=INK)
    d.line((M, y + 17, W - M, y + 17), fill=INK, width=1)
    y += 21
    cols, rows = 3, 10
    colw = (W - 2 * M - 2 * 12) / cols
    for i, (place, text, region) in enumerate(ALSO):
        c, r = divmod(i, rows)
        x = M + c * (colw + 12)
        yy = y + r * 15
        badge(d, x, yy + 1, i + 14, REGIONS[region], r=6.5)
        size = 13
        while size > 9:
            fb, fn = F(NARROW_B, size), F(NARROW, size)
            if d.textlength(place + " ", font=fb) + d.textlength(text, font=fn) <= colw - 18:
                break
            size -= 0.5
        d.text((x + 17, yy), place, font=fb, fill=INK)
        d.text((x + 17 + d.textlength(place + " ", font=fb), yy), text, font=fn, fill=INK)

    # date check and footer
    y += rows * 15 + 4
    d.rectangle((M, y, W - M, y + 40), outline=RED, width=1)
    fdc = F(SANS_B, 11)
    d.text((M + 6, y + 4), "DATE CHECK ✓", font=F("Arial Unicode.ttf", 11), fill=RED)
    note = ("Every story happened, or was first reported, on Thursday 19 November 2026. Left out as other days' news: "
            "18 Nov — Fiji's drought, the Van Gogh sale, the Senegal boat capsizing, Fed minutes, Anthropic's IPO pricing; "
            "20 Nov — Cyclone Akvan's landfall, COP31's close, the UK–EU summit.")
    block(d, M + 92, y + 4, note, F(NARROW, 12), W - 2 * M - 100, INK, gap=1, max_lines=2)
    foot = ("Claims attributed, not stated as fact · Pictures drawn in code · Sources: AP, Reuters, AFP, BBC, Bloomberg, CNN, "
            "NYT, FT, CFR, RFE/RL, Just Security, Foreign Exchanges, Kyiv Independent, UNICEF, IAEA, Yonhap")
    ff = F(NARROW, 11)
    d.text(((W - d.textlength(foot, font=ff)) / 2, y + 45), foot, font=ff, fill=GREY)
    print("bottom of page at", y + 60)

    out = ROOT / "entry.png"
    img.save(out, optimize=True)
    print(out, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
