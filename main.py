#!/usr/bin/env python3
"""The World in One Day -- Thursday 19 November 2026.

A pure-stdlib program that draws a dense newspaper front page summing up
the world's news of Thursday 19 November 2026 and writes it as a single
1024x1024 PNG to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

No network, no third-party imports, fully deterministic: two runs write
the same bytes. Text is rendered with a hand-written 5x7 bitmap font.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows of 5 cells; '#' is ink, '.' is
# blank. Lowercase letters sit on rows 2..6 where they have no ascender.

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".#..."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "a": (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".###.", "#...#", "#....", "#...#", ".###."),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#..#", ".#...", "###..", ".#...", ".#...", ".#..."),
    "g": (".....", ".###.", "#...#", "#...#", ".####", ".#...", "##..."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    "j": ("...#.", ".....", ".###.", "...#.", "...#.", "...#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "###..", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", ".#.#.", "..#..", ".#..."),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": ("###..", "..#..", "..#..", "..#..", "..#..", "..#..", "###.."),
    "|": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "\\": ("#....", "#....", ".#...", ".#...", "..#..", "..#..", "...#."),
    "^": ("..#..", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "~": (".....", ".....", ".##.#", "#.#.#", ".....", ".....", "....."),
    "`": (".#...", "..#..", ".....", ".....", ".....", ".....", "....."),
    "·": (".....", ".....", ".....", ".##..", ".##..", ".....", "....."),
    "—": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
}

FALLBACK = FONT["?"]


# ------------------------------------------------------------- canvas
# The picture is an RGB bytearray, row-major. All drawing goes through
# these helpers; nothing here touches the network or the clock, so the
# output bytes are identical on every run.


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.fill(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill(x, y, thick, h, color)

    def outline(self, x, y, w, h, color, thick=1):
        self.fill(x, y, w, thick, color)
        self.fill(x, y + h - thick, w, thick, color)
        self.fill(x, y, thick, h, color)
        self.fill(x + w - thick, y, thick, h, color)

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = r * r - (yy - cy) * (yy - cy)
            if dx < 0:
                continue
            d = int(dx ** 0.5)
            self.fill(cx - d, yy, 2 * d + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=2):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - thick) * (r - thick) <= d2 <= r * r:
                    self.set(xx, yy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        # Scanline fill: walk rows, find the x span of the triangle.
        ymin = min(y0, y1, y2)
        ymax = max(y0, y1, y2)
        pts = [(x0, y0), (x1, y1), (x2, y2)]
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in ((pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[0])):
                if ay == by:
                    continue
                if min(ay, by) <= yy <= max(ay, by):
                    xs.append(ax + (bx - ax) * (yy - ay) / (by - ay))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.fill(xa, yy, xb - xa + 1, 1, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        # Bresenham; thick by stamping small squares.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.fill(x - thick // 2, y - thick // 2, thick, thick, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy


# --------------------------------------------------------------- text
def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_glyph(cv, x, y, ch, scale, color):
    rows = FONT.get(ch, FALLBACK)
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            if cell == "#":
                cv.fill(x + c * scale, y + r * scale, scale, scale, color)


def text(cv, x, y, s, scale, color, bold=False):
    cx = x
    for ch in s:
        draw_glyph(cv, cx, y, ch, scale, color)
        if bold:
            draw_glyph(cv, cx + max(1, scale // 2), y, ch, scale, color)
        cx += 6 * scale
    return cx


def text_center(cv, cx, y, s, scale, color, bold=False):
    x = cx - text_width(s, scale) // 2
    return text(cv, x, y, s, scale, color, bold)


def wrap(s, max_chars):
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def paragraph(cv, x, y, s, width, scale, color, line_h=None, bold=False):
    if line_h is None:
        line_h = 7 * scale + 3
    max_chars = max(1, width // (6 * scale))
    yy = y
    for line in wrap(s, max_chars):
        text(cv, x, yy, line, scale, color, bold)
        yy += line_h
    return yy


# ---------------------------------------------------------- PNG out
def write_png(path, cv):
    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------------- colors
PAPER = (247, 243, 232)
INK = (26, 24, 20)
SOFT = (74, 70, 60)
RED = (165, 32, 28)
DARKRED = (120, 20, 18)
BLUE = (31, 74, 128)
GREEN = (34, 110, 72)
ORANGE = (196, 110, 30)
PURPLE = (104, 74, 140)
BROWN = (146, 104, 62)
GREY = (120, 116, 106)
LIGHT = (236, 230, 214)
CARD = (255, 253, 246)
NAVY = (16, 34, 62)
GOLD = (212, 160, 40)
SKY = (158, 196, 222)

REGION_COLORS = [
    ("EUROPE", 11, BLUE),
    ("THE AMERICAS", 10, GREEN),
    ("ASIA-PACIFIC", 8, RED),
    ("MIDDLE EAST", 6, ORANGE),
    ("AFRICA", 3, BROWN),
    ("OCEANIA", 1, PURPLE),
    ("WORLD", 2, GREY),
]

# ------------------------------------------------------------- map
# A dotted world map, 64 columns x 32 rows. '#' is land. Authored by
# hand as a coarse equirectangular sketch: x 0..63 is -180..180, y 0..31
# is 90..-60. The map panel draws one small square per land cell.
MAP_ROWS = [
    "................................................................",
    "............####................................................",
    "..........########.................#####...################....",
    ".........##########..............##########################....",
    "........###########......####..#############################...",
    ".........##########....######..#############################...",
    "..........##########..#######..##################..########...",
    "...........#########...######..##################...#######...",
    "............########....#####...#################....######...",
    ".............######......####...#################.....#####...",
    "..............#####.......###...################......####....",
    "...............####........###..########..#######.............",
    "................###.........############..######.............",
    ".................##..........###########...#####.............",
    ".................##...........##########....####...##........",
    "..................#............#########....###...####.......",
    "..................##............########.....##...#####......",
    "..................##.............######..............##......",
    "...................#.............######.............###......",
    "...................#..............####..........########.....",
    "...................#..............###..........##########....",
    "....................#.............###..........##########....",
    "....................#..............##...........########.....",
    "....................##.............##............######......",
    ".....................#............................####.......",
    ".....................#.......................................",
    ".....................##......................................",
    "......................#......................................",
    "................................................................",
    "................................................................",
    "................................................................",
    "................................................................",
]

# Numbered story markers on the map: (lon, lat, number, dx, dy). The
# dx/dy nudge keeps neighbouring markers' discs from overlapping.
MAP_MARKS = [
    (114.0, 22.5, "1", 0, 0),     # Shenzhen
    (-74.0, 40.7, "2", 0, 0),     # New York
    (4.3, 52.1, "4", 0, 0),       # The Hague
    (30.7, 36.9, "5", 0, 4),      # Antalya
    (85.8, 20.3, "6", 0, 0),      # Odisha
    (30.5, 50.4, "7", 0, 0),      # Kyiv
    (-80.2, 26.1, "9", 0, 3),     # Florida
    (42.5, 16.9, "12", 0, 0),     # Jazan
    (20.1, 32.1, "13", -6, 6),    # Benghazi
]


def draw_map(cv, x, y, w, h):
    # Panel background and dotted land.
    cv.fill(x, y, w, h, NAVY)
    cols, rows = 64, 32
    cw = w / cols
    ch = h / rows
    dot = max(1, int(min(cw, ch) * 0.62))
    for r, line in enumerate(MAP_ROWS):
        for c, cell in enumerate(line):
            if cell == "#":
                px = x + int(c * cw + (cw - dot) / 2)
                py = y + int(r * ch + (ch - dot) / 2)
                cv.fill(px, py, dot, dot, (232, 214, 160))
    # Numbered markers.
    for lon, lat, num, dx, dy in MAP_MARKS:
        mx = x + int((lon + 180.0) / 360.0 * w) + dx
        my = y + int((90.0 - lat) / 150.0 * h) + dy
        cv.disc(mx, my, 8, RED)
        cv.ring(mx, my, 8, (255, 255, 255), 1)
        text(cv, mx - 3, my - 3, num, 1, (255, 255, 255), bold=True)


# -------------------------------------------------------- illustrations
# Small flat geometric pictures for the story cards. Each draws inside
# the given box (x, y, w, h) and nothing outside it.

def ill_skyline(cv, x, y, w, h):
    """Shenzhen summit: dusk skyline, three flags, rising sun."""
    cv.fill(x, y, w, h, (44, 62, 96))
    cv.disc(x + w - 34, y + 26, 15, GOLD)
    heights = [0.55, 0.8, 0.45, 0.95, 0.6, 0.75, 0.5, 0.88, 0.62, 0.7]
    bw = w // len(heights)
    for i, f in enumerate(heights):
        bh = int(h * f)
        cv.fill(x + i * bw + 1, y + h - bh, bw - 2, bh, (24, 34, 58))
        # lit windows
        for wy in range(y + h - bh + 6, y + h - 6, 10):
            cv.fill(x + i * bw + bw // 2 - 1, wy, 3, 3, (255, 214, 120))
    # three flags on poles above the skyline
    def flag(fx, kind):
        cv.vline(fx, y + 6, 34, (240, 240, 240), 2)
        if kind == "us":
            cv.fill(fx + 2, y + 6, 22, 13, (178, 34, 52))
            cv.fill(fx + 2, y + 8, 22, 2, (255, 255, 255))
            cv.fill(fx + 2, y + 12, 22, 2, (255, 255, 255))
            cv.fill(fx + 2, y + 6, 9, 7, (60, 59, 110))
        elif kind == "cn":
            cv.fill(fx + 2, y + 6, 22, 13, (222, 41, 16))
            cv.disc(fx + 7, y + 11, 2, GOLD)
            cv.disc(fx + 14, y + 9, 1, GOLD)
            cv.disc(fx + 16, y + 13, 1, GOLD)
        else:
            cv.fill(fx + 2, y + 6, 22, 4, (255, 255, 255))
            cv.fill(fx + 2, y + 10, 22, 5, (0, 57, 166))
            cv.fill(fx + 2, y + 15, 22, 4, (213, 0, 50))
    flag(x + 14, "us")
    flag(x + 52, "cn")
    flag(x + 90, "ru")


def ill_sunset(cv, x, y, w, h):
    """GTA VI day: neon sunset over a Vice City skyline."""
    bands = [(58, 24, 92), (94, 32, 104), (150, 48, 96), (224, 92, 66), (248, 168, 80)]
    bh = h // len(bands)
    for i, col in enumerate(bands):
        cv.fill(x, y + i * bh, w, bh + 1, col)
    cv.disc(x + w // 2, y + h - 30, 26, (255, 236, 170))
    cv.fill(x, y + h - 34, w, 4, (58, 24, 92))
    # skyline silhouettes
    heights = [0.42, 0.62, 0.35, 0.7, 0.5, 0.58, 0.4]
    bw = w // len(heights)
    for i, f in enumerate(heights):
        sh = int(h * f * 0.55)
        cv.fill(x + i * bw + 2, y + h - sh, bw - 4, sh, (30, 12, 48))
    # palm silhouettes
    for px in (x + 18, x + w - 22):
        cv.vline(px, y + h - 34, 22, (20, 8, 32), 3)
        cv.line(px, y + h - 34, px - 10, y + h - 42, (20, 8, 32), 2)
        cv.line(px, y + h - 34, px + 10, y + h - 42, (20, 8, 32), 2)
        cv.line(px, y + h - 34, px, y + h - 46, (20, 8, 32), 2)
    cv.fill(x + 8, y + 8, 74, 14, (20, 8, 32))
    text(cv, x + 12, y + 10, "OUT TODAY", 1, (255, 236, 170), bold=True)


def ill_chart(cv, x, y, w, h):
    """Anthropic IPO: green board, rising candles and a climbing line."""
    cv.fill(x, y, w, h, (12, 58, 44))
    # grid
    for gy in range(y + 12, y + h - 8, 16):
        cv.hline(x + 6, gy, w - 12, (28, 96, 74), 1)
    # candlesticks rising left to right
    lows = [0.72, 0.66, 0.6, 0.55, 0.47, 0.42, 0.34, 0.28]
    bw = (w - 24) // len(lows)
    for i, f in enumerate(lows):
        cx = x + 12 + i * bw + bw // 2
        top = y + int(h * f)
        bot = y + int(h * (f + 0.16))
        cv.vline(cx, top - 5, bot - top + 10, (220, 240, 230), 1)
        col = (64, 224, 140) if i % 3 else (240, 120, 110)
        cv.fill(cx - bw // 4, top, bw // 2, bot - top, col)
    # climbing trend line
    pts = []
    for i, f in enumerate(lows):
        pts.append((x + 12 + i * bw + bw // 2, y + int(h * f) - 8))
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], (255, 214, 90), 3)
    cv.fill(x + 8, y + 6, 118, 14, (8, 40, 30))
    text(cv, x + 12, y + 8, "ANT  NASDAQ  FIRST TRADE", 1, (255, 255, 255), bold=True)
    text(cv, x + w - 46, y + h - 18, "$83", 2, (255, 214, 90), bold=True)


def ill_court(cv, x, y, w, h):
    """The Hague: courthouse with columns under a pale sky."""
    cv.fill(x, y, w, h, (214, 222, 230))
    cv.triangle(x + 6, y + h - 22, x + w - 6, y + h - 22, x + w // 2, y + 6, (120, 90, 60))
    cv.fill(x + 8, y + h - 22, w - 16, 3, (90, 70, 50))
    for i in range(5):
        cx = x + 12 + i * ((w - 24) // 4)
        cv.fill(cx - 2, y + h - 19, 4, 14, (240, 240, 235))
    cv.fill(x + 8, y + h - 5, w - 16, 3, (90, 70, 50))


def ill_climate(cv, x, y, w, h):
    """COP31: sun over striped earth bands."""
    cv.fill(x, y, w, h, (232, 220, 180))
    cv.disc(x + w - 18, y + 12, 9, (230, 140, 40))
    bands = [(120, 160, 90), (90, 140, 110), (60, 120, 130), (50, 100, 140)]
    bh = (h - 14) // len(bands)
    for i, col in enumerate(bands):
        cv.fill(x, y + 14 + i * bh, w, bh + 1, col)
    cv.hline(x, y + 14, w, (255, 255, 255), 2)


def ill_storm(cv, x, y, w, h):
    """Cyclone Akvan: spiral cloud over a dark sea."""
    cv.fill(x, y, w, h, (30, 50, 84))
    cx, cy = x + w // 2, y + h // 2 - 2
    cv.disc(cx, cy, 5, (240, 240, 240))
    for r, col in ((9, (200, 220, 240)), (14, (170, 195, 225)), (19, (140, 170, 210)), (24, (110, 145, 190))):
        cv.ring(cx, cy, r, col, 3)
    cv.fill(x, y + h - 8, w, 8, (16, 28, 52))
    for i in range(6):
        cv.fill(x + 6 + i * ((w - 12) // 6), y + h - 5, 8, 2, (200, 220, 240))


def ill_kyiv(cv, x, y, w, h):
    """Kyiv: blue and gold bands with domes."""
    cv.fill(x, y, w, h // 2, (40, 110, 200))
    cv.fill(x, y + h // 2, w, h - h // 2, (250, 200, 40))
    for dx, r in ((0.3, 7), (0.55, 9), (0.8, 6)):
        cx = x + int(w * dx)
        cv.fill(cx - 3, y + h - 20, 6, 12, (90, 60, 20))
        cv.disc(cx, y + h - 20, r, (250, 200, 40))
        cv.disc(cx, y + h - 20, r - 3, (230, 170, 30))


def ill_trade(cv, x, y, w, h):
    """APEC: a big globe with land patches and a member-count label."""
    cv.fill(x, y, w, h, (180, 210, 225))
    cx, cy = x + w // 2, y + h // 2 - 2
    cv.disc(cx, cy, 15, (40, 100, 160))
    cv.disc(cx - 6, cy - 4, 4, (120, 190, 120))
    cv.disc(cx + 5, cy + 3, 5, (120, 190, 120))
    cv.disc(cx + 7, cy - 6, 3, (120, 190, 120))
    cv.ring(cx, cy, 15, (30, 70, 120), 2)
    cv.fill(x + w // 2 - 40, y + h - 11, 80, 9, (30, 70, 120))
    text(cv, x + w // 2 - 36, y + h - 10, "21 ECONOMIES", 1, (255, 255, 255), bold=True)


def ill_rain(cv, x, y, w, h):
    """Florida floods: rain cloud over rising water."""
    cv.fill(x, y, w, h, (150, 170, 190))
    cv.disc(x + w // 2 - 10, y + 12, 9, (70, 85, 105))
    cv.disc(x + w // 2 + 8, y + 12, 11, (70, 85, 105))
    cv.fill(x + w // 2 - 18, y + 12, 36, 8, (70, 85, 105))
    for i in range(7):
        rx = x + 8 + i * ((w - 16) // 7)
        cv.line(rx, y + 24, rx - 3, y + 32, (220, 235, 245), 2)
    cv.fill(x, y + h - 10, w, 10, (40, 90, 140))
    for i in range(5):
        cv.fill(x + 8 + i * ((w - 16) // 5), y + h - 6, 10, 2, (200, 230, 245))


def ill_strata(cv, x, y, w, h):
    """Geology: layered rock strata with a fossil ring."""
    bands = [(160, 120, 80), (140, 100, 60), (120, 140, 90), (100, 110, 130), (90, 90, 110)]
    bh = h // len(bands)
    for i, col in enumerate(bands):
        cv.fill(x, y + i * bh, w, bh + 1, col)
    cv.ring(x + w // 2, y + h // 2, 9, (245, 235, 210), 3)
    cv.disc(x + w // 2, y + h // 2, 3, (245, 235, 210))


def ill_paris(cv, x, y, w, h):
    """Paris: tower silhouette against a tricolore sky."""
    cv.fill(x, y, w // 3, h, (40, 90, 180))
    cv.fill(x + w // 3, y, w // 3 + 1, h, (245, 245, 240))
    cv.fill(x + 2 * w // 3, y, w - 2 * w // 3, h, (220, 50, 60))
    cx = x + w // 2
    cv.triangle(cx - 16, y + h - 4, cx + 16, y + h - 4, cx, y + 4, (60, 55, 50))
    cv.fill(cx - 2, y + 4, 4, h - 8, (60, 55, 50))
    cv.fill(cx - 11, y + h - 14, 22, 3, (60, 55, 50))
    cv.fill(cx - 6, y + h - 24, 12, 3, (60, 55, 50))


def ill_desert(cv, x, y, w, h):
    """Jazan: sun over low desert dunes, with a green all-clear tick."""
    cv.fill(x, y, w, h, (245, 220, 160))
    cv.disc(x + w - 16, y + 10, 8, (240, 160, 40))
    # low dune arcs: big discs whose centres sit below the panel
    cv.disc(x + w // 4, y + h + 22, 34, (220, 170, 90))
    cv.disc(x + 3 * w // 4, y + h + 26, 38, (200, 150, 70))
    cv.fill(x, y + h - 3, w, 3, (180, 130, 60))
    # a green all-clear tick on a white chip
    cv.fill(x + 8, y + 8, 24, 16, (255, 255, 255))
    cv.outline(x + 8, y + 8, 24, 16, (34, 140, 70), 1)
    cv.line(x + 12, y + 16, x + 16, y + 20, (34, 140, 70), 2)
    cv.line(x + 16, y + 20, x + 27, y + 11, (34, 140, 70), 2)


def ill_seizure(cv, x, y, w, h):
    """Benghazi: capsules and parcels on a dark table."""
    cv.fill(x, y, w, h, (50, 44, 40))
    cols = [(220, 60, 60), (240, 200, 60), (255, 255, 255), (80, 160, 220)]
    for i, col in enumerate(cols):
        px = x + 8 + i * ((w - 24) // 4)
        cv.fill(px, y + 8, 14, 8, col)
        cv.fill(px + 14, y + 8, 14, 8, (255, 255, 255))
        cv.outline(px, y + 8, 28, 8, (20, 18, 16), 1)
    cv.fill(x + 10, y + h - 16, w - 20, 10, (150, 120, 70))
    cv.fill(x + 10, y + h - 16, w - 20, 2, (110, 85, 45))


# ------------------------------------------------------------- stories
# Every story below happened, or was first reported, on Thursday
# 19 November 2026. Stories first reported on Wednesday 18 November
# (the Jeffries nomination vote, Voyager 1's light-day crossing, the
# EU's proposed EUR 45bn Ukraine loan, Pew's Islam projection) are
# deliberately NOT counted as news; they appear only in the DATE CHECK
# box at the foot of the page.

HEROES = [
    {
        "num": "1", "place": "SHENZHEN", "beat": "SUMMIT",
        "ill": ill_skyline,
        "head": "Trump, Xi and Putin hold first three-way summit",
        "body": "The three leaders meet at APEC in Shenzhen; arms control "
                "and the Iran war top the agenda. Ukraine is left off it.",
    },
    {
        "num": "2", "place": "NEW YORK", "beat": "GAMES",
        "ill": ill_sunset,
        "head": "GTA VI arrives after a 13-year wait",
        "body": "Rockstar's sequel unlocks at midnight in each country, "
                "New Zealand first; 15.9m pre-orders banked. $79.99 on "
                "PS5 and Xbox, no PC yet.",
    },
    {
        "num": "3", "place": "NASDAQ", "beat": "MARKETS",
        "ill": ill_chart,
        "head": "Anthropic debuts in the biggest IPO on record",
        "body": "Priced at $83, above its range, the Claude maker raised "
                "$81.3bn and is valued near $1.5tn. Thursday's first "
                "trades set the real price.",
    },
]

SECONDARY = [
    {"num": "4", "place": "THE HAGUE", "beat": "LAW", "ill": ill_court,
     "head": "World Court rules on Myanmar's Rohingya case",
     "body": "The ICJ reads its judgment in The Gambia's case over the "
             "2017 campaign."},
    {"num": "5", "place": "ANTALYA", "beat": "CLIMATE", "ill": ill_climate,
     "head": "COP31 enters its final 48 hours",
     "body": "Ministers take over the text in Antalya; 'phase out' and "
             "the $120bn fund still open."},
    {"num": "6", "place": "ODISHA", "beat": "STORM", "ill": ill_storm,
     "head": "Akvan bears down as 200,000 flee the coast",
     "body": "Red alerts in 11 districts, schools shut. Landfall near "
             "Puri due Friday."},
    {"num": "7", "place": "KYIV", "beat": "WAR", "ill": ill_kyiv,
     "head": "Crimean Bridge hit for a third time this week",
     "body": "Overnight strike halts traffic on the crossing; Kyiv's "
             "role unconfirmed."},
    {"num": "8", "place": "SHENZHEN", "beat": "TRADE", "ill": ill_trade,
     "head": "APEC leaders adopt the Shenzhen Declaration",
     "body": "Twenty-one economies back digital trade and an "
             "Asia-Pacific community roadmap."},
    {"num": "9", "place": "FLORIDA", "beat": "WEATHER", "ill": ill_rain,
     "head": "Flooded Florida braces for still more rain",
     "body": "A foot of rain in hours in Hollywood; 300 rescue calls "
             "in a night."},
    {"num": "10", "place": "SCIENCE", "beat": "GEOLOGY", "ill": ill_strata,
     "head": "Earth's missing billion years are explained",
     "body": "A Nature study blames mantle currents and ancient ice "
             "sheets for the erasure."},
    {"num": "11", "place": "PARIS", "beat": "POLITICS", "ill": ill_paris,
     "head": "Melenchon could win, says France's justice minister",
     "body": "The hard-left leader is a plausible president, the "
             "minister concedes."},
    {"num": "12", "place": "JAZAN", "beat": "GULF", "ill": ill_desert,
     "head": "Saudi Arabia says danger has passed in three cities",
     "body": "The all-clear follows southern alerts after a Houthi "
             "missile was downed."},
    {"num": "13", "place": "BENGHAZI", "beat": "CRIME", "ill": ill_seizure,
     "head": "Cocaine and millions of pills seized in eastern Libya",
     "body": "Officials display one of the country's biggest drug "
             "hauls, seized in the east."},
]

BRIEFS = [
    "14 GAZA - four nations urge aid for flooded Gaza",
    "15 ESTONIA - Russia border to close in December",
    "16 PRAGUE - huge march for media freedom",
    "17 MADRID - general strike hits ports, factories",
    "18 JERUSALEM - Eisenkot tapped to form government",
    "19 CARACAS - US details $12bn oil revenue",
    "20 TOKYO - India, Japan review defence ties in 2+2",
    "21 SEOUL - N. Korea expands uranium enrichment",
    "22 OTTAWA - Canada sanctions Israeli settlers",
    "23 JAKARTA - EU greenlights Indonesia trade pact",
    "24 NEW DELHI - Modi meets the Prince of Wales",
    "25 LONDON - Van Gogh sells for a record $190.4m",
    "26 MEXICO CITY - Banxico cuts rates to 6.25%",
    "27 BERLIN - IMF lifts Germany growth to 1.3%",
    "28 WASHINGTON - AI cyber threats outpace defences",
    "29 BRUSSELS - Colby quits Ukraine meeting early",
    "30 WASHINGTON - Russian charged in Palantir case",
    "31 GULF - USS Roosevelt arrives amid tensions",
    "32 GAZA - senior Hamas commander killed in strike",
    "33 LONDON - drought now covers 82% of England",
    "34 NAIROBI - drought deepens Kenya milk shortage",
    "35 MOGADISHU - Somalia crisis deepens over reforms",
    "36 TEHRAN - Trump: Iran seeks biological weapons",
    "37 MIAMI - NTSB: helicopter flew low before crash",
    "38 LOS ANGELES - Stacy Keach dies at 85",
    "39 PARIS - fourth weekend of cost protests",
    "40 NEW DELHI - Sindhu back in badminton top five",
    "41 SYDNEY - General Pants enters administration",
]

KPIS = [
    ("$81.3bn", "raised by Anthropic - the largest IPO on record"),
    ("15.9m", "GTA VI pre-orders banked before release day"),
    ("200,000", "evacuated ahead of Cyclone Akvan"),
    ("$120bn", "a year of adaptation finance unresolved at COP31"),
    ("730,000", "Rohingya who fled in 2017 - the ICJ case"),
    ("13 yrs", "wait since GTA V, ended at midnight"),
]

DATE_CHECK = (
    "the House Democrats' 251-11 vote nominating Hakeem Jeffries - "
    "Voyager 1 crossing one light-day, at 10:16 GMT Wednesday - the EU's "
    "proposed EUR 45bn loan for Ukraine - Pew's projection that Islam "
    "becomes the largest religion by 2035 - the Iranian drone "
    "interceptions over Kuwait and Bahrain - the first COP31 draft "
    "(Monday) - the Bangladesh garment shutdowns."
)

FOOTER = [
    "Every story happened, or was first reported, on Thursday 19 November 2026. "
    "Disputed claims are attributed, not stated as fact.",
    "Sources: Reuters, AP, AFP, BBC, The Hindu, IMD, NASA, ICJ, Pew. "
    "Original drawings. The World in One Day - 19 November 2026.",
]


# -------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H, PAPER)
    mx = 20
    cw = W - 2 * mx  # 984

    # Top bar.
    cv.hline(mx, 10, cw, INK, 2)
    text(cv, mx, 16, "THE WORLD IN ONE DAY", 1, RED, bold=True)
    right = "ONE PAGE · 41 STORIES · THURSDAY'S NEWS"
    text(cv, mx + cw - text_width(right, 1), 16, right, 1, SOFT, bold=True)
    cv.hline(mx, 27, cw, INK, 1)

    # Masthead.
    text_center(cv, W // 2, 33, "Thursday 19 November 2026", 6, INK, bold=True)
    deck = ("First three-way summit in Shenzhen · GTA VI day · the biggest "
            "IPO in history · a genocide judgment")
    text_center(cv, W // 2, 81, deck, 1, DARKRED, bold=True)
    cv.hline(mx, 94, cw, INK, 1)

    # Region strip.
    widths = [130, 190, 180, 150, 100, 110, 124]
    x = mx
    for (name, count, color), wd in zip(REGION_COLORS, widths):
        cv.fill(x, 99, wd, 20, color)
        label = "%s %d" % (name, count)
        text_center(cv, x + wd // 2, 105, label, 1, (255, 255, 255), bold=True)
        x += wd

    # KPI strip.
    kx = mx
    kcol = cw // 6
    for num, cap in KPIS:
        text(cv, kx + 4, 127, num, 3, RED, bold=True)
        paragraph(cv, kx + 4, 152, cap, kcol - 10, 1, SOFT)
        kx += kcol
        if kx < mx + cw:
            cv.vline(kx - 1, 127, 52, (200, 192, 172), 1)
    cv.hline(mx, 187, cw, INK, 2)

    # Hero row: three big cards.
    hy, hh = 193, 220
    hw = (cw - 24) // 3
    for i, s in enumerate(HEROES):
        x = mx + i * (hw + 12)
        cv.fill(x, hy, hw, hh, CARD)
        cv.outline(x, hy, hw, hh, (180, 172, 150), 1)
        s["ill"](cv, x + 4, hy + 4, hw - 8, 96)
        kicker = "%s · %s · %s" % (s["num"], s["place"], s["beat"])
        text(cv, x + 8, hy + 106, kicker, 1, RED, bold=True)
        yy = paragraph(cv, x + 8, hy + 118, s["head"], hw - 16, 2, INK,
                       line_h=17, bold=True)
        paragraph(cv, x + 8, yy + 3, s["body"], hw - 16, 1, SOFT)

    # Secondary rows: five small cards each.
    sy = 419
    sh = 136
    sw = (cw - 40) // 5
    for row in range(2):
        for i in range(5):
            s = SECONDARY[row * 5 + i]
            x = mx + i * (sw + 10)
            y = sy + row * (sh + 6)
            cv.fill(x, y, sw, sh, CARD)
            cv.outline(x, y, sw, sh, (180, 172, 150), 1)
            s["ill"](cv, x + 3, y + 3, sw - 6, 40)
            kicker = "%s · %s · %s" % (s["num"], s["place"], s["beat"])
            text(cv, x + 6, y + 47, kicker, 1, RED, bold=True)
            yy = paragraph(cv, x + 6, y + 58, s["head"], sw - 12, 1, INK,
                           line_h=10, bold=True)
            paragraph(cv, x + 6, yy + 2, s["body"], sw - 12, 1, SOFT,
                      line_h=10)

    # Bottom band: map + numbered briefs.
    by, bh = 703, 200
    map_w = 350
    cv.fill(mx, by, map_w, bh, CARD)
    cv.outline(mx, by, map_w, bh, (180, 172, 150), 1)
    cv.fill(mx, by, map_w, 18, NAVY)
    text(cv, mx + 8, by + 5, "WHERE IT HAPPENED", 1, (255, 255, 255), bold=True)
    draw_map(cv, mx + 4, by + 22, map_w - 8, 138)
    paragraph(cv, mx + 8, by + 166,
              "Red numbers mark the lead stories. Positions are approximate.",
              map_w - 16, 1, SOFT, line_h=10)

    bx = mx + map_w + 8
    bw = mx + cw - bx
    cv.fill(bx, by, bw, bh, CARD)
    cv.outline(bx, by, bw, bh, (180, 172, 150), 1)
    text(cv, bx + 8, by + 6,
         "ALSO ON THURSDAY 19 NOVEMBER - 28 MORE STORIES", 1, RED, bold=True)
    cv.hline(bx + 8, by + 20, bw - 16, (200, 192, 172), 1)
    col_w = (bw - 16) // 2
    for col in range(2):
        cx0 = bx + 8 + col * col_w
        for j in range(14):
            b = BRIEFS[col * 14 + j]
            text(cv, cx0, by + 26 + j * 12, b, 1, INK)

    # Date check box.
    dy = 909
    cv.outline(mx, dy, cw, 54, RED, 2)
    text(cv, mx + 8, dy + 6,
         "DATE CHECK - FIRST REPORTED WEDNESDAY 18 NOV, SO NOT ON THIS PAGE AS NEWS:",
         1, RED, bold=True)
    paragraph(cv, mx + 8, dy + 19, DATE_CHECK, cw - 16, 1, INK, line_h=11)

    # Footer.
    text_center(cv, W // 2, 970, FOOTER[0], 1, SOFT)
    text_center(cv, W // 2, 981, FOOTER[1], 1, SOFT)
    cv.hline(mx, 996, cw, INK, 1)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    cv = build()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, cv)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
