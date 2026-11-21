# main.py — the hand-in program for the news-image bounty.
# Python 3.13, standard library only. It draws the front page of
# Friday 20 November 2026 from the story list below (every story happened,
# or was first reported, on that day) and writes it to /output/entry.png
# (or $MAKEFUN_OUTPUT_DIR/entry.png outside the grader). The drawing engine
# lives in render.py beside this file. The output is fully deterministic:
# no clock, no randomness, no network — two runs write identical bytes.
#
# Run it:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from render import Canvas, write_png

W, H = 1024, 1024
MX = 16                      # page margin
CW = W - 2 * MX              # 992

# ------------------------------------------------------------ palette ----
PAPER = (247, 241, 227)
INK = (17, 17, 17)
RED = (180, 35, 24)
NAVY = (15, 27, 45)
NAVY2 = (16, 24, 48)
BLUE = (29, 78, 137)
SKY = (127, 179, 213)
SEA = (46, 110, 166)
SEALIGHT = (168, 198, 224)
LAND = (206, 178, 120)
LAND2 = (201, 179, 128)
TEAL = (15, 118, 110)
GOLD = (180, 83, 9)
GREEN = (22, 101, 52)
PURPLE = (107, 33, 168)
GRAY = (107, 114, 128)
LINE = (216, 210, 192)
WHITE = (255, 255, 255)
CREAM2 = (239, 231, 211)
YELLOW = (242, 194, 48)
ORANGE = (232, 118, 42)
GRID = (40, 60, 90)
DARK = (10, 10, 10)

# ------------------------------------------------------------- stories ----
# Leads: (number, kicker, headline, body). Tiles: (label, kicker, headline,
# summary, tag, scene). Also-on: (place, text, source). All of it is the
# verified news of Friday 20 November 2026, as reported that day.
LEADS = [
    (
        1, "KYIV, UKRAINE · WAR",
        "Russian missiles hit three Kyiv bridges",
        "An overnight barrage of about 110 missiles and 400 drones killed "
        "at least nine people and cut power and water in Kyiv. "
        "(Kyiv Independent, BBC)",
    ),
    (
        2, "ODISHA, INDIA · CYCLONE",
        "Cyclone Akvan comes ashore in eastern India",
        "The storm crossed the coast near Gopalpur from about 8 am after "
        "more than 370,000 people were moved to shelters. No deaths were "
        "reported. (IMD, Deccan Herald)",
    ),
    (
        3, "TAIPEI · SEOUL · TOKYO · MARKETS",
        "AI sell-off sinks Asia's stock markets",
        "Taiwan's index fell 6.2% to end its worst week since 1991. Seoul "
        "lost 5.2% and Tokyo 5.1% as chipmakers led the slide. "
        "(Al Jazeera, Anadolu)",
    ),
]

TILES = [
    ("UK-EU DEAL", "BRUSSELS · DIPLOMACY",
     "UK and EU seal a \"reset\" deal",
     "Food trade, youth visas, carbon link.",
     "Agreed · Reuters", "flags"),
    ("COP31: NO DEAL", "ANTALYA · CLIMATE",
     "COP31 reaches its last day with no deal",
     "The draft text leaves out fossil fuels.",
     "Ongoing · UN News", "globe"),
    ("POLAND: MISSILE", "E. POLAND · SECURITY",
     "Russian cruise missile lands in Poland",
     "It fell in a field; two airports paused.",
     "Minister says · Reuters", "missile"),
    ("IRAQ: ARMY IN", "C. IRAQ · SECURITY",
     "Iraqi army enters a militia stronghold",
     "Troops deploy to Jurf al-Sakhar.",
     "Witnessed · Reuters", "tanks"),
    ("ITALY: STRIKE", "ITALY · LABOUR",
     "General strike over Italy's budget",
     "Workers and students march.",
     "Reported · Reuters", "strike"),
    ("JAPAN: +2.3%", "TOKYO · ECONOMY",
     "Japan's inflation picks up to 2.3%",
     "A December rate rise stays in view.",
     "Official · Reuters", "sun"),
    ("SEOUL: IMPEACH", "SEOUL · POLITICS",
     "Korea's ruling party to impeach top judge",
     "It follows an overturned conviction.",
     "Party decision · Herald", "parliament"),
    ("KENYA: OIL", "TURKANA · ENERGY",
     "Kenya starts drilling its first oil well",
     "First crude is due on 1 December.",
     "Ceremony · allAfrica", "rig"),
    ("BUKELE: 3RD BID", "SAN SALVADOR · POLIT.",
     "Bukele files to run for a third term",
     "The vote is on 28 February 2027.",
     "Filed · AP", "ballot"),
    ("PHILLIPS: 118", "WELLINGTON · CRICKET",
     "Phillips hits 118 against India",
     "Hundreds v India in all three formats.",
     "Scorecard · ICC", "cricket"),
]

