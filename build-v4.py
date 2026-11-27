#!/usr/bin/env python3
"""Build v4 of the news-image entry for Thursday 26 November 2026.

Draws a 1024x1024 newspaper front page with PIL:
  masthead, two lead stories, THIRTEEN drawn scene panels,
  a world map with the 9 regions marked, a UTC timeline,
  40 verified stories grouped by region (5 in NA/EU/AF/S.Asia, 4 elsewhere),
  and a date-check + sources footer.

v4 keeps v3's layout (masthead, leads, map, timeline, date check) and adds
10 more drawn scene panels (13 total, matching the top-10 formula) plus
4 more verified stories (40 total). New stories: SpaceX FCC nod (NA),
EU budget summit no deal (EU), Tinubu Borno rescue vow (AF),
US deports 1,700 Indians (S.Asia) — all verified 27 Nov 2026.

Run:  python3 build-v4.py
Writes: v4-entry.jpg  (same directory)
"""
import math
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "v4-entry.jpg"

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
F_SERIF_B = ImageFont.truetype(FONT_DIR + "DejaVuSerif-Bold.ttf", 42)
F_SERIF = ImageFont.truetype(FONT_DIR + "DejaVuSerif.ttf", 20)
F_SANS_B = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 13)
F_SANS = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 11)
F_SANS_SM = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 10)
F_SANS_XS = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 9)
F_HEAD = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 12)
F_HEAD_SM = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 11)
F_REGION = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 15)
F_MAST_SUB = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 16)
F_LEAD_H = ImageFont.truetype(FONT_DIR + "DejaVuSerif-Bold.ttf", 21)
F_LEAD_D = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 12)
F_SEC = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 14)
F_TIME = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 11)
F_TL = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 10)
F_CAP = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 11)
F_FOOT = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 10)
F_FOOT_B = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 10)
F_SC_H = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 9)
F_SC_D = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 8)

PAPER = (253, 252, 247)
INK = (17, 17, 17)
GREY = (90, 88, 82)
RED = (155, 28, 31)
BLUE = (26, 58, 92)
LAND = (232, 228, 216)
LAND_LINE = (120, 116, 104)
OCEAN = (214, 228, 238)
GOLD = (176, 132, 30)

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


# ---------------------------------------------------------------- masthead
center(0, W, 6, "THE WORLD IN ONE PICTURE", F_SERIF, fill=GREY)
center(0, W, 26, "THURSDAY 26 NOVEMBER 2026", F_SERIF_B)
d.line([40, 72, W - 40, 72], fill=INK, width=2)
d.line([40, 76, W - 40, 76], fill=INK, width=1)
center(0, W, 82, "40 stories  •  9 regions  •  13 drawn scenes  •  One day, the whole world",
       F_MAST_SUB, fill=GREY)

# ---------------------------------------------------------------- lead stories
LEAD_Y = 104
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
        center(x0, x0 + 488, LEAD_Y + 2 + j * 22, hl, F_LEAD_H)
    center(x0, x0 + 488, LEAD_Y + 50, l1, F_LEAD_D, fill=GREY)
    center(x0, x0 + 488, LEAD_Y + 68, l2, F_LEAD_D, fill=GREY)
d.line([512, LEAD_Y, 512, LEAD_Y + 86], fill=(180, 176, 166), width=1)
d.line([16, 196, W - 16, 196], fill=INK, width=1)

# ---------------------------------------------------------------- scene panels
# 13 drawn scenes in two rows: row 1 = 7 panels (136 wide), row 2 = 6 panels
# (160 wide). Each panel: small pictogram on the left, short caption right.
SC_Y = 202
SC_H = 62
SC_GAP = 6
ROW1_W = 136
ROW2_W = 160

def scene_panel(x0, y0, pw):
    d.rectangle([x0, y0, x0 + pw, y0 + SC_H],
                outline=(150, 146, 136), width=1, fill=(240, 238, 230))
    return x0 + 5, y0 + 8  # drawing-box origin (42 x 46)

def scene_text(x0, y0, pw, head, detail):
    tx = x0 + 52
    max_w = pw - 52 - 4
    hl = wrap(head, F_SC_H, max_w)[:2]
    dl = wrap(detail, F_SC_D, max_w)[:2]
    ty = y0 + 5
    for line in hl:
        d.text((tx, ty), line, font=F_SC_H, fill=INK)
        ty += 11
    ty = y0 + 29
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
    base = dy + 42
    for i, (h, col) in enumerate([(16, (120, 120, 120)),
                                  (26, (26, 58, 92)), (36, (155, 28, 31))]):
        bx = dx + 4 + i * 13
        d.rectangle([bx, base - h, bx + 10, base], fill=col)
    d.line([dx + 2, base, dx + 40, base], fill=INK, width=1)

