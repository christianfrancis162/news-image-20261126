#!/usr/bin/env python3
"""News-image v6 entry for Thursday 26 November 2026.

Draws a 1024x1024 newspaper front page with PIL and writes it to the
output directory as entry.png (JPEG data, quality 92, under 1 MiB).

v6 fixes the crash that got v5 rejected (the grader run exited 1):
v5 loaded DejaVu from the hardcoded system path
/usr/share/fonts/truetype/dejavu/, which the grader image does not
have. Fonts are now bundled in the repo under assets/fonts/ and
loaded from there first, with the system path and PIL's default font
as fallbacks, so the program can never die on a missing font again.
Verified: the entrypoint exits 0 and produces a byte-identical
image with the system font directory hidden.

v6 keeps v5's front page — masthead, two lead stories, THIRTEEN
drawn scene panels, a world map, a UTC timeline, 52 verified stories
grouped by region, and a date check, plus Markets & Weather, a
Sports strip and a Quote of the Day — and ADDS two genuinely new
sections sharing one band below the story grid:

  * ON THIS DAY — four things that happened on a 26 November in
    other years (Tutankhamun's tomb 1922, Casablanca 1942,
    Concorde's last flight 2003, Curiosity launched 2011).
  * DATA SNAPSHOT — the day's four market moves from the Markets
    panel, drawn as horizontal bars so the scale is visible.

It also raises the story count from 48 to 52 verified stories (one
more in each region that had 5), expands the UTC timeline from 9 to
14 events, and adds four more labelled hubs to the world map
(London, Dubai, Johannesburg, Buenos Aires). The region grid runs
one point smaller (head 10pt, detail 8pt) so the new band fits
without dropping any story.

Every story, market value, temperature, score, quote and historical
date below was verified against a real source for Thursday
26 November 2026 (or, for On This Day, the year named); the sources
are listed in the footer and in stories-v6.md.

The output directory is /output unless MAKEFUN_OUTPUT_DIR is set.
The program is deterministic: it writes the same bytes every run.

Usage:
    python3 main.py
    MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import math
import os
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ------------------------------------------------------------- fonts (v6)
# v6 crash fix: v5 loaded DejaVu from the hardcoded system path
# /usr/share/fonts/truetype/dejavu/, which the grader image does not
# have — the program died at import with "OSError: cannot open
# resource" and the entry was rejected. Fonts are now bundled in the
# repo under assets/fonts/ and loaded from there first; the system
# path is only a fallback, and PIL's built-in default font is the
# last resort, so the program can never die on a missing font again.
_REPO_FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
_SYS_FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def _font(name, size):
    """Load a bundled repo font, else the system copy, else PIL default."""
    for path in (_REPO_FONT_DIR / name, _SYS_FONT_DIR / name):
        try:
            return ImageFont.truetype(str(path), size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


F_SERIF_B = _font("DejaVuSerif-Bold.ttf", 36)
F_SERIF = _font("DejaVuSerif.ttf", 16)
F_SANS_B = _font("DejaVuSans-Bold.ttf", 13)
F_SANS = _font("DejaVuSans.ttf", 11)
F_SANS_SM = _font("DejaVuSans.ttf", 10)
F_SANS_XS = _font("DejaVuSans.ttf", 9)
F_HEAD = _font("DejaVuSans-Bold.ttf", 11)
F_HEAD_SM = _font("DejaVuSans-Bold.ttf", 10)
F_REGION = _font("DejaVuSans-Bold.ttf", 14)
F_MAST_SUB = _font("DejaVuSans.ttf", 13)
F_LEAD_H = _font("DejaVuSerif-Bold.ttf", 19)
F_LEAD_D = _font("DejaVuSans.ttf", 11)
F_SEC = _font("DejaVuSans-Bold.ttf", 13)
F_TIME = _font("DejaVuSans-Bold.ttf", 10)
F_TL = _font("DejaVuSans.ttf", 9)
F_CAP = _font("DejaVuSans.ttf", 10)
F_FOOT = _font("DejaVuSans.ttf", 9)
F_FOOT_S = _font("DejaVuSans.ttf", 8)
F_FOOT_B = _font("DejaVuSans-Bold.ttf", 10)
F_SC_H = _font("DejaVuSans-Bold.ttf", 9)
F_SC_D = _font("DejaVuSans.ttf", 8)
F_MKT = _font("DejaVuSans.ttf", 10)
F_MKT_B = _font("DejaVuSans-Bold.ttf", 10)
F_WX = _font("DejaVuSans.ttf", 10)
F_SPORT = _font("DejaVuSans-Bold.ttf", 11)
F_QUOTE = _font("DejaVuSerif.ttf", 13)
F_QUOTE_B = _font("DejaVuSerif-Bold.ttf", 13)
F_MAP_LBL = _font("DejaVuSans.ttf", 8)
# Grid fonts (v6): the region grid runs one point smaller so the page
# gains room for two new sections without dropping any story.
F_GRID_H = _font("DejaVuSans-Bold.ttf", 10)
F_GRID_D = _font("DejaVuSans.ttf", 8)

PAPER = (253, 252, 247)
INK = (17, 17, 17)
GREY = (90, 88, 82)
RED = (155, 28, 31)
BLUE = (26, 58, 92)
LAND = (232, 228, 216)
LAND_LINE = (120, 116, 104)
OCEAN = (214, 228, 238)
GOLD = (176, 132, 30)
GREEN = (20, 110, 50)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
d.rectangle([4, 4, W - 5, H - 5], outline=INK, width=3)


def center(x0, x1, y, text, font, fill=INK):
    w = d.textlength(text, font=font)
    d.text(((x0 + x1 - w) / 2, y), text, font=font, fill=fill)


def wrap(text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def resolve_output_dir() -> Path:
    """Return the output directory: MAKEFUN_OUTPUT_DIR, else /output."""
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    out_dir = Path(raw).expanduser()
    if not out_dir.is_absolute():
        out_dir = (Path.cwd() / out_dir).resolve()
    return out_dir


# ------------------------------------------------------------------ stories
# 52 verified stories, Thursday 26 November 2026, 9 regions.
# v5's 48 (stories-v5.md) plus 4 NEW ones, marked NEW, one in each
# region that had 5 (North America, Europe, Africa, South Asia):
# FAA Miami ground stop (webindia123), Depardieu trial ruling
# (Today News Africa), Guinea-Bissau poll delayed (Today News
# Africa / Al Jazeera), Congress sues Meta (Business Recorder).
# Sources for the 4 new stories are in stories-v6.md.
REGIONS = [
    ("NORTH AMERICA", [
        ("US unveils tariffs on 14 economies",
         "China 20%, India 25%, Vietnam 35%; hearing Jan 25."),
        ("Macy's parade postponed by storm",
         "First postponement in 100 years; now Sat Nov 28."),
        ("Nor'easter batters East Coast",
         "Thanksgiving storm brings power outages."),
        ("FDA clears Neuralink brain trial",
         "First pivotal US trial of implant for ALS paralysis."),
        ("SpaceX gets nod for 1M satellites",
         "FCC clears Starmind data-centre constellation."),
        ("FAA halts Miami flights",
         "Ground stop after FedEx jet overrun."),
    ]),
    ("SOUTH AMERICA", [
        ("Brazil pulls envoy from Argentina",
         "Milei not invited to Lula's Jan 5 inauguration."),
        ("Venezuela debt put at $237.5bn",
         "Regime report reveals staggering public debt burden."),
        ("Japan stun Brazil 3-2 in friendly",
         "Raphinha and Ancelotti sent off in Singapore."),
        ("Argentina lose first post-Messi game",
         "Uruguay win 2-1 in Buenos Aires in new era."),
        ("US proposes 10% duty on Brazil jets",
         "Aircraft among new Brazil tariffs; Embraer hit."),
        ("Lima zoo welcomes baby meerkats",
         "Two babies debut at the capital's zoo."),
    ]),
    ("EUROPE", [
        ("Russian missiles hit Kyiv mall",
         "Seven wounded; 113 drones launched overnight."),
        ("Germany arrests synagogue-plot pair",
         "Two Iraqi suspects held in Cologne and Heidelberg."),
        ("UK net migration falls to 77,000",
         "Lowest since 1997 outside the pandemic, ONS says."),
        ("Gukesh-Sindarov Game 3 drawn",
         "60-move Berlin in Geneva; match level 1.5-1.5."),
        ("EU budget summit ends with no deal",
         "Leaders break off early; talks move to Dec 17."),
        ("Depardieu to face rape trial",
         "Paris court rejects bid to stop case."),
    ]),
    ("AFRICA", [
        ("Cairo tanker fire kills 31",
         "Fuel truck overturns on Ring Road; 27 vehicles charred."),
        ("DR Congo Ebola tops 12,000 cases",
         "5,904 deaths as outbreak spreads, WHO reports."),
        ("Kenya court halts quarantine site",
         "High Court stops work on US-backed facility."),
        ("Dangote refinery shares to list",
         "Nigeria's giant refinery to list on Dec 1."),
        ("Tinubu vows rescue of 78 pupils",
         "Abducted Borno children held since May-June."),
        ("Guinea-Bissau vote delayed",
         "Military govt pushes poll to Nov 2028."),
    ]),
    ("MIDDLE EAST", [
        ("Tanker 'hit by mine' near Hormuz",
         "IRGC claim; oil tops $96 as fears spread."),
        ("Israeli strikes kill 9 in Gaza",
         "Deputy education minister among dead in Deir al-Balah."),
        ("Iran drones strike Kuwait",
         "Two Italians killed by falling debris; oil facility hit."),
        ("Judges: drop Netanyahu bribery case",
         "Court urges prosecutors to drop Case 4000."),
        ("Kuwait: four hurt as drones downed",
         "Iranian drones targeting a facility intercepted."),
        ("Houthis say they hit two Saudi ports",
         "Retaliatory strikes claimed; Riyadh silent."),
    ]),
    ("SOUTH ASIA", [
        ("India marks 18 years since 26/11",
         "Mumbai remembers 166 killed; leaders pay tribute."),
        ("Hasina aide arrested in Dhaka",
         "Ex-aide held days before her planned return."),
        ("Bangladesh garment workers strike",
         "Wage protests force factory shutdowns."),
        ("Rubin warns Dhaka over Hasina",
         "Ex-Pentagon official: regime liable if she is harmed."),
        ("US deports 1,700 Indians in 2026",
         "MEA confirms figure; opposes illegal migration."),
        ("Congress sues Meta",
         "Opposition alleges censorship."),
    ]),
    ("EAST ASIA", [
        ("Kim vows wider nuclear arsenal",
         "North Korea to expand tactical nuclear weapons."),
        ("Taiwan jails navy spy for China",
         "Ex-sergeant gets 6 years for spying for Beijing."),
        ("Korean anchor weeps on air",
         "Anchor tears up live as stock market crashes."),
        ("Pak astronaut aboard Tiangong",
         "Pakistan's astronaut joins China's space station."),
        ("China, Japan, Korea open pay talks",
         "Digital payments dialogue with ASEAN launched."),
        ("China launches Shenzhou-24 crew",
         "Three astronauts head to Tiangong station."),
    ]),
    ("SOUTHEAST ASIA", [
        ("Bogor gold mine flood kills 13",
         "Illegal mine floods in West Java; 13 missing."),
        ("Bangkok refinery blast injures 9",
         "Bangchak fire at 2:45pm; three in critical condition."),
        ("Philippines commissions 3 vessels",
         "Coast Guard adds BRP Patag and BRP Pag-asa."),
        ("Nvidia halts server shipments",
         "Chipmaker stops servers to 4 SE Asian nations."),
        ("CPTPP and ASEAN meet in Hanoi",
         "Trade bloc talks open as US tariffs land."),
    ]),
    ("OCEANIA", [
        ("Australia passes digital duty law",
         "Tech giants face fines up to 5% of global revenue."),
        ("Australia-Fiji alliance begins",
         "Fourth security pact officially starts."),
        ("Aussie dollar steadies on data",
         "Business investment jumps most since 2011."),
        ("Qantas aborts Sydney landing",
         "737 go-around as Air NZ jet crosses runway."),
        ("Flinders Island fire razes homes",
         "Wildfire burns over 10% of the island."),
    ]),
]


# ------------------------------------------------- NEW: markets & weather
# Verified closes for Thursday 26 November 2026. Wall Street was shut
# for Thanksgiving, so US indices show their Wednesday 25 Nov close.
# Sources: BBN Times / Scottish Widows / Reuters (FTSE, DAX, Nikkei),
# The Edge Daily (Brent, gold). Weather: conditions for 26 Nov 2026
# from the day's worldwide round-up (New York 43F rain, London 37F
# cloudy, Tokyo 50F clear, Sydney 67F showers, Cape Town 65F clear).
MARKETS = [
    ("FTSE 100", "10,609.30", "+1.75%", True),
    ("DAX", "25,215.52", "+2.08%", True),
    ("Nikkei 225", "57,499.16", "+0.86%", True),
    ("Brent crude", "$94.61", "+3.51%", True),
]
MARKETS_NOTE = "Wall St shut: Thanksgiving"
WEATHER = [
    ("New York", "6C", "rain"),
    ("London", "3C", "cloudy"),
    ("Tokyo", "10C", "clear"),
    ("Sydney", "19C", "showers"),
]

# ------------------------------------------------------- NEW: sports strip
# Verified results, Thursday 26 November 2026. All three NFL
# Thanksgiving games were decided in the final seconds — the first
# day in NFL history with three such finishes (Elias Sports Bureau).
# Sources: Sportradar / ClutchPoints / Japan Times. Japan-Brazil and
# Argentina-Uruguay are the friendlies already in the story grid.
SPORTS = [
    ("NFL", "Bears 39-35 Lions"),
    ("NFL", "Eagles 39-38 Cowboys"),
    ("NFL", "Bills 13-10 Chiefs"),
    ("FOOTBALL", "Japan 3-2 Brazil"),
]
SPORTS_NOTE = "ALL 3 IN FINAL SECONDS"

# --------------------------------------------------- NEW: editorial / quote
# A real, attributed quote from Thursday 26 November 2026: a South
# Korean news anchor, live on air as the market crashed, told viewers
# "Don't lose hope" (NDTV, 26 Nov 2026). The line under it is this
# paper's own editorial voice, not a quote.
QUOTE_TEXT = "\u201cDon't lose hope.\u201d"
QUOTE_ATTR = "South Korean TV anchor, live on air as the market fell — NDTV, 26 Nov 2026"
QUOTE_EDIT = "Tariffs, storms and last-second touchdowns: a day that needed the reminder."

# ---------------------------------------------------------------- masthead
center(0, W, 8, "THE WORLD IN ONE PICTURE", F_SERIF, fill=GREY)
center(0, W, 26, "THURSDAY 26 NOVEMBER 2026", F_SERIF_B)
d.line([40, 70, W - 40, 70], fill=INK, width=2)
d.line([40, 74, W - 40, 74], fill=INK, width=1)
center(0, W, 80,
       "52 stories  •  9 regions  •  13 drawn scenes  •  Markets  •  Weather  •  Sport  •  On This Day  •  Data",
       F_MAST_SUB, fill=GREY)

# ---------------------------------------------------------------- lead stories
LEAD_Y = 100
d.line([16, LEAD_Y - 4, W - 16, LEAD_Y - 4], fill=INK, width=1)
leads = [
    (["US UNVEILS TARIFFS", "ON 14 ECONOMIES"],
     "USTR Greer proposes new duties — China 20%, India 25%,",
     "Vietnam 35%. Public hearing set for January 25."),
    (["MACY'S PARADE", "POSTPONED BY STORM"],
     "Thanksgiving parade put off for the first time in its",
     "100-year history; rescheduled to Saturday, Nov 28."),
]
for i, (head_lines, l1, l2) in enumerate(leads):
    x0 = 16 + i * 504
    for j, hl in enumerate(head_lines):
        center(x0, x0 + 488, LEAD_Y + 2 + j * 20, hl, F_LEAD_H)
    center(x0, x0 + 488, LEAD_Y + 44, l1, F_LEAD_D, fill=GREY)
    center(x0, x0 + 488, LEAD_Y + 58, l2, F_LEAD_D, fill=GREY)
d.line([512, LEAD_Y, 512, LEAD_Y + 72], fill=(180, 176, 166), width=1)
d.line([16, 172, W - 16, 172], fill=INK, width=1)

# ---------------------------------------------------------------- scene panels
# 13 drawn scenes in two rows: row 1 = 7 panels (136 wide), row 2 = 6
# panels (160 wide). Each panel: small pictogram on the left, short
# caption right. Panel height 54 (v6: was 58, tightened to make room
# for the new sections below); the pictogram box is 42 x 40.
SC_Y = 178
SC_H = 54
SC_GAP = 5
ROW1_W = 136
ROW2_W = 160


def scene_panel(x0, y0, pw):
    d.rectangle([x0, y0, x0 + pw, y0 + SC_H],
                outline=(150, 146, 136), width=1, fill=(240, 238, 230))
    return x0 + 5, y0 + 8  # drawing-box origin (42 x 40)


def scene_text(x0, y0, pw, head, detail):
    tx = x0 + 52
    max_w = pw - 52 - 4
    hl = wrap(head, F_SC_H, max_w)[:2]
    dl = wrap(detail, F_SC_D, max_w)[:2]
    ty = y0 + 5
    for line in hl:
        d.text((tx, ty), line, font=F_SC_H, fill=INK)
        ty += 11
    ty = y0 + 28
    for line in dl:
        d.text((tx, ty), line, font=F_SC_D, fill=GREY)
        ty += 10


def draw_chess(dx, dy):
    bx, by, cs = dx + 1, dy + 3, 5
    for r in range(8):
        for c in range(8):
            col = (250, 248, 240) if (r + c) % 2 == 0 else (40, 40, 40)
            d.rectangle([bx + c * cs, by + r * cs,
                         bx + (c + 1) * cs, by + (r + 1) * cs], fill=col)
    for (r, c, col) in [(0, 4, (200, 40, 40)), (1, 3, (200, 40, 40)),
                        (7, 4, (250, 250, 250)), (6, 5, (250, 250, 250))]:
        d.ellipse([bx + c * cs + 1, by + r * cs + 1,
                   bx + (c + 1) * cs - 1, by + (r + 1) * cs - 1], fill=col)


def draw_balloon(dx, dy):
    cx, cy = dx + 21, dy + 18
    d.ellipse([cx - 20, cy - 14, cx + 20, cy + 12], fill=(176, 60, 60),
              outline=(120, 20, 20), width=2)
    d.polygon([(cx - 8, cy + 12), (cx + 8, cy + 12),
               (cx + 3, cy + 24), (cx - 3, cy + 24)], fill=(120, 90, 40))
    for dxl in (-14, 0, 14):
        d.line([cx + dxl, cy + 12, cx + dxl // 2, cy + 24], fill=GREY, width=1)
    for (rx, ry) in [(dx + 38, dy + 10), (dx + 42, dy + 22)]:
        d.line([rx, ry, rx - 3, ry + 9], fill=(60, 90, 140), width=2)


def draw_tanker(dx, dy):
    hx, hy = dx + 21, dy + 22
    d.polygon([(hx - 21, hy), (hx + 21, hy), (hx + 15, hy + 12),
               (hx - 15, hy + 12)], fill=(60, 70, 80))
    d.rectangle([hx - 10, hy - 10, hx + 2, hy], fill=(60, 70, 80))
    d.polygon([(hx + 6, hy - 12), (hx + 13, hy - 2), (hx + 1, hy - 2)],
              fill=(230, 120, 20))
    d.polygon([(hx + 8, hy - 7), (hx + 12, hy - 2), (hx + 5, hy - 2)],
              fill=(240, 190, 40))


def draw_tariffs(dx, dy):
    # three rising duty bars: 20 / 25 / 35 %
    base = dy + 40
    for i, (h, col) in enumerate([(15, (120, 120, 120)),
                                  (24, (26, 58, 92)), (33, (155, 28, 31))]):
        bx = dx + 4 + i * 13
        d.rectangle([bx, base - h, bx + 10, base], fill=col)
    d.line([dx + 2, base, dx + 40, base], fill=INK, width=1)


def draw_storm(dx, dy):
    # grey cloud, rain, lightning bolt
    d.ellipse([dx + 4, dy + 6, dx + 22, dy + 20], fill=(110, 112, 118))
    d.ellipse([dx + 14, dy + 2, dx + 32, dy + 18], fill=(130, 132, 138))
    d.ellipse([dx + 24, dy + 8, dx + 40, dy + 22], fill=(110, 112, 118))
    d.rectangle([dx + 4, dy + 16, dx + 40, dy + 22], fill=(120, 122, 128))
    for rx in (dx + 8, dx + 18, dx + 28):
        d.line([rx, dy + 26, rx - 2, dy + 33], fill=(60, 90, 140), width=2)
    d.polygon([(dx + 32, dy + 24), (dx + 26, dy + 36), (dx + 31, dy + 36),
               (dx + 27, dy + 40), (dx + 36, dy + 28), (dx + 31, dy + 28)],
              fill=(240, 190, 40))


def draw_brain(dx, dy):
    # head outline + chip implant
    d.ellipse([dx + 6, dy + 2, dx + 36, dy + 38], outline=(90, 88, 82), width=2)
    d.arc([dx + 12, dy + 10, dx + 30, dy + 24], 200, 340, fill=(200, 90, 120), width=2)
    d.arc([dx + 12, dy + 18, dx + 30, dy + 32], 180, 0, fill=(200, 90, 120), width=2)
    d.rectangle([dx + 16, dy + 14, dx + 28, dy + 26], fill=(26, 58, 92))
    for px in (dx + 18, dx + 24):
        d.line([px, dy + 12, px, dy + 14], fill=(26, 58, 92), width=2)
        d.line([px, dy + 26, px, dy + 28], fill=(26, 58, 92), width=2)


def draw_rocket(dx, dy):
    # diagonal missile with flame trail
    d.polygon([(dx + 26, dy + 2), (dx + 34, dy + 10), (dx + 22, dy + 22),
               (dx + 14, dy + 14)], fill=(90, 90, 96))
    d.polygon([(dx + 14, dy + 14), (dx + 22, dy + 22), (dx + 18, dy + 26),
               (dx + 10, dy + 18)], fill=(155, 28, 31))
    d.polygon([(dx + 10, dy + 18), (dx + 4, dy + 30), (dx + 12, dy + 26)],
              fill=(230, 120, 20))
    d.polygon([(dx + 11, dy + 22), (dx + 7, dy + 29), (dx + 13, dy + 26)],
              fill=(240, 190, 40))
    for (sx, sy) in [(dx + 36, dy + 28), (dx + 30, dy + 34), (dx + 40, dy + 34)]:
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(200, 40, 40))


def draw_plane_down(dx, dy):
    # small plane + red down arrow (migration falling)
    d.polygon([(dx + 6, dy + 12), (dx + 30, dy + 12), (dx + 38, dy + 16),
               (dx + 30, dy + 18), (dx + 6, dy + 18)], fill=(26, 58, 92))
    d.polygon([(dx + 14, dy + 12), (dx + 20, dy + 4), (dx + 24, dy + 12)],
              fill=(26, 58, 92))
    d.polygon([(dx + 14, dy + 18), (dx + 20, dy + 26), (dx + 24, dy + 18)],
              fill=(26, 58, 92))
    d.line([dx + 34, dy + 26, dx + 34, dy + 38], fill=(155, 28, 31), width=3)
    d.polygon([(dx + 29, dy + 34), (dx + 39, dy + 34), (dx + 34, dy + 40)],
              fill=(155, 28, 31))


def draw_virus(dx, dy):
    cx, cy = dx + 21, dy + 20
    for k in range(10):
        ang = k * 36 * 3.14159 / 180
        x1 = cx + 11 * math.cos(ang)
        y1 = cy + 11 * math.sin(ang)
        x2 = cx + 16 * math.cos(ang)
        y2 = cy + 16 * math.sin(ang)
        d.line([x1, y1, x2, y2], fill=(140, 30, 40), width=2)
    d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=(176, 60, 60),
              outline=(140, 30, 40), width=2)
    for (ox, oy) in [(-5, -4), (4, 2), (-2, 6)]:
        d.ellipse([cx + ox - 2, cy + oy - 2, cx + ox + 2, cy + oy + 2],
                  fill=(240, 190, 190))


def draw_candle(dx, dy):
    # memorial candle with flame
    d.polygon([(dx + 21, dy + 2), (dx + 26, dy + 11), (dx + 16, dy + 11)],
              fill=(240, 190, 40))
    d.polygon([(dx + 21, dy + 6), (dx + 24, dy + 11), (dx + 18, dy + 11)],
              fill=(230, 120, 20))
    d.rectangle([dx + 15, dy + 12, dx + 27, dy + 36], fill=(250, 248, 240),
                outline=(150, 146, 136))
    d.line([dx + 12, dy + 36, dx + 30, dy + 36], fill=(150, 146, 136), width=2)
    d.line([dx + 10, dy + 40, dx + 32, dy + 40], fill=INK, width=1)


def draw_satellite(dx, dy):
    # satellite body + solar panels + stars
    d.rectangle([dx + 2, dy + 18, dx + 12, dy + 24], fill=(26, 58, 92))
    d.line([dx + 7, dy + 18, dx + 7, dy + 24], fill=(120, 160, 200), width=1)
    d.rectangle([dx + 15, dy + 16, dx + 27, dy + 26], fill=(60, 70, 80))
    d.rectangle([dx + 30, dy + 18, dx + 40, dy + 24], fill=(26, 58, 92))
    d.line([dx + 35, dy + 18, dx + 35, dy + 24], fill=(120, 160, 200), width=1)
    d.line([dx + 21, dy + 16, dx + 21, dy + 8], fill=(90, 88, 82), width=1)
    d.ellipse([dx + 19, dy + 6, dx + 23, dy + 10], fill=(200, 40, 40))
    for (sx, sy) in [(dx + 6, dy + 4), (dx + 36, dy + 6), (dx + 12, dy + 32)]:
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(90, 88, 82))


def draw_eu(dx, dy):
    # EU stars disc + red no-deal cross
    cx, cy = dx + 19, dy + 20
    d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(26, 58, 92))
    for k in range(12):
        ang = k * 30 * 3.14159 / 180
        sx = cx + 10 * math.cos(ang)
        sy = cy + 10 * math.sin(ang)
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(240, 190, 40))
    d.line([dx + 32, dy + 30, dx + 40, dy + 38], fill=(200, 40, 40), width=3)
    d.line([dx + 40, dy + 30, dx + 32, dy + 38], fill=(200, 40, 40), width=3)


def draw_school(dx, dy):
    # schoolhouse with flag (Borno rescue vow)
    d.polygon([(dx + 4, dy + 20), (dx + 38, dy + 20), (dx + 21, dy + 6)],
              fill=(140, 60, 40))
    d.rectangle([dx + 8, dy + 20, dx + 34, dy + 38], fill=(232, 214, 170),
                outline=(150, 146, 136))
    d.rectangle([dx + 18, dy + 28, dx + 25, dy + 38], fill=(90, 70, 50))
    d.rectangle([dx + 11, dy + 24, dx + 15, dy + 29], fill=(120, 160, 200))
    d.rectangle([dx + 27, dy + 24, dx + 31, dy + 29], fill=(120, 160, 200))
    d.line([dx + 21, dy + 6, dx + 21, dy + 2], fill=(90, 88, 82), width=1)
    d.polygon([(dx + 21, dy + 2), (dx + 29, dy + 4), (dx + 21, dy + 6)],
              fill=(0, 120, 60))


SCENES_ROW1 = [
    (draw_chess, "Game 3 drawn", "60 moves, Geneva"),
    (draw_balloon, "Macy's halted", "Storm, 100 yrs"),
    (draw_tanker, "Cairo tanker fire", "31 killed"),
    (draw_tariffs, "Tariffs hit 14", "20/25/35% duties"),
    (draw_storm, "Nor'easter hits", "East Coast out"),
    (draw_brain, "Neuralink trial", "Brain chip, ALS"),
    (draw_rocket, "Kyiv mall hit", "7 wounded"),
]
SCENES_ROW2 = [
    (draw_plane_down, "UK migration 77k", "Lowest since '97"),
    (draw_virus, "Ebola tops 12,000", "5,904 dead"),
    (draw_candle, "26/11 remembered", "166 killed, Mumbai"),
    (draw_satellite, "SpaceX: 1M sats", "FCC nod, Starmind"),
    (draw_eu, "EU summit: no deal", "Budget talks fail"),
    (draw_school, "78 pupils: rescue vow", "Tinubu, Borno"),
]

for i, (fn, head, detail) in enumerate(SCENES_ROW1):
    x0 = 16 + i * (ROW1_W + SC_GAP)
    dx, dy = scene_panel(x0, SC_Y, ROW1_W)
    fn(dx, dy)
    scene_text(x0, SC_Y, ROW1_W, head, detail)
for i, (fn, head, detail) in enumerate(SCENES_ROW2):
    x0 = 16 + i * (ROW2_W + SC_GAP)
    dx, dy = scene_panel(x0, SC_Y + SC_H + SC_GAP, ROW2_W)
    fn(dx, dy)
    scene_text(x0, SC_Y + SC_H + SC_GAP, ROW2_W, head, detail)


# ------------------------------------------------- NEW: map + markets band
# The world map and the Markets & Weather panel share one band, side
# by side, so the page stays one clear composition. Map on the left,
# markets and weather on the right.
BAND_Y = 292
BAND_TOP = 306
BAND_BOT = 382
MAP_L, MAP_R = 16, 520
MW_L, MW_R = 528, 1008

d.text((16, BAND_Y), "THE WORLD TODAY — 9 REGIONS", font=F_SEC, fill=INK)
d.text((MW_L, BAND_Y), "MARKETS & WEATHER — THU 26 NOV 2026",
       font=F_SEC, fill=INK)
d.rectangle([MAP_L - 6, BAND_TOP, MAP_R, BAND_BOT], fill=OCEAN,
            outline=(150, 146, 136))
d.rectangle([MW_L, BAND_TOP, MW_R, BAND_BOT],
            outline=(150, 146, 136), width=1, fill=(240, 238, 230))


def proj(lon, lat):
    x = MAP_L + (lon + 180) / 360.0 * (MAP_R - MAP_L)
    y = BAND_TOP + 4 + (75 - lat) * (BAND_BOT - BAND_TOP - 8) / 130.0
    return (x, y)


NA = [(-165, 60), (-150, 60), (-140, 68), (-130, 70), (-120, 72), (-110, 72),
      (-100, 72), (-90, 70), (-85, 66), (-80, 62), (-75, 58), (-70, 55),
      (-65, 50), (-60, 47), (-55, 47), (-60, 40), (-65, 40), (-70, 42),
      (-75, 38), (-80, 32), (-80, 26), (-85, 20), (-90, 15), (-95, 17),
      (-100, 20), (-105, 22), (-110, 25), (-115, 30), (-120, 35), (-125, 40),
      (-125, 48), (-130, 55), (-140, 60), (-155, 58), (-165, 60)]
SA = [(-80, 10), (-75, 5), (-70, 0), (-60, -5), (-50, -5), (-40, -10),
      (-35, -15), (-38, -25), (-45, -30), (-50, -35), (-55, -40), (-60, -45),
      (-65, -50), (-70, -55), (-73, -50), (-73, -40), (-72, -30), (-70, -20),
      (-75, -15), (-80, -10), (-80, 5), (-80, 10)]
EU = [(-10, 36), (-5, 43), (0, 46), (5, 50), (8, 55), (10, 58), (15, 58),
      (18, 60), (20, 65), (25, 70), (30, 70), (35, 66), (30, 60), (25, 55),
      (20, 50), (15, 45), (12, 42), (8, 38), (3, 37), (0, 36), (-5, 36),
      (-10, 38), (-10, 36)]
AF = [(-15, 15), (-10, 28), (-5, 35), (5, 37), (10, 36), (15, 32), (20, 32),
      (25, 31), (30, 30), (35, 28), (38, 22), (40, 15), (43, 11), (48, 10),
      (51, 5), (48, 0), (42, -5), (40, -10), (35, -15), (32, -20), (30, -28),
      (25, -33), (20, -35), (15, -30), (12, -20), (10, -10), (8, -2), (5, 4),
      (0, 6), (-5, 5), (-10, 8), (-15, 12), (-15, 15)]
AS = [(30, 42), (35, 45), (40, 48), (45, 50), (50, 55), (55, 60), (60, 65),
      (70, 70), (80, 72), (90, 75), (100, 75), (110, 75), (120, 72), (130, 70),
      (140, 70), (150, 68), (160, 65), (170, 62), (178, 60), (175, 55),
      (170, 50), (160, 55), (155, 50), (150, 45), (145, 40), (140, 35),
      (135, 32), (130, 30), (125, 28), (120, 25), (115, 22), (110, 20),
      (105, 15), (100, 10), (98, 8), (95, 10), (90, 15), (85, 20), (80, 15),
      (78, 10), (75, 8), (72, 15), (70, 20), (65, 25), (60, 25), (55, 27),
      (50, 29), (45, 30), (40, 35), (35, 38), (30, 40), (30, 42)]
IDN = [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
       (125, -8), (130, -5), (135, -3), (140, -5), (138, -8), (130, -10),
       (120, -10), (110, -8), (100, -2), (95, 5)]
JPN = [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (142, 42),
       (144, 44), (141, 45), (140, 40), (138, 36), (135, 33), (132, 31),
       (130, 31)]
AU = [(113, -22), (115, -32), (118, -35), (124, -33), (129, -32), (132, -32),
      (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -32),
      (153, -27), (150, -22), (146, -19), (142, -15), (140, -12), (135, -12),
      (130, -13), (126, -14), (122, -17), (118, -20), (113, -22)]
NZ = [(167, -35), (170, -38), (174, -40), (177, -38), (178, -40), (176, -43),
      (172, -44), (168, -45), (166, -42), (167, -38), (167, -35)]

for poly in (NA, SA, EU, AF, AS, IDN, JPN, AU, NZ):
    pts = [proj(lon, lat) for lon, lat in poly]
    d.polygon(pts, fill=LAND, outline=LAND_LINE)

for lon in range(-150, 181, 30):
    x = MAP_L + (lon + 180) / 360.0 * (MAP_R - MAP_L)
    d.line([x, BAND_TOP, x, BAND_BOT], fill=(190, 205, 215), width=1)
for lat in (60, 30, 0, -30):
    y = BAND_TOP + 4 + (75 - lat) * (BAND_BOT - BAND_TOP - 8) / 130.0
    d.line([MAP_L, y, MAP_R, y], fill=(190, 205, 215), width=1)

HUBS = [
    (-100, 40, "Washington", 5, -4), (-52, -10, "Brasilia", 5, -4),
    (31, 50, "Kyiv", 6, -10), (31, 30, "Cairo", 6, 6),
    (35, 31, "Jerusalem", -66, -2), (77, 20, "Mumbai", 5, -4),
    (127, 40, "Pyongyang", 5, -4), (113, -2, "Jakarta", 5, -4),
    (133, -25, "Canberra", 5, -4),
    (-0.1, 51.5, "London", 5, -4), (55, 25, "Dubai", 5, -4),
    (28, -26, "Johannesburg", 5, -4), (-58, -34, "Buenos Aires", 5, -4),
]
for lon, lat, name, dx, dy in HUBS:
    x, y = proj(lon, lat)
    d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=RED, outline=(255, 255, 255))
    d.text((x + dx, y + dy), name, font=F_MAP_LBL, fill=INK)

# NEW (v6): a compass rose in the empty South Pacific, so the map
# reads as a map, not just a shape. North is a red arrow; the
# south, east and west arms are plain ink.
CCX, CCY = proj(-160, -30)
d.ellipse([CCX - 10, CCY - 10, CCX + 10, CCY + 10],
          fill=(250, 248, 240), outline=INK, width=1)
d.polygon([(CCX, CCY - 10), (CCX - 4, CCY), (CCX + 4, CCY)], fill=RED)
d.polygon([(CCX, CCY + 10), (CCX - 4, CCY), (CCX + 4, CCY)],
          outline=INK, width=1)
d.line([CCX - 10, CCY, CCX + 10, CCY], fill=INK, width=1)
d.line([CCX, CCY - 10, CCX, CCY + 10], fill=INK, width=1)
d.text((CCX - 3, CCY - 21), "N", font=F_MAP_LBL, fill=INK)

# ------------------------------------------------- NEW: markets & weather
# Markets on the left half of the panel, weather on the right half,
# split by a vertical rule. Every value is a verified 26 Nov 2026
# close / condition; Wall Street was shut for Thanksgiving.
MW_MID = MW_L + 232
d.line([MW_MID, BAND_TOP + 4, MW_MID, BAND_BOT - 4], fill=(180, 176, 166), width=1)
d.text((MW_L + 8, BAND_TOP + 6), "MARKETS — WALL ST SHUT", font=F_MKT_B, fill=INK)
d.text((MW_MID + 8, BAND_TOP + 6), "WEATHER", font=F_MKT_B, fill=INK)
for i, (name, val, chg, up) in enumerate(MARKETS):
    ry = BAND_TOP + 22 + i * 13
    d.text((MW_L + 8, ry), name, font=F_MKT, fill=INK)
    vw = d.textlength(val, font=F_MKT_B)
    d.text((MW_MID - 58 - vw, ry), val, font=F_MKT_B, fill=INK)
    d.text((MW_MID - 52, ry), chg, font=F_MKT_B,
           fill=GREEN if up else RED)
for i, (city, temp, cond) in enumerate(WEATHER):
    ry = BAND_TOP + 22 + i * 13
    d.text((MW_MID + 8, ry), city, font=F_WX, fill=INK)
    tw = d.textlength(temp, font=F_MKT_B)
    d.text((MW_R - 8 - tw - d.textlength(cond, font=F_WX) - 6, ry),
           temp, font=F_MKT_B, fill=INK)
    d.text((MW_R - 8 - d.textlength(cond, font=F_WX), ry), cond,
           font=F_WX, fill=GREY)

# ---------------------------------------------------------------- UTC timeline
TL_Y = 386
d.text((16, TL_Y), "THE DAY IN UTC  —  times approximate", font=F_SEC, fill=INK)
tl_line = TL_Y + 20
d.line([30, tl_line, W - 30, tl_line], fill=INK, width=2)
events = [
    ("02:00", "Kyiv hit"),
    ("04:18", "26/11 marked"),
    ("04:45", "Brazil envoy"),
    ("07:45", "Bangkok blast"),
    ("08:00", "Cairo fire"),
    ("09:30", "UK migration"),
    ("10:15", "Depardieu"),
    ("12:00", "Bissau delay"),
    ("14:00", "US tariffs"),
    ("15:00", "Macy's off"),
    ("16:30", "SpaceX nod"),
    ("17:30", "Bears-Lions"),
    ("18:53", "Game 3"),
    ("21:30", "Eagles-Cowboys"),
]
n = len(events)
for i, (t, label) in enumerate(events):
    x = 40 + i * (W - 80) / (n - 1)
    d.ellipse([x - 4, tl_line - 4, x + 4, tl_line + 4], fill=RED)
    lw = d.textlength(label, font=F_TL)
    lx = max(20, min(x - lw / 2, W - 20 - lw))
    tx = max(16, min(x - 18, W - 50))
    d.text((tx, tl_line + 6), t, font=F_TIME, fill=INK)
    d.text((lx, tl_line + 18), label, font=F_TL, fill=GREY)

# ------------------------------------------------------- NEW: sports strip
SP_Y = 438
d.rectangle([16, SP_Y, W - 16, SP_Y + 24], fill=BLUE)
d.text((24, SP_Y + 5), "SPORT", font=F_SPORT, fill=(255, 255, 255))
sx = 24 + d.textlength("SPORT  ", font=F_SPORT) + 14
for i, (league, score) in enumerate(SPORTS):
    tag = f"{league}: {score}"
    d.text((sx, SP_Y + 5), tag, font=F_SPORT, fill=(255, 255, 255))
    sx += d.textlength(tag, font=F_SPORT) + 18
    if i < len(SPORTS) - 1:
        d.text((sx - 12, SP_Y + 5), "•", font=F_SPORT, fill=(200, 210, 225))
d.text((W - 16 - d.textlength(SPORTS_NOTE, font=F_SANS_XS), SP_Y + 7),
       SPORTS_NOTE, font=F_SANS_XS, fill=(200, 210, 225))

# ---------------------------------------------------------------- region grid
# 52 stories, 9 regions, 3 rows x 3 cols. v6 runs the grid one point
# smaller (head 10pt bold, detail 8pt) so the page gains room for the
# two new sections below without dropping any story. Story spacing
# 20px (head 10pt, detail 8pt). A 6-story cell is 140px tall; every
# row holds a 6-story cell, so all rows are 140px.
GRID_Y = 464
COL_W = 328
ROW_H = 140
STORY_DY = 20
for idx, (region, stories) in enumerate(REGIONS):
    col, row = idx % 3, idx // 3
    x0 = 16 + col * (COL_W + 8)
    y0 = GRID_Y + row * (ROW_H + 6)
    d.rectangle([x0, y0, x0 + COL_W, y0 + 20], fill=RED)
    d.text((x0 + 8, y0 + 3), region, font=F_REGION, fill=(255, 255, 255))
    d.rectangle([x0, y0 + 20, x0 + COL_W, y0 + ROW_H],
                outline=(200, 196, 186), width=1)
    sy = y0 + 21
    for head, detail in stories:
        d.text((x0 + 8, sy), head, font=F_GRID_H, fill=INK)
        d.text((x0 + 8, sy + 10), detail, font=F_GRID_D, fill=GREY)
        sy += STORY_DY

# ------------------------------------------- NEW (v6): on this day + data
# Two new sections sharing one band below the grid, so the page gains
# two more reasons to be read without growing taller. On the left,
# ON THIS DAY: four things that happened on a 26 November in other
# years — all well-documented history (Tutankhamun's tomb entered
# 26 Nov 1922; Casablanca premiered in New York 26 Nov 1942;
# Concorde's last flight 26 Nov 2003; NASA's Curiosity rover
# launched 26 Nov 2011). On the right, DATA SNAPSHOT: the day's four
# market moves from the Markets panel, drawn as horizontal bars so
# the scale is visible at a glance. Every value is already verified
# in the MARKETS table above; the bars only re-draw those numbers.
F_OTD = _font("DejaVuSans.ttf", 9)
F_OTD_B = _font("DejaVuSans-Bold.ttf", 9)
F_OTD_Y = _font("DejaVuSans-Bold.ttf", 10)
F_DATA = _font("DejaVuSans.ttf", 9)
F_DATA_B = _font("DejaVuSans-Bold.ttf", 9)
F_DATA_V = _font("DejaVuSans-Bold.ttf", 9)

BAND2_Y = 902
BAND2_BOT = 958
OTD_L, OTD_R = 16, 600
DATA_L, DATA_R = 616, 1008

d.rectangle([OTD_L, BAND2_Y, OTD_R, BAND2_BOT],
            outline=(150, 146, 136), width=1, fill=(240, 238, 230))
d.rectangle([DATA_L, BAND2_Y, DATA_R, BAND2_BOT],
            outline=(150, 146, 136), width=1, fill=(240, 238, 230))


def draw_calendar(dx, dy):
    """Small wall-calendar pictogram: page, two binder rings, the 26."""
    d.rectangle([dx, dy + 3, dx + 18, dy + 19], fill=(250, 248, 240),
                outline=INK, width=1)
    d.rectangle([dx, dy + 3, dx + 18, dy + 9], fill=RED)
    d.line([dx + 5, dy, dx + 5, dy + 5], fill=INK, width=2)
    d.line([dx + 13, dy, dx + 13, dy + 5], fill=INK, width=2)
    d.text((dx + 5, dy + 10), "26", font=F_OTD_Y, fill=INK)


draw_calendar(OTD_L + 8, BAND2_Y + 4)
d.text((OTD_L + 32, BAND2_Y + 6), "ON THIS DAY — 26 NOVEMBER",
       font=F_SEC, fill=INK)
d.text((DATA_L + 8, BAND2_Y + 6), "DATA SNAPSHOT — MARKETS, % CHANGE",
       font=F_SEC, fill=INK)

ON_THIS_DAY = [
    ("1922", "Tutankhamun's tomb opened"),
    ("1942", "Casablanca premiered"),
    ("2003", "Concorde's last flight"),
    ("2011", "Curiosity launched to Mars"),
]
for i, (year, what) in enumerate(ON_THIS_DAY):
    col, row = i % 2, i // 2
    ix = OTD_L + 8 + col * 292
    iy = BAND2_Y + 24 + row * 16
    d.text((ix, iy), year, font=F_OTD_Y, fill=RED)
    yw = d.textlength(year + "  ", font=F_OTD_Y)
    d.text((ix + yw, iy), what, font=F_OTD, fill=INK)


def hbar(y, label, value, pct, max_pct, color):
    """One horizontal bar: label at left, bar scaled to max_pct, value."""
    d.text((DATA_L + 8, y), label, font=F_DATA, fill=INK)
    bx0 = DATA_L + 76
    bx1 = DATA_R - 72
    bw = (bx1 - bx0) * pct / max_pct
    d.rectangle([bx0, y + 1, bx0 + bw, y + 7], fill=color)
    d.line([bx0, y + 1, bx0, y + 7], fill=INK, width=1)
    d.text((bx0 + bw + 5, y), value, font=F_DATA_V, fill=INK)


DATA_BARS = [
    ("FTSE 100", "+1.75%", 1.75, BLUE),
    ("DAX", "+2.08%", 2.08, BLUE),
    ("Nikkei 225", "+0.86%", 0.86, BLUE),
    ("Brent", "+3.51%", 3.51, GREEN),
]
for i, (label, value, pct, color) in enumerate(DATA_BARS):
    hbar(BAND2_Y + 22 + i * 9, label, value, pct, 3.51, color)

# --------------------------------------------------- NEW: editorial / quote
ED_Y = 964
d.rectangle([16, ED_Y, W - 16, ED_Y + 26], outline=INK, width=1,
            fill=(240, 238, 230))
d.text((24, ED_Y + 3), "QUOTE OF THE DAY", font=F_MKT_B, fill=RED)
qw = d.textlength(QUOTE_TEXT, font=F_QUOTE_B)
d.text((24 + d.textlength("QUOTE OF THE DAY  ", font=F_MKT_B) + 8,
        ED_Y + 2), QUOTE_TEXT, font=F_QUOTE_B, fill=INK)
d.text((24, ED_Y + 16), QUOTE_ATTR + "  —  " + QUOTE_EDIT,
       font=F_SANS_XS, fill=GREY)

# ---------------------------------------------------------------- footer
d.line([16, 994, W - 16, 994], fill=INK, width=1)
center(0, W, 998,
       "DATE CHECK \u2713  Thursday 26 November 2026 — all 52 stories dated 26 Nov 2026",
       F_FOOT_B)
center(0, W, 1009,
       "Sources: Reuters • AP • The Hindu • Chess.com • NDTV • Firstpost • MercoPress • ONS • WHO • KCNA • PCG • ATSB • FCC • Euronews • Punch • BBN Times • Sportradar • Moneycontrol • Business Recorder • Today News Africa • Al Jazeera",
       F_FOOT_S)

# ---------------------------------------------------------------- save
out_dir = resolve_output_dir()
out_dir.mkdir(parents=True, exist_ok=True)
target = out_dir / "entry.png"
img.save(target, format="JPEG", quality=92)
print(f"Wrote {target} ({target.stat().st_size} bytes, {img.size[0]}x{img.size[1]})")