ALSO_ON = [
    ("Lviv", "A strike on a railway station kills two", "BBC"),
    ("Moscow", "Russia declares Estonia's border closure", "Reuters"),
    ("Berlin", "School pupils strike against military service", "Al Jazeera"),
    ("London", "General says UK runs cyber attacks abroad", "Sky News"),
    ("Beijing", "China holds its loan rates for an 18th month", "Xinhua"),
    ("Tokyo", "SoftBank shares fall more than 14% in a day", "Al Jazeera"),
    ("Seoul", "Kospi index ends the week 7.9% lower", "Anadolu"),
    ("Ganjam", "209 mm of rain falls as Akvan crosses Odisha", "PTI"),
    ("Lebanon", "Israeli air strikes hit the south and the east", "Anadolu"),
    ("Yemen", "Gunmen fire on a cargo ship off the coast", "UKMTO"),
    ("Abuja", "Court bars new evidence against Tinubu", "Channels TV"),
    ("Kampala", "Police told to enforce Ebola ban on rallies", "allAfrica"),
    ("Malawi", "Fuel crisis brings night-long petrol queues", "Al Jazeera"),
    ("Africa", "AfDB says 22 countries are in debt distress", "allAfrica"),
    ("Las Vegas", "Russell fastest in wet Grand Prix practice", "Autosport"),
    ("New York", "Nasdaq futures fall 1.6% before the bell", "24/7 Wall St"),
    ("Washington", "Democrats query law firm's free work", "Al Jazeera"),
    ("Wellington", "Nicholls makes 175 in a stand of 216", "ICC"),
    ("Sydney", "Australian shares fall 1.8% in the sell-off", "Reuters"),
    ("Antalya", "Panama asks COP31 to cap world oil output", "Anadolu"),
    ("Antalya", "EU official calls the climate draft unacceptable", "RTE"),
    ("Turin", "ATP backs a plan to lift player pay past $350m", "Anadolu"),
]

DATE_CHECK = (
    "Left out on purpose as Thursday 19 November's news: the World Court's "
    "ruling on Myanmar, the three-leader declaration in Shenzhen, Tonga's "
    "drought emergency and the migrant boat lost off Senegal, BepiColombo's "
    "entry into orbit round Mercury and any final COP31 text."
)