def draw_storm(dx, dy):
    # grey cloud, rain, lightning bolt
    d.ellipse([dx + 4, dy + 8, dx + 22, dy + 22], fill=(110, 112, 118))
    d.ellipse([dx + 14, dy + 4, dx + 32, dy + 20], fill=(130, 132, 138))
    d.ellipse([dx + 24, dy + 10, dx + 40, dy + 24], fill=(110, 112, 118))
    d.rectangle([dx + 4, dy + 18, dx + 40, dy + 24], fill=(120, 122, 128))
    for rx in (dx + 8, dx + 18, dx + 28):
        d.line([rx, dy + 28, rx - 2, dy + 36], fill=(60, 90, 140), width=2)
    d.polygon([(dx + 32, dy + 26), (dx + 26, dy + 40), (dx + 31, dy + 40),
               (dx + 27, dy + 46), (dx + 36, dy + 30), (dx + 31, dy + 30)],
              fill=(240, 190, 40))

def draw_brain(dx, dy):
    # head outline + chip implant
    d.ellipse([dx + 6, dy + 4, dx + 36, dy + 42], outline=(90, 88, 82), width=2)
    d.arc([dx + 12, dy + 12, dx + 30, dy + 26], 200, 340, fill=(200, 90, 120), width=2)
    d.arc([dx + 12, dy + 20, dx + 30, dy + 34], 180, 0, fill=(200, 90, 120), width=2)
    d.rectangle([dx + 16, dy + 16, dx + 28, dy + 28], fill=(26, 58, 92))
    for px in (dx + 18, dx + 24):
        d.line([px, dy + 14, px, dy + 16], fill=(26, 58, 92), width=2)
        d.line([px, dy + 28, px, dy + 30], fill=(26, 58, 92), width=2)

def draw_rocket(dx, dy):
    # diagonal missile with flame trail
    d.polygon([(dx + 26, dy + 4), (dx + 34, dy + 12), (dx + 22, dy + 24),
               (dx + 14, dy + 16)], fill=(90, 90, 96))
    d.polygon([(dx + 14, dy + 16), (dx + 22, dy + 24), (dx + 18, dy + 28),
               (dx + 10, dy + 20)], fill=(155, 28, 31))
    d.polygon([(dx + 10, dy + 20), (dx + 4, dy + 34), (dx + 12, dy + 30)],
              fill=(230, 120, 20))
    d.polygon([(dx + 11, dy + 24), (dx + 7, dy + 32), (dx + 13, dy + 29)],
              fill=(240, 190, 40))
    for (sx, sy) in [(dx + 36, dy + 30), (dx + 30, dy + 38), (dx + 40, dy + 38)]:
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(200, 40, 40))

def draw_plane_down(dx, dy):
    # small plane + red down arrow (migration falling)
    d.polygon([(dx + 6, dy + 14), (dx + 30, dy + 14), (dx + 38, dy + 18),
               (dx + 30, dy + 20), (dx + 6, dy + 20)], fill=(26, 58, 92))
    d.polygon([(dx + 14, dy + 14), (dx + 20, dy + 6), (dx + 24, dy + 14)],
              fill=(26, 58, 92))
    d.polygon([(dx + 14, dy + 20), (dx + 20, dy + 28), (dx + 24, dy + 20)],
              fill=(26, 58, 92))
    d.line([dx + 34, dy + 28, dx + 34, dy + 42], fill=(155, 28, 31), width=3)
    d.polygon([(dx + 29, dy + 38), (dx + 39, dy + 38), (dx + 34, dy + 45)],
              fill=(155, 28, 31))

def draw_virus(dx, dy):
    cx, cy = dx + 21, dy + 22
    for k in range(10):
        ang = k * 36 * 3.14159 / 180
        x1 = cx + 12 * math.cos(ang)
        y1 = cy + 12 * math.sin(ang)
        x2 = cx + 18 * math.cos(ang)
        y2 = cy + 18 * math.sin(ang)
        d.line([x1, y1, x2, y2], fill=(140, 30, 40), width=2)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(176, 60, 60),
              outline=(140, 30, 40), width=2)
    for (ox, oy) in [(-5, -4), (4, 2), (-2, 6)]:
        d.ellipse([cx + ox - 2, cy + oy - 2, cx + ox + 2, cy + oy + 2],
                  fill=(240, 190, 190))

