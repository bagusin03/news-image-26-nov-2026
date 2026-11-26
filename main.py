#!/usr/bin/env python3
"""news-image-20261126: one front-page image summing up Thursday 26 November 2026.

Pure Python 3.13 standard library only. No network, no files read, no randomness,
no clock: the same bytes come out of every run. Draws a newspaper front page
("THE WORLD TODAY") with the day's verified stories, all first reported on
26 November 2026 in at least one time zone (Wed 25 Nov in the US = Thu 26 Nov
in Asia):

  * US announces new tariffs on 14 trading partners: China 20%, EU 15%
    (Section 301, overcapacity probe)
  * Houthis claim an attack on Saudi Arabia's largest refinery, Ras Tanura;
    Brent crude tops $94 a barrel
  * Two oil tankers hit naval mines, explode and catch fire in the Strait
    of Hormuz
  * Fuel tanker crash on Cairo's Ring Road kills at least 30 people
  * Israeli judges recommend dropping the bribery case against PM Netanyahu
  * Shenzhou-24 docks with Tiangong: Pakistan's first astronaut in orbit

Output: /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png), 1024x1024 PNG.
"""

import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)
INK = (20, 33, 61)
RED = (193, 39, 45)
BLUE = (29, 111, 184)
SKY = (178, 216, 240)
TEAL = (14, 124, 123)
GOLD = (232, 163, 23)
ORANGE = (232, 106, 23)
FLAME = (245, 158, 11)
GREEN = (46, 125, 50)
GREY = (107, 114, 128)
LIGHTGREY = (210, 208, 198)
WHITE = (255, 255, 255)
BLACK = (12, 12, 12)
SEA = (23, 92, 140)
SEALIGHT = (64, 148, 196)
BROWN = (120, 72, 32)
SKIN = (232, 190, 150)

# ------------------------------------------------------- hand-drawn 5x7 font
FONT = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    '3': ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ',': ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ':': ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    '-': ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '?': ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    '&': ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    '/': ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    '%': ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    '$': ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    '+': ["00000", "00100", "00100", "01110", "00100", "00100", "00000"],
    '=': ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    '*': ["00000", "10101", "01110", "11111", "01110", "10101", "00000"],
    '"': ["01010", "01010", "00000", "00000", "00000", "00000", "00000"],
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def wrap_text(s, max_w, scale):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    lines = []
    for raw in s.split("\n"):
        words = raw.split(" ")
        cur = ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
    return lines

# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.buf), 3):
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = r, g, b

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                j = base + (xx - x0) * 3
                self.buf[j], self.buf[j + 1], self.buf[j + 2] = c

    def border(self, x, y, w, h, c, t=3):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, wd=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        r = max(1, wd // 2)
        while True:
            self.circle(x, y, r, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            dx = int(rx * math.sqrt(max(0.0, 1.0 - (dy * dy) / float(ry * ry))))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def poly(self, pts, c):
        """Filled polygon via scanline."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.rect(int(math.ceil(xs[k])), y,
                          int(math.floor(xs[k + 1])) - int(math.ceil(xs[k])) + 1, 1, c)

    def text(self, x, y, s, c, scale=2):
        cx = x
        for ch in s.upper():
            g = FONT.get(ch, FONT[' '])
            for row in range(7):
                for col in range(5):
                    if g[row][col] == '1':
                        self.rect(cx + col * scale, y + row * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, c, scale=2):
        self.text(cx - text_width(s, scale) // 2, y, s, c, scale)

    def para(self, x, y, s, c, max_w, scale=2, leading=None):
        lh = leading if leading is not None else 9 * scale
        for line in wrap_text(s, max_w, scale):
            self.text(x, y, line, c, scale)
            y += lh
        return y


def panel(cv, x, y, w, h, tag, tag_color=RED):
    cv.rect(x, y, w, h, WHITE)
    cv.border(x, y, w, h, INK, 3)
    cv.rect(x, y, w, 26, INK)
    cv.text(x + 10, y + 5, tag, WHITE, 2)


# ------------------------------------------------------------------- scenes
def draw_tariff_scene(cv, x, y, w, h):
    """Container port: cranes, stacked containers, cargo ship, sized h=110."""
    cv.rect(x, y, w, h, SKY)
    cv.circle(x + w - 40, y + 18, 15, GOLD)
    # sea + quay
    cv.rect(x, y + h - 30, w, 30, SEA)
    cv.rect(x, y + h - 30, w, 4, SEALIGHT)
    # cargo ship with containers
    sx, sy = x + 30, y + h - 58
    cv.rect(sx, sy + 12, 210, 16, INK)
    for i, col in enumerate((RED, BLUE, GOLD, TEAL, ORANGE)):
        cv.rect(sx + 12 + i * 38, sy - 14, 34, 26, col)
        cv.rect(sx + 12 + i * 38, sy - 14, 34, 3, WHITE)
    cv.rect(sx + 210, sy - 6, 26, 34, WHITE)
    cv.rect(sx + 216, sy - 6, 14, 8, RED)
    # cranes
    for cx in (x + 300, x + 430):
        cv.rect(cx, y + 18, 8, h - 48, INK)
        cv.line(cx, y + 18, cx + 90, y + 44, INK, 5)
        cv.line(cx + 90, y + 44, cx + 90, y + 62, INK, 3)
        cv.rect(cx + 82, y + 62, 16, 12, GOLD)
    # (rates 20% / 15% are in the red headline box below, not repeated here)


def draw_refinery_scene(cv, x, y, w, h):
    """Oil refinery: towers, tanks, smoke plume, sized h=80 band."""
    cv.rect(x, y, w, h, (232, 214, 180))
    cv.circle(x + 34, y + 16, 13, GOLD)
    # storage tanks
    for tx, tw in ((x + 8, 46), (x + 58, 40)):
        cv.ellipse(tx + tw // 2, y + h - 18, tw // 2, 9, WHITE)
        cv.rect(tx, y + h - 36, tw, 20, WHITE)
        cv.rect(tx, y + h - 36, tw, 4, INK)
    # distillation towers
    for tx, th in ((x + 150, 58), (x + 176, 68), (x + 202, 52)):
        cv.rect(tx, y + h - th, 16, th, GREY)
        cv.rect(tx - 3, y + h - th - 6, 22, 6, INK)
    # flare stack with flame + smoke
    fx = x + w - 60
    cv.rect(fx, y + 22, 10, h - 22, INK)
    cv.circle(fx + 5, y + 16, 10, FLAME)
    cv.circle(fx + 5, y + 16, 5, WHITE)
    for sx, sy, sr in ((fx - 16, y + 6, 9), (fx + 2, y - 2, 11), (fx + 20, y + 8, 8)):
        cv.circle(sx, sy, sr, GREY)
    # oil price tag, top centre, clear of the towers and flare stack
    cv.rect(x + 130, y + 6, 92, 20, INK)
    cv.text(x + 136, y + 11, "OIL $94", GOLD, 2)


def draw_tanker_scene(cv, x, y, w, h):
    """Tanker at sea hitting a mine: explosion, smoke, sized h=80 band."""
    cv.rect(x, y, w, h, SKY)
    cv.circle(x + w - 34, y + 16, 14, GOLD)
    cv.rect(x, y + h - 36, w, 36, SEA)
    cv.rect(x, y + h - 36, w, 4, SEALIGHT)
    # tanker hull
    cv.rect(x + 30, y + h - 52, 220, 20, RED)
    cv.poly([(x + 250, y + h - 52), (x + 282, y + h - 44), (x + 250, y + h - 32)], RED)
    cv.rect(x + 60, y + h - 72, 26, 20, WHITE)
    cv.rect(x + 60, y + h - 72, 26, 4, INK)
    cv.rect(x + 130, y + h - 66, 60, 14, WHITE)
    # mine explosion starburst amidships
    ex, ey = x + 150, y + 26
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        cv.line(ex, ey, int(ex + 18 * math.cos(rad)), int(ey + 18 * math.sin(rad)),
                ORANGE, 5)
    cv.circle(ex, ey, 11, FLAME)
    cv.circle(ex, ey, 5, WHITE)
    cv.circle(ex - 18, ey - 14, 9, GREY)
    cv.circle(ex + 6, ey - 20, 11, GREY)
    # second tanker, small, background right
    cv.rect(x + w - 90, y + h - 44, 70, 12, GREY)
    cv.rect(x + w - 78, y + h - 56, 14, 12, WHITE)


def draw_cairo_scene(cv, x, y, w, h):
    """Overturned fuel tanker on a ring road, flames, sized h=120 band."""
    cv.rect(x, y, w, h, (232, 214, 180))
    cv.circle(x + 34, y + 16, 13, GOLD)
    # road
    cv.rect(x, y + h - 34, w, 34, (60, 60, 60))
    for dx in range(x + 10, x + w - 10, 36):
        cv.rect(dx, y + h - 18, 20, 4, WHITE)
    # overturned tanker: cylinder on its side + cab
    cv.ellipse(x + 70, y + h - 52, 52, 16, ORANGE)
    cv.rect(x + 18, y + h - 52, 104, 16, ORANGE)
    cv.rect(x + 130, y + h - 56, 30, 22, RED)
    cv.circle(x + 40, y + h - 34, 9, INK)
    cv.circle(x + 100, y + h - 34, 9, INK)
    # flames above the tanker
    for fx, fh in ((x + 50, 26), (x + 80, 34), (x + 110, 24)):
        cv.poly([(fx - 12, y + h - 52), (fx, y + h - 52 - fh), (fx + 12, y + h - 52)],
                FLAME)
    cv.circle(x + 80, y + h - 84, 10, GREY)
    cv.circle(x + 104, y + h - 92, 8, GREY)
    # charred cars, right
    cv.rect(x + w - 92, y + h - 56, 62, 16, BLACK)
    cv.rect(x + w - 84, y + h - 68, 34, 12, BLACK)


def draw_court_scene(cv, x, y, w, h):
    """Courthouse facade with columns, sized for an h=110 art band."""
    cv.rect(x, y, w, h, SKY)
    cv.circle(x + w - 40, y + 18, 15, GOLD)
    cv.poly([(x + 20, y + 46), (x + w // 2, y + 8), (x + w - 20, y + 46)], INK)
    cv.rect(x + 20, y + 46, w - 40, 8, INK)
    for cx in range(x + 44, x + w - 40, 52):
        cv.rect(cx, y + 54, 16, h - 54, WHITE)
        cv.rect(cx, y + 54, 16, 5, INK)
        cv.rect(cx, y + h - 8, 16, 5, INK)
    cv.rect(x, y + h - 6, w, 6, INK)
    # scales of justice, left
    sx, sy = x + 52, y + h - 52
    cv.line(sx, sy - 26, sx, sy + 12, GOLD, 4)
    cv.line(sx - 22, sy - 26, sx + 22, sy - 26, GOLD, 4)
    cv.line(sx - 22, sy - 26, sx - 28, sy - 6, GOLD, 3)
    cv.line(sx + 22, sy - 26, sx + 28, sy - 6, GOLD, 3)
    cv.ellipse(sx - 28, sy - 4, 12, 4, GOLD)
    cv.ellipse(sx + 28, sy - 4, 12, 4, GOLD)
    # gavel, right
    gx, gy = x + w - 92, y + h - 34
    cv.rect(gx, gy, 34, 14, BROWN)
    cv.rect(gx - 8, gy - 4, 50, 5, BROWN)
    cv.line(gx + 42, gy + 4, gx + 66, gy - 14, BROWN, 5)


def draw_space_scene(cv, x, y, w, h):
    """Rocket lifting off toward a space station, sized for an h=120 band."""
    cv.rect(x, y, w, h, (16, 24, 64))
    for sx, sy in ((x + 30, y + 20), (x + 90, y + 40), (x + 200, y + 16),
                   (x + 260, y + 46), (x + 150, y + 60)):
        cv.circle(sx, sy, 2, WHITE)
    # space station, top right
    sx, sy = x + w - 90, y + 34
    cv.rect(sx - 46, sy - 6, 92, 12, BLUE)
    cv.rect(sx - 10, sy - 14, 20, 28, WHITE)
    cv.rect(sx - 58, sy - 4, 12, 8, GOLD)
    cv.rect(sx + 46, sy - 4, 12, 8, GOLD)
    # rocket, centre-left, nose up
    rx, ry = x + 90, y + h - 78
    cv.poly([(rx, ry - 34), (rx + 14, ry - 14), (rx + 14, ry + 22),
             (rx, ry + 30), (rx - 14, ry + 22), (rx - 14, ry - 14)], WHITE)
    cv.circle(rx, ry - 8, 6, RED)
    cv.poly([(rx - 14, ry + 22), (rx - 26, ry + 40), (rx - 14, ry + 30)], RED)
    cv.poly([(rx + 14, ry + 22), (rx + 26, ry + 40), (rx + 14, ry + 30)], RED)
    cv.poly([(rx - 6, ry + 30), (rx, ry + 52), (rx + 6, ry + 30)], FLAME)
    cv.circle(rx, ry + 58, 6, GREY)
    # crescent moon, top left
    cv.circle(x + 26, y + 22, 12, GOLD)
    cv.circle(x + 31, y + 19, 10, (16, 24, 64))


# ------------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.rect(0, 0, W, 8, RED)
    cv.text_center(W // 2, 18, "THE WORLD TODAY", INK, 6)
    cv.rect(12, 88, W - 24, 3, INK)
    cv.rect(12, 96, W - 24, 36, RED)
    cv.text_center(W // 2, 104, "THURSDAY 26 NOVEMBER 2026", WHITE, 3)
    cv.text_center(W // 2, 136, "THE DAY'S WORLD NEWS - IN ONE PICTURE", INK, 1)

    # ---- row 1: lead tariffs + Ras Tanura + Hormuz
    panel(cv, 12, 156, 600, 366, "TRADE - WASHINGTON, USA")
    draw_tariff_scene(cv, 15, 185, 594, 110)
    cv.rect(36, 302, 552, 66, RED)
    cv.text(52, 314, "NEW TARIFFS", WHITE, 4)
    cv.text(52, 346, "CHINA 20% - EU 15%", WHITE, 2)
    cv.text(36, 378, "US HITS 14 PARTNERS", INK, 3)
    cv.text(36, 406, "WITH NEW DUTIES", INK, 3)
    cv.para(36, 442, "Section 301 tariffs on China, the EU, Japan, Korea and more, to curb subsidised factory output.",
            INK, 552, 2)

    panel(cv, 624, 156, 388, 182, "OIL - SAUDI ARABIA")
    draw_refinery_scene(cv, 627, 185, 382, 80)
    cv.text(636, 270, "RAS TANURA HIT", INK, 3)
    cv.text(636, 298, "BRENT TOPS $94", INK, 3)
    cv.para(636, 326, "Houthis claim refinery attack; 4 drones shot down.", INK, 364, 1)

    panel(cv, 624, 350, 388, 172, "SEA - STRAIT OF HORMUZ")
    draw_tanker_scene(cv, 627, 379, 382, 80)
    cv.text(636, 454, "TANKERS HIT MINES", INK, 3)
    cv.text(636, 482, "TWO CATCH FIRE", INK, 3)
    cv.text(636, 506, "Ships explode in the strait, Iran says.", INK, 1)

    # ---- row 2: Cairo, Netanyahu, space
    panel(cv, 12, 534, 325, 266, "DISASTER - CAIRO")
    draw_cairo_scene(cv, 15, 563, 319, 110)
    cv.text(24, 680, "CAIRO TANKER", INK, 3)
    cv.text(24, 708, "FIRE: 30 DEAD", INK, 3)
    cv.para(24, 742, "Fuel tanker crash on the Ring Road; 25 hurt, cars burn.",
            INK, 301, 2)

    panel(cv, 349, 534, 326, 266, "JUSTICE - JERUSALEM")
    draw_court_scene(cv, 352, 563, 320, 110)
    cv.text(361, 680, "JUDGES: DROP", INK, 3)
    cv.text(361, 708, "THE CASE", INK, 3)
    cv.para(361, 742, "Court urges prosecutors to drop Netanyahu bribery case.",
            INK, 302, 2)

    panel(cv, 687, 534, 325, 266, "SPACE - TIANGONG")
    draw_space_scene(cv, 690, 563, 319, 120)
    cv.text(699, 690, "PAKISTAN IN", INK, 3)
    cv.text(699, 718, "ORBIT", INK, 3)
    cv.para(699, 748, "Shenzhou-24 docks; Ali is the first Pakistani in space.",
            INK, 301, 2)

    # ---- row 3: also today strip
    panel(cv, 12, 812, 1000, 150, "ALSO TODAY")
    cv.text(24, 852, "COLOMBIA FREES 76 HOSTAGES IN CARTAGENA SUPERMARKET SIEGE", INK, 2)
    cv.text(24, 878, "NORTH KOREA EXPELS SWISS ENVOY, SHUTS PYONGYANG OFFICE", INK, 2)
    cv.text(24, 904, "S&P PUTS NVIDIA ON CREDITWATCH NEGATIVE; SHARES FALL 4%", INK, 2)
    cv.text(24, 930, "GAZA STRIKE KILLS HAMAS OFFICIAL ABUELOUF AND HIS FAMILY", INK, 2)

    # footer
    cv.rect(12, 974, W - 24, 3, INK)
    cv.text_center(W // 2, 986, "TARIFFS - OIL - HORMUZ - CAIRO - NETANYAHU - SPACE", INK, 2)
    return cv


# ---------------------------------------------------------------- PNG writer
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.buf[y * cv.w * 3:(y + 1) * cv.w * 3])
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path}: {len(data)} bytes, {W}x{H}")


if __name__ == "__main__":
    main()