def build():
    cv = Canvas(W, H, PAPER)
    c = {}
    for name, rgb in [
        ("paper", PAPER), ("ink", INK), ("red", RED), ("navy", NAVY),
        ("navy2", NAVY2), ("blue", BLUE), ("sky", SKY), ("sea", SEA),
        ("sealight", SEALIGHT), ("land", LAND), ("land2", LAND2),
        ("teal", TEAL), ("gold", GOLD), ("green", GREEN),
        ("purple", PURPLE), ("gray", GRAY), ("line", LINE),
        ("white", WHITE), ("cream2", CREAM2), ("yellow", YELLOW),
        ("orange", ORANGE), ("grid", GRID), ("dark", DARK),
    ]:
        c[name] = cv.color(rgb)

    # ------------------------------------------------------- masthead ----
    cv.text(MX, 10, "THE WORLD IN ONE DAY", 1, c["red"], bold=True)
    cv.text(W - MX, 10, "35 STORIES · 7 REGIONS · EVERY ONE DATED FRIDAY 20 NOVEMBER 2026",
            1, c["ink"], align="right")
    cv.fill_rect(MX, 26, CW, 3, c["ink"])
    cv.text(W // 2, 36, "Friday 20 November 2026", 5, c["ink"], bold=True, align="center")
    cv.text(W // 2, 84,
            "Russian missiles hit Kyiv's bridges · Cyclone Akvan strikes India · "
            "AI sell-off sinks Asia · UK and EU seal a deal",
            1, c["ink"], align="center")
    cv.fill_rect(MX, 102, CW, 1, c["ink"])

    # ---------------------------------------------------- number strip ----
    numbers = [
        ("3", "bridges damaged in Kyiv"),
        ("370,000", "people moved to shelters"),
        ("-6.2%", "Taiwan's index, Friday's close"),
        ("100,000", "youth visas a year, UK-EU deal"),
        ("2.3%", "Japan inflation in October"),
        ("118", "runs by Phillips v India"),
    ]
    widths = [165, 165, 166, 165, 165, 166]
    x = MX
    for i, (num, label) in enumerate(numbers):
        w = widths[i]
        cv.text(x + 8, 108, num, 3, c["ink"], bold=True, advance=22)
        cv.para(x + 8, 136, label, 1, c["gray"], w - 16, 10)
        if i < 5:
            cv.fill_rect(x + w - 2, 110, 3, 44, c["red"])
        x += w

    # ---------------------------------------------------- region strip ----
    regions = [
        ("Europe 8", "blue"), ("Asia 8", "red"), ("Middle East 3", "gold"),
        ("Africa 5", "green"), ("Americas 4", "purple"), ("Oceania 3", "teal"),
        ("Global 4", "gray"),
    ]
    rw = [142, 142, 141, 142, 142, 141, 142]
    x = MX
    for i, (label, col) in enumerate(regions):
        cv.fill_rect(x, 160, rw[i], 16, c[col])
        cv.text(x + rw[i] // 2, 162, label, 1, c["white"], bold=True, align="center")
        x += rw[i]

    # ---------------------------------------------------------- panels ----
    px = [MX, 352, 688]
    pw = 320
    py, ph = 180, 140
    draw_panel_kyiv(cv, c, px[0], py, pw, ph)
    draw_panel_cyclone(cv, c, px[1], py, pw, ph)
    draw_panel_markets(cv, c, px[2], py, pw, ph)

    # ----------------------------------------------------------- leads ----
    ly = 332
    for (num, kicker, head, body), x0 in zip(LEADS, px):
        cv.circle(x0 + 9, ly + 9, 9, c["red"])
        cv.text(x0 + 9, ly + 5, str(num), 1, c["white"], bold=True, align="center")
        cv.text(x0 + 24, ly + 5, kicker, 1, c["red"], bold=True)
        y = ly + 22
        y += cv.para(x0, y, head, 2, c["ink"], pw, 19, bold=True)
        y += 4
        cv.para(x0, y, body, 1, c["ink"], pw, 10)

    # ----------------------------------------------------------- tiles ----
    tx = [MX, 217, 418, 619, 820]
    tw = 189
    ty = [460, 566]
    th = 98
    for i, tile in enumerate(TILES):
        col = i % 5
        row = i // 5
        draw_tile(cv, c, tx[col], ty[row], tw, th, 4 + i, tile)

    # ---------------------------------------------------- map + also -----
    by = 670
    cv.text(MX, by, "WHERE IT HAPPENED", 1, c["red"], bold=True)
    cv.text(352, by, "ALSO ON FRIDAY 20 NOVEMBER — 22 MORE STORIES", 1, c["red"], bold=True)
    draw_map(cv, c, MX, by + 16, 320, 178)
    cv.para(MX, by + 200, "Each number is the story with that number on this page.",
            1, c["gray"], 320, 10)
    col_x = [352, 688]
    for j, (place, text, src) in enumerate(ALSO_ON):
        col = j // 11
        k = j % 11
        draw_also(cv, c, col_x[col], by + 16 + k * 20, 320, 14 + j, place, text, src)

    # ------------------------------------------------------ date check ----
    dy = 912
    cv.rect(MX, dy, CW, 52, c["red"], t=2)
    cv.fill_rect(MX + 8, dy + 8, 96, 18, c["red"])
    cv.text(MX + 56, dy + 10, "DATE CHECK", 1, c["white"], bold=True, align="center")
    cv.para(MX + 112, dy + 8, DATE_CHECK, 1, c["ink"], CW - 124, 11)

    # ---------------------------------------------------------- footer ----
    cv.text(MX, 972, "Every story here happened, or was first reported, on 20 November 2026.",
            1, c["ink"])
    cv.text(W - MX, 972, "Sources named beside each story · original drawings",
            1, c["gray"], align="right")
    return cv


# -------------------------------------------------------------- panels ----
def draw_panel_kyiv(cv, c, x0, y0, w, h):
    cv.fill_rect(x0, y0, w, h, c["navy"])
    for sx, sy in [(20, 12), (60, 30), (120, 10), (180, 22), (240, 12), (290, 28),
                   (90, 45), (210, 40), (270, 52), (150, 55), (40, 60)]:
        cv.fill_rect(x0 + sx, y0 + sy, 2, 2, c["white"])
    for bx, bw, bh in [(0, 40, 40), (44, 34, 52), (82, 26, 36), (112, 40, 48),
                       (156, 30, 34), (190, 36, 44), (230, 28, 32), (262, 34, 42),
                       (300, 20, 30)]:
        cv.fill_rect(x0 + bx, y0 + h - bh, bw, bh, c["dark"])
    for wx, wy in [(10, 112), (52, 100), (90, 118), (120, 104), (165, 116),
                   (198, 108), (238, 118), (270, 106)]:
        cv.fill_rect(x0 + wx, y0 + wy, 2, 2, c["yellow"])
    cv.fill_rect(x0, y0 + 118, w, 3, c["gray"])
    cv.fill_rect(x0 + 90, y0 + 84, 6, 36, c["gray"])
    cv.fill_rect(x0 + 210, y0 + 84, 6, 36, c["gray"])
    for ax, ay, bx, by in [(93, 84, 40, 118), (93, 84, 150, 118),
                           (213, 84, 150, 118), (213, 84, 280, 118)]:
        cv.line(x0 + ax, y0 + ay, x0 + bx, y0 + by, c["gray"])
    cv.dashed_line(x0 + 300, y0 + 10, x0 + 250, y0 + 100, c["yellow"])
    cv.dashed_line(x0 + 278, y0 + 6, x0 + 150, y0 + 100, c["yellow"])
    cv.burst(x0 + 60, y0 + 110, 10, c["yellow"])
    cv.burst(x0 + 150, y0 + 112, 12, c["orange"])
    cv.burst(x0 + 250, y0 + 110, 10, c["yellow"])
    cv.fill_rect(x0 + 10, y0 + 10, 100, 30, c["red"])
    cv.text(x0 + 16, y0 + 14, "KYIV", 3, c["white"], bold=True, advance=22)
    cv.fill_rect(x0 + 10, y0 + 44, 236, 20, c["dark"])
    cv.text(x0 + 16, y0 + 46, "3 bridges hit", 2, c["white"])
    cv.fill_rect(x0 + 10, y0 + h - 16, 140, 14, c["dark"])
    cv.text(x0 + 14, y0 + h - 14, "Officials' count", 1, c["white"])


def draw_panel_cyclone(cv, c, x0, y0, w, h):
    cv.fill_rect(x0, y0, w, h, c["sea"])
    cv.poly([(x0, y0), (x0 + 90, y0), (x0 + 120, y0 + 30), (x0 + 110, y0 + 70),
             (x0 + 70, y0 + 110), (x0 + 30, y0 + h), (x0, y0 + h)], c["land"])
    cv.poly([(x0 + 250, y0 + 8), (x0 + 300, y0 + 4), (x0 + 312, y0 + 30),
             (x0 + 280, y0 + 44), (x0 + 252, y0 + 30)], c["land2"])
    for r in (40, 28, 16):
        cv.ring(x0 + 205, y0 + 70, r, c["white"], t=2)
    cv.circle(x0 + 205, y0 + 70, 6, c["white"])
    cv.dashed_line(x0 + 205, y0 + 70, x0 + 118, y0 + 62, c["red"])
    cv.circle(x0 + 118, y0 + 62, 5, c["red"])
    cv.fill_rect(x0 + 10, y0 + 10, 220, 26, c["red"])
    cv.text(x0 + 16, y0 + 13, "CYCLONE AKVAN", 2, c["white"], bold=True)
    cv.fill_rect(x0 + 10, y0 + 40, 234, 20, c["dark"])
    cv.text(x0 + 16, y0 + 42, "Landfall · 8 am", 2, c["white"])
    cv.text(x0 + 262, y0 + 118, "BAY OF BENGAL", 1, c["white"], bold=True, align="right")
    cv.fill_rect(x0 + 10, y0 + h - 16, 112, 14, c["dark"])
    cv.text(x0 + 14, y0 + h - 14, "Weather office", 1, c["white"])


def draw_panel_markets(cv, c, x0, y0, w, h):
    cv.fill_rect(x0, y0, w, h, c["navy2"])
    for gy in range(20, h, 20):
        cv.hline(x0, y0 + gy, w, c["grid"])
    pts = [(10, 30), (60, 45), (110, 40), (160, 70), (210, 85), (260, 110), (300, 125)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(x0 + ax, y0 + ay, x0 + bx, y0 + by, c["red"])
        cv.line(x0 + ax, y0 + ay + 1, x0 + bx, y0 + by + 1, c["red"])
    cv.poly([(x0 + 300, y0 + 125), (x0 + 288, y0 + 118), (x0 + 288, y0 + 130)], c["red"])
    rows = [("Taipei", "-6.2%"), ("Seoul", "-5.2%"), ("Tokyo", "-5.1%"), ("Hong Kong", "-1.9%")]
    for i, (city, val) in enumerate(rows):
        yy = y0 + 16 + i * 16
        cv.text(x0 + 196, yy, city, 1, c["white"], bold=True)
        cv.text(x0 + 268, yy, val, 1, c["red"], bold=True)
    cv.fill_rect(x0 + 10, y0 + 10, 186, 26, c["red"])
    cv.text(x0 + 16, y0 + 13, "AI SELL-OFF", 2, c["white"], bold=True)
    cv.fill_rect(x0 + 10, y0 + 40, 176, 20, c["dark"])
    cv.text(x0 + 16, y0 + 42, "Asia, Friday's close", 1, c["white"])
    cv.fill_rect(x0 + 10, y0 + h - 16, 116, 14, c["dark"])
    cv.text(x0 + 14, y0 + h - 14, "Closing prices", 1, c["white"])


# --------------------------------------------------------------- tiles ----
def draw_tile(cv, c, x0, y0, w, h, num, tile):
    label, kicker, head, summary, tag, scene = tile
    draw_scene(cv, c, x0, y0, w, 30, scene)
    cv.fill_rect(x0, y0 + 2, 8 + len(label) * 8 + 6, 14, c["red"])
    cv.text(x0 + 4, y0 + 4, label, 1, c["white"], bold=True)
    y = y0 + 33
    cv.text(x0, y, str(num), 1, c["red"], bold=True)
    cv.text(x0 + (20 if num >= 10 else 14), y, kicker, 1, c["red"], bold=True)
    y = y0 + 45
    y += cv.para(x0, y, head, 1, c["ink"], w, 10, bold=True)
    cv.para(x0, y, summary, 1, c["gray"], w, 10)
    cv.text(x0, y0 + h - 10, tag, 1, c["gray"])


def draw_scene(cv, c, x0, y0, w, h, scene):
    if scene == "flags":
        cv.fill_rect(x0, y0, w // 2, h, c["blue"])
        cv.circle(x0 + w // 4, y0 + h // 2, 8, c["yellow"])
        cv.fill_rect(x0 + w // 2, y0, w // 2, h, c["white"])
        cv.fill_rect(x0 + w // 2 + w // 4 - 4, y0, 8, h, c["red"])
        cv.fill_rect(x0 + w // 2, y0 + h // 2 - 4, w // 2, 8, c["red"])
    elif scene == "globe":
        cv.fill_rect(x0, y0, w, h, c["teal"])
        cv.circle(x0 + 40, y0 + 15, 11, c["green"])
        cv.circle(x0 + 44, y0 + 12, 5, c["blue"])
        cv.fill_rect(x0 + 150, y0 + 4, 6, 22, c["white"])
        cv.circle(x0 + 153, y0 + 24, 5, c["red"])
    elif scene == "missile":
        cv.fill_rect(x0, y0, w, h, c["cream2"])
        cv.fill_rect(x0 + 8, y0 + 18, 90, 4, c["green"])
        cv.dashed_line(x0 + 100, y0 + 8, x0 + 170, y0 + 22, c["red"])
        cv.poly([(x0 + 170, y0 + 18), (x0 + 182, y0 + 22), (x0 + 170, y0 + 26)], c["gray"])
    elif scene == "tanks":
        cv.fill_rect(x0, y0, w, h, c["land"])
        cv.fill_rect(x0 + 20, y0 + 16, 60, 8, c["green"])
        cv.fill_rect(x0 + 110, y0 + 18, 56, 8, c["green"])
        cv.line(x0 + 30, y0 + 16, x0 + 22, y0 + 6, c["green"])
        cv.circle(x0 + 160, y0 + 8, 6, c["green"])
    elif scene == "strike":
        cv.fill_rect(x0, y0, w // 3, h, c["green"])
        cv.fill_rect(x0 + w // 3, y0, w // 3, h, c["white"])
        cv.fill_rect(x0 + 2 * w // 3, y0, w // 3, h, c["red"])
        for dx in (30, 70, 110, 150):
            cv.circle(x0 + dx, y0 + 20, 4, c["ink"])
    elif scene == "sun":
        cv.fill_rect(x0, y0, w, h, c["white"])
        cv.circle(x0 + 40, y0 + 15, 10, c["red"])
        for i, bh in enumerate((8, 14, 11, 18, 15)):
            cv.fill_rect(x0 + 100 + i * 16, y0 + 26 - bh, 10, bh, c["gray"])
    elif scene == "parliament":
        cv.fill_rect(x0, y0, w, h, c["sealight"])
        cv.fill_rect(x0 + 60, y0 + 12, 70, 14, c["white"])
        cv.poly([(x0 + 78, y0 + 12), (x0 + 112, y0 + 12), (x0 + 95, y0 + 2)], c["white"])
        for dx in (66, 82, 98, 114):
            cv.fill_rect(x0 + dx, y0 + 14, 4, 12, c["gray"])
    elif scene == "rig":
        cv.fill_rect(x0, y0, w, h, c["orange"])
        cv.circle(x0 + 150, y0 + 12, 10, c["yellow"])
        cv.line(x0 + 40, y0 + 28, x0 + 60, y0 + 4, c["dark"])
        cv.line(x0 + 80, y0 + 28, x0 + 60, y0 + 4, c["dark"])
        cv.fill_rect(x0 + 36, y0 + 26, 48, 4, c["dark"])
    elif scene == "ballot":
        cv.fill_rect(x0, y0, w, h, c["cream2"])
        cv.fill_rect(x0 + 70, y0 + 10, 50, 16, c["blue"])
        cv.fill_rect(x0 + 82, y0 + 8, 26, 4, c["white"])
        cv.text(x0 + 145, y0 + 10, "2027", 1, c["ink"], bold=True)
    elif scene == "cricket":
        cv.fill_rect(x0, y0, w, h, c["green"])
        cv.poly([(x0 + 40, y0 + 4), (x0 + 52, y0 + 4), (x0 + 48, y0 + 26), (x0 + 36, y0 + 26)], c["land2"])
        cv.circle(x0 + 120, y0 + 12, 6, c["red"])
        cv.text(x0 + 140, y0 + 10, "118", 1, c["white"], bold=True)


# ----------------------------------------------------------------- map ----
def draw_map(cv, c, x0, y0, w, h):
    cv.fill_rect(x0, y0, w, h, c["cream2"])
    cv.poly([(x0 + 8, y0 + 28), (x0 + 30, y0 + 14), (x0 + 62, y0 + 18), (x0 + 88, y0 + 30),
             (x0 + 84, y0 + 52), (x0 + 70, y0 + 58), (x0 + 58, y0 + 78), (x0 + 40, y0 + 72),
             (x0 + 22, y0 + 60), (x0 + 10, y0 + 44)], c["land"])
    cv.poly([(x0 + 88, y0 + 8), (x0 + 104, y0 + 10), (x0 + 102, y0 + 22), (x0 + 90, y0 + 20)], c["land"])
    cv.poly([(x0 + 78, y0 + 96), (x0 + 96, y0 + 92), (x0 + 110, y0 + 108), (x0 + 102, y0 + 138),
             (x0 + 90, y0 + 158), (x0 + 80, y0 + 140), (x0 + 74, y0 + 116)], c["land"])
    cv.poly([(x0 + 150, y0 + 30), (x0 + 168, y0 + 22), (x0 + 184, y0 + 28), (x0 + 182, y0 + 44),
             (x0 + 168, y0 + 48), (x0 + 156, y0 + 44)], c["land"])
    cv.poly([(x0 + 150, y0 + 62), (x0 + 172, y0 + 58), (x0 + 190, y0 + 68), (x0 + 188, y0 + 96),
             (x0 + 178, y0 + 122), (x0 + 164, y0 + 124), (x0 + 154, y0 + 100), (x0 + 148, y0 + 78)], c["land"])
    cv.poly([(x0 + 186, y0 + 26), (x0 + 230, y0 + 14), (x0 + 286, y0 + 20), (x0 + 306, y0 + 40),
             (x0 + 296, y0 + 66), (x0 + 270, y0 + 78), (x0 + 240, y0 + 72), (x0 + 210, y0 + 60),
             (x0 + 190, y0 + 48)], c["land"])
    cv.poly([(x0 + 258, y0 + 84), (x0 + 272, y0 + 82), (x0 + 274, y0 + 94), (x0 + 260, y0 + 96)], c["land"])
    cv.poly([(x0 + 262, y0 + 120), (x0 + 292, y0 + 116), (x0 + 302, y0 + 130),
             (x0 + 288, y0 + 146), (x0 + 266, y0 + 142)], c["land"])
    dots = [
        (184, 38, "1", "red"), (238, 66, "2", "red"), (280, 58, "3", "red"),
        (148, 26, "4", "blue"), (192, 54, "5", "blue"), (172, 22, "6", "red"),
        (210, 64, "7", "red"), (158, 50, "8", "red"), (302, 48, "9", "red"),
        (288, 38, "10", "red"), (172, 96, "11", "green"), (52, 62, "12", "purple"),
        (306, 152, "13", "teal"),
    ]
    for dx, dy, num, col in dots:
        cv.circle(x0 + dx, y0 + dy, 7, c[col])
        cv.text(x0 + dx, y0 + dy - 4, num, 1, c["white"], bold=True, align="center")


def draw_also(cv, c, x0, y0, w, num, place, text, src):
    full = "%s %s (%s)" % (place, text, src)
    lines = cv.wrap(full, w - 26, 1)
    cv.text(x0, y0, str(num), 1, c["red"], bold=True)
    for i, ln in enumerate(lines[:2]):
        cv.text(x0 + 26, y0 + i * 10, ln, 1, c["ink"])


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(cv, path)
    with open(path, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    print("news-image-20261120: wrote %s (%d bytes, sha256 %s)" % (path, size, digest))
    print("dimensions: 1024x1024, stories: 35, regions: 7")


if __name__ == "__main__":
    main()