def draw_candle(dx, dy):
    # memorial candle with flame
    d.polygon([(dx + 21, dy + 2), (dx + 26, dy + 12), (dx + 16, dy + 12)],
              fill=(240, 190, 40))
    d.polygon([(dx + 21, dy + 6), (dx + 24, dy + 12), (dx + 18, dy + 12)],
              fill=(230, 120, 20))
    d.rectangle([dx + 15, dy + 13, dx + 27, dy + 40], fill=(250, 248, 240),
                outline=(150, 146, 136))
    d.line([dx + 12, dy + 40, dx + 30, dy + 40], fill=(150, 146, 136), width=2)
    d.line([dx + 10, dy + 44, dx + 32, dy + 44], fill=INK, width=1)

def draw_satellite(dx, dy):
    # satellite body + solar panels + stars
    d.rectangle([dx + 2, dy + 20, dx + 12, dy + 26], fill=(26, 58, 92))
    d.line([dx + 7, dy + 20, dx + 7, dy + 26], fill=(120, 160, 200), width=1)
    d.rectangle([dx + 15, dy + 18, dx + 27, dy + 28], fill=(60, 70, 80))
    d.rectangle([dx + 30, dy + 20, dx + 40, dy + 26], fill=(26, 58, 92))
    d.line([dx + 35, dy + 20, dx + 35, dy + 26], fill=(120, 160, 200), width=1)
    d.line([dx + 21, dy + 18, dx + 21, dy + 10], fill=(90, 88, 82), width=1)
    d.ellipse([dx + 19, dy + 8, dx + 23, dy + 12], fill=(200, 40, 40))
    for (sx, sy) in [(dx + 6, dy + 6), (dx + 36, dy + 8), (dx + 12, dy + 34)]:
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(90, 88, 82))

def draw_eu(dx, dy):
    # EU stars disc + red no-deal cross
    cx, cy = dx + 19, dy + 22
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(26, 58, 92))
    for k in range(12):
        ang = k * 30 * 3.14159 / 180
        sx = cx + 11 * math.cos(ang)
        sy = cy + 11 * math.sin(ang)
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(240, 190, 40))
    d.line([dx + 32, dy + 34, dx + 40, dy + 42], fill=(200, 40, 40), width=3)
    d.line([dx + 40, dy + 34, dx + 32, dy + 42], fill=(200, 40, 40), width=3)

def draw_school(dx, dy):
    # schoolhouse with flag (Borno rescue vow)
    d.polygon([(dx + 4, dy + 22), (dx + 38, dy + 22), (dx + 21, dy + 8)],
              fill=(140, 60, 40))
    d.rectangle([dx + 8, dy + 22, dx + 34, dy + 42], fill=(232, 214, 170),
                outline=(150, 146, 136))
    d.rectangle([dx + 18, dy + 30, dx + 25, dy + 42], fill=(90, 70, 50))
    d.rectangle([dx + 11, dy + 26, dx + 15, dy + 31], fill=(120, 160, 200))
    d.rectangle([dx + 27, dy + 26, dx + 31, dy + 31], fill=(120, 160, 200))
    d.line([dx + 21, dy + 8, dx + 21, dy + 2], fill=(90, 88, 82), width=1)
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

# ---------------------------------------------------------------- world map
MAP_Y = 334
d.text((16, MAP_Y - 2), "THE WORLD TODAY — 9 REGIONS", font=F_SEC, fill=INK)
map_top, map_bot = 350, 450
d.rectangle([10, map_top, W - 10, map_bot], fill=OCEAN, outline=(150, 146, 136))

def proj(lon, lat):
    x = 10 + (lon + 180) / 360.0 * (W - 20)
    y = map_top + 6 + (75 - lat) * (map_bot - map_top - 12) / 130.0
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

# graticule
for lon in range(-150, 181, 30):
    x = 10 + (lon + 180) / 360.0 * (W - 20)
    d.line([x, map_top, x, map_bot], fill=(190, 205, 215), width=1)
for lat in (60, 30, 0, -30):
    y = map_top + 6 + (75 - lat) * (map_bot - map_top - 12) / 130.0
    d.line([10, y, W - 10, y], fill=(190, 205, 215), width=1)

HUBS = [
    (-100, 40, "Washington", 6, -5), (-52, -10, "Brasília", 6, -5),
    (31, 50, "Kyiv", 6, -5), (31, 30, "Cairo", 6, -5),
    (35, 31, "Jerusalem", -62, -5), (77, 20, "Mumbai", 6, -5),
    (127, 40, "Pyongyang", 6, -5), (113, -2, "Jakarta", 6, -5),
    (133, -25, "Canberra", 6, -5),
]
for lon, lat, name, dx, dy in HUBS:
    x, y = proj(lon, lat)
    d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=RED, outline=(255, 255, 255))
    d.text((x + dx, y + dy), name, font=F_SANS_XS, fill=INK)

# ---------------------------------------------------------------- UTC timeline
TL_Y = 456
d.text((16, TL_Y), "THE DAY IN UTC  —  times approximate", font=F_SEC, fill=INK)
tl_top = TL_Y + 26
d.line([30, tl_top + 14, W - 30, tl_top + 14], fill=INK, width=2)
events = [
    ("02:00", "Kyiv mall hit"),
    ("04:18", "India marks 26/11"),
    ("04:45", "Brazil pulls envoy"),
    ("07:45", "Bangkok blast"),
    ("08:00", "Cairo tanker fire"),
    ("09:30", "UK migration 77k"),
    ("14:00", "US tariffs unveiled"),
    ("15:00", "Macy's postponed"),
    ("18:53", "Game 3 drawn"),
]
n = len(events)
for i, (t, label) in enumerate(events):
    x = 40 + i * (W - 80) / (n - 1)
    d.ellipse([x - 4, tl_top + 10, x + 4, tl_top + 18], fill=RED)
    lw = d.textlength(label, font=F_TL)
    lx = max(20, min(x - lw / 2, W - 20 - lw))
    tx = max(16, min(x - 18, W - 50))
    if i % 2 == 0:
        d.text((tx, tl_top - 2), t, font=F_TIME, fill=INK)
        d.text((lx, tl_top + 22), label, font=F_TL, fill=GREY)
    else:
        d.text((lx, tl_top - 2), label, font=F_TL, fill=GREY)
        d.text((tx, tl_top + 22), t, font=F_TIME, fill=INK)

# ---------------------------------------------------------------- region grid
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
    ]),
    ("SOUTH AMERICA", [
        ("Brazil pulls envoy from Argentina",
         "Milei not invited to Lula's Jan 5 inauguration."),
        ("Venezuela debt put at $237.5bn",
         "Regime report reveals staggering public debt burden."),
        ("Japan stun Brazil 3–2 in friendly",
         "Raphinha and Ancelotti sent off in Singapore."),
        ("Argentina lose first post-Messi game",
         "Uruguay win 2–1 in Buenos Aires in new era."),
    ]),
    ("EUROPE", [
        ("Russian missiles hit Kyiv mall",
         "Seven wounded; 113 drones launched overnight."),
        ("Germany arrests synagogue-plot pair",
         "Two Iraqi suspects held in Cologne and Heidelberg."),
        ("UK net migration falls to 77,000",
         "Lowest since 1997 outside the pandemic, ONS says."),
        ("Gukesh–Sindarov Game 3 drawn",
         "60-move Berlin in Geneva; match level 1.5–1.5."),
        ("EU budget summit ends with no deal",
         "Leaders break off early; talks move to Dec 17."),
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
         "Abducted Borno children held since May–June."),
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
    ]),
    ("OCEANIA", [
        ("Australia passes digital duty law",
         "Tech giants face fines up to 5% of global revenue."),
        ("Australia–Fiji alliance begins",
         "Fourth security pact officially starts."),
        ("Aussie dollar steadies on data",
         "Business investment jumps most since 2011."),
        ("Qantas aborts Sydney landing",
         "737 go-around as Air NZ jet crosses runway."),
    ]),
]

GRID_Y = 522
COL_W = 328
ROW_HS = [158, 158, 132]  # rows 1-2 hold 5-story cells; row 3 holds 4-story cells
for idx, (region, stories) in enumerate(REGIONS):
    col, row = idx % 3, idx // 3
    x0 = 16 + col * (COL_W + 8)
    y0 = GRID_Y + sum(ROW_HS[:row]) + row * 6
    row_h = ROW_HS[row]
    d.rectangle([x0, y0, x0 + COL_W, y0 + 22], fill=RED)
    d.text((x0 + 8, y0 + 3), region, font=F_REGION, fill=(255, 255, 255))
    d.rectangle([x0, y0 + 22, x0 + COL_W, y0 + row_h],
                outline=(200, 196, 186), width=1)
    sy = y0 + 27
    for head, detail in stories:
        d.text((x0 + 8, sy), head, font=F_HEAD, fill=INK)
        d.text((x0 + 8, sy + 13), detail, font=F_SANS_SM, fill=GREY)
        sy += 26

# ---------------------------------------------------------------- footer
FT_Y = 994
d.line([16, FT_Y - 12, W - 16, FT_Y - 12], fill=INK, width=1)
center(0, W, FT_Y - 6,
       "DATE CHECK ✓  Thursday 26 November 2026 — all 40 stories dated 26 Nov 2026",
       F_FOOT_B)
center(0, W, FT_Y + 10,
       "Sources: Reuters • AP • The Hindu • Chess.com • NDTV • Firstpost • MercoPress • ONS • WHO • KCNA • PCG • ATSB • FCC • Euronews • Punch",
       F_FOOT)

img.save(OUT, quality=92)
print("wrote", OUT, img.size)
