#!/usr/bin/env python3
"""THE GLOBAL SUNDAY - one-page newspaper front page summing up the world news
of Sunday 22 November 2026. Pure Python standard library, no network, fully
deterministic: the same run always writes the same bytes to entry.png."""

import binascii
import math
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette ---
PAPER = (247, 241, 222)
PAPER2 = (238, 230, 203)
PAPER3 = (228, 218, 186)
INK = (26, 26, 26)
INK2 = (74, 74, 74)
GREY = (128, 128, 128)
LGREY = (196, 196, 196)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (193, 39, 45)
DRED = (140, 20, 25)
BLUE = (31, 78, 121)
NAVY = (16, 42, 67)
SKY = (135, 206, 235)
SKY2 = (168, 216, 240)
SEA = (0, 119, 182)
SEA2 = (0, 180, 216)
TEAL = (0, 128, 128)
GREEN = (46, 125, 50)
LGREEN = (139, 195, 74)
FOREST = (34, 90, 60)
GOLD = (212, 175, 55)
YELLOW = (255, 213, 74)
ORANGE = (230, 126, 34)
BROWN = (121, 85, 72)
SAND = (222, 184, 135)
MAROON = (128, 0, 32)
PURPLE = (106, 76, 147)
PINK = (233, 150, 180)
CREAM = (255, 248, 220)
DUSK = (52, 52, 96)
FLAME = (255, 110, 0)

TAG_COLORS = [RED, BLUE, TEAL, GREEN, ORANGE, PURPLE, MAROON, FOREST, NAVY, DRED]

# ------------------------------------------------------------- 5x7 font ---
# Each glyph is 7 rows of 5 bits, written as strings of 0/1.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}


def text_width(text, scale):
    """Pixel width of a string at the given scale."""
    return len(text) * 6 * scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width pixels."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Pix:
    """A 1024x1024 RGB framebuffer with flat-cartoon drawing primitives."""

    def __init__(self, w=W, h=H):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill(PAPER)

    def fill(self, color):
        r, g, b = color
        self.buf[:] = bytes((r, g, b)) * (self.w * self.h)

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def hline(self, x, y, length, color):
        if y < 0 or y >= self.h:
            return
        x0 = max(0, x)
        x1 = min(self.w, x + length)
        if x1 <= x0:
            return
        i = (y * self.w + x0) * 3
        self.buf[i:(y * self.w + x1) * 3] = bytes(color) * (x1 - x0)

    def vline(self, x, y, length, color):
        if x < 0 or x >= self.w:
            return
        y0 = max(0, y)
        y1 = min(self.h, y + length)
        for yy in range(y0, y1):
            self.px(x, yy, color)

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + (x1 - x0) * 3] = row

    def border(self, x, y, w, h, color, t=1):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def circle(self, cx, cy, r, color):
        if r <= 0:
            return
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.hline(cx - dx, cy + dy, 2 * dx + 1, color)

    def ring(self, cx, cy, r, color, t=2):
        if r <= 0:
            return
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            inner = int(math.sqrt(max(0, (r - t) * (r - t) - dy * dy))) if r - t > 0 else 0
            if abs(dy) < r - t:
                self.hline(cx - dx, cy + dy, dx - inner, color)
                self.hline(cx + inner, cy + dy, dx - inner + 1, color)
            else:
                self.hline(cx - dx, cy + dy, 2 * dx + 1, color)

    def ellipse(self, cx, cy, rx, ry, color):
        if rx <= 0 or ry <= 0:
            return
        for dy in range(-ry, ry + 1):
            dx = int(rx * math.sqrt(max(0.0, 1.0 - (dy * dy) / float(ry * ry))))
            self.hline(cx - dx, cy + dy, 2 * dx + 1, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.px(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def tri(self, x0, y0, x1, y1, x2, y2, color):
        pts = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            return
        for y in range(max(0, ay), min(self.h, cy + 1)):
            if y < by:
                t1 = (y - ay) / float(by - ay) if by != ay else 0.0
                xa = ax + (bx - ax) * t1
            else:
                t1 = (y - by) / float(cy - by) if cy != by else 0.0
                xa = bx + (cx - bx) * t1
            t2 = (y - ay) / float(cy - ay)
            xb = ax + (cx - ax) * t2
            lo, hi = (xa, xb) if xa <= xb else (xb, xa)
            self.hline(int(lo), y, int(hi) - int(lo) + 1, color)

    def poly(self, points, color):
        """Scanline fill of a simple polygon given as [(x, y), ...]."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        y0, y1 = max(0, min(ys)), min(self.h - 1, max(ys))
        n = len(points)
        for y in range(y0, y1 + 1):
            xs = []
            for i in range(n):
                x0, ya = points[i]
                x1, yb = points[(i + 1) % n]
                if (ya <= y < yb) or (yb <= y < ya):
                    t = (y - ya) / float(yb - ya)
                    xs.append(x0 + (x1 - x0) * t)
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.hline(int(xs[k]), y, int(xs[k + 1]) - int(xs[k]) + 1, color)

    def starburst(self, cx, cy, r, color, spikes=8):
        for k in range(spikes):
            ang = math.pi * 2 * k / spikes
            x1 = int(cx + math.cos(ang) * r)
            y1 = int(cy + math.sin(ang) * r)
            ang2 = ang + math.pi / spikes
            x2 = int(cx + math.cos(ang2) * r * 0.45)
            y2 = int(cy + math.sin(ang2) * r * 0.45)
            self.tri(cx, cy, x1, y1, x2, y2, color)

    def text(self, x, y, s, color, scale=1, bold=False):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale, scale, scale, color)
                        if bold:
                            self.rect(cx + col * scale + 1, y + row * scale, scale, scale, color)
            cx += 6 * scale
        return cx

    def text_c(self, cx, y, s, color, scale=1, bold=False):
        self.text(cx - text_width(s, scale) // 2, y, s, color, scale, bold)

    def arch(self, x, y, w, h, color):
        """Rounded-top (arch) filled shape: rectangle with a semicircular top."""
        r = w // 2
        self.rect(x, y + r, w, h - r, color)
        self.circle(x + r, y + r, r, color)

    def waves(self, x, y, w, h, color, amp=3, step=14):
        for xx in range(x, x + w, step):
            self.circle(xx + step // 2, y + h // 2, amp, color)


# ------------------------------------------------------------ illustrations ---
# Every painter draws a flat cartoon scene inside the box (x, y, w, h).
# v selects a colour/detail variant of the same motif.

def sc_missile(p, x, y, w, h, v=0):
    sky = DUSK if v == 0 else NAVY
    p.rect(x, y, w, h, sky)
    for sx, sy in ((12, 12), (38, 26), (70, 10), (88, 30)):
        p.px(x + w * sx // 100, y + h * sy // 100, WHITE)
        p.px(x + w * sx // 100 + 1, y + h * sy // 100, WHITE)
    p.rect(x, y + h * 78 // 100, w, h * 22 // 100, (38, 38, 58))
    bx, by = x + w // 2, y + h * 78 // 100
    p.circle(bx, by, h // 5, LGREY)
    p.ring(bx, by, h // 5, INK, 2)
    p.line(bx, by, bx - h // 4, by - h // 3, INK)
    p.line(bx, by, bx + h // 6, by - h // 4, INK)
    p.line(x + w // 8, y + h // 4, x + w * 3 // 8, y + h // 8, YELLOW)
    p.line(x + w // 8, y + h // 4 + 2, x + w * 3 // 8, y + h // 8 + 2, ORANGE)
    p.tri(x + w * 3 // 8, y + h // 8, x + w * 3 // 8 - 8, y + h // 8 + 2, x + w * 3 // 8 - 3, y + h // 8 + 10, ORANGE)
    p.line(x + w * 5 // 8, y + h // 3, x + w * 7 // 8, y + h // 6, YELLOW)
    p.line(x + w * 5 // 8, y + h // 3 + 2, x + w * 7 // 8, y + h // 6 + 2, ORANGE)
    p.tri(x + w * 7 // 8, y + h // 6, x + w * 7 // 8 - 8, y + h // 6 + 2, x + w * 7 // 8 - 3, y + h // 6 + 10, ORANGE)
    p.starburst(x + w * 82 // 100, y + h * 62 // 100, h // 7, FLAME)
    p.starburst(x + w * 82 // 100, y + h * 62 // 100, h // 12, YELLOW)
    for i, bh in enumerate((16, 24, 12, 20)):
        bx = x + w * (6 + i * 8) // 100
        p.rect(bx, y + h * 78 // 100 - h * bh // 100, w // 14, h * bh // 100, (24, 24, 40))
        p.rect(bx + 2, y + h * 78 // 100 - h * bh // 100 + 3, 2, 2, YELLOW)


def sc_climate(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SKY2)
    p.circle(x + w * 82 // 100, y + h * 18 // 100, h // 7, YELLOW)
    p.circle(x + w * 82 // 100, y + h * 18 // 100, h // 7 - 3, GOLD)
    p.circle(x + w // 2, y + h * 58 // 100, h // 3, SEA)
    p.ellipse(x + w * 42 // 100, y + h * 52 // 100, w // 10, h // 12, LGREEN)
    p.ellipse(x + w * 60 // 100, y + h * 66 // 100, w // 12, h // 14, FOREST)
    p.ellipse(x + w * 52 // 100, y + h * 42 // 100, w // 16, h // 16, LGREEN)
    p.rect(x + w // 8, y + h * 70 // 100, w // 10, h // 18, INK2)
    p.rect(x + w // 8 + w // 40, y + h * 64 // 100, w // 40, h // 8, GREY)
    p.circle(x + w * 16 // 100, y + h * 62 // 100, h // 14, LGREY)
    p.circle(x + w * 22 // 100, y + h * 58 // 100, h // 16, LGREY)
    p.rect(x + w * 72 // 100, y + h * 74 // 100, w // 22, h // 6, RED)
    p.rect(x + w * 72 // 100, y + h * 74 // 100, w // 11, h // 6, WHITE)
    p.rect(x, y + h * 88 // 100, w, h * 12 // 100, FOREST)


def sc_quake(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SKY2 if v == 0 else (244, 214, 170))
    p.tri(x, y + h, x + w // 3, y + h // 4, x + w * 2 // 3, y + h, GREY)
    p.tri(x + w // 3, y + h, x + w * 2 // 3, y + h // 5, x + w, y + h, (90, 90, 90))
    p.circle(x + w // 4, y + h // 6, h // 9, WHITE)
    p.rect(x + w // 8, y + h // 2, w // 7, h // 3, (176, 142, 110))
    p.rect(x + w // 8 + w // 28, y + h // 2 - h // 10, w // 7, h // 10, DRED)
    p.rect(x + w * 5 // 8, y + h * 58 // 100, w // 6, h // 4, (150, 120, 95))
    p.line(x + w // 5, y + h * 82 // 100, x + w // 3, y + h * 92 // 100, INK)
    p.line(x + w // 3, y + h * 92 // 100, x + w // 2, y + h * 84 // 100, INK)
    p.line(x + w // 2, y + h * 84 // 100, x + w * 2 // 3, y + h * 94 // 100, INK)
    p.line(x + w * 2 // 3, y + h * 94 // 100, x + w * 4 // 5, y + h * 86 // 100, INK)
    p.rect(x, y + h * 92 // 100, w, h * 8 // 100, BROWN)
    p.starburst(x + w * 78 // 100, y + h * 30 // 100, h // 9, RED)
    p.starburst(x + w * 78 // 100, y + h * 30 // 100, h // 16, YELLOW)


def sc_shipfire(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SKY)
    p.circle(x + w * 84 // 100, y + h * 16 // 100, h // 9, YELLOW)
    p.rect(x, y + h * 62 // 100, w, h * 38 // 100, SEA)
    p.waves(x, y + h * 62 // 100, w, h // 6, SEA2, 3, 16)
    p.poly([(x + w // 8, y + h * 62 // 100), (x + w * 7 // 8, y + h * 62 // 100),
            (x + w * 82 // 100, y + h * 76 // 100), (x + w // 7, y + h * 76 // 100)], DRED)
    p.rect(x + w // 5, y + h * 48 // 100, w // 9, h // 14, GOLD)
    p.rect(x + w // 3, y + h * 48 // 100, w // 9, h // 14, TEAL)
    p.rect(x + w * 47 // 100, y + h * 48 // 100, w // 9, h // 14, ORANGE)
    p.rect(x + w * 3 // 5, y + h * 40 // 100, w // 16, h // 10, WHITE)
    p.tri(x + w // 4, y + h * 48 // 100, x + w // 4 + w // 12, y + h * 30 // 100,
          x + w // 4 + w // 6, y + h * 48 // 100, FLAME)
    p.tri(x + w // 3, y + h * 48 // 100, x + w // 3 + w // 14, y + h * 34 // 100,
          x + w // 3 + w // 7, y + h * 48 // 100, YELLOW)
    p.circle(x + w // 4, y + h * 26 // 100, h // 12, GREY)
    p.circle(x + w // 3, y + h * 20 // 100, h // 10, LGREY)


def sc_cityfire(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, DUSK)
    p.circle(x + w * 86 // 100, y + h * 14 // 100, h // 10, (220, 220, 220))
    for i, bh in enumerate((42, 58, 34, 50, 62, 40)):
        bx = x + w * (6 + i * 15) // 100
        bw = w // 8
        p.rect(bx, y + h * 88 // 100 - h * bh // 100, bw, h * bh // 100, (30, 30, 46))
        p.rect(bx + bw // 4, y + h * 88 // 100 - h * bh // 100 + 4, 3, 3, YELLOW)
        p.rect(bx + bw // 2, y + h * 88 // 100 - h * bh // 100 + 10, 3, 3, YELLOW)
    p.tri(x + w // 4, y + h * 88 // 100, x + w // 4 + w // 12, y + h * 60 // 100,
          x + w // 4 + w // 6, y + h * 88 // 100, FLAME)
    p.tri(x + w // 2, y + h * 88 // 100, x + w // 2 + w // 14, y + h * 66 // 100,
          x + w // 2 + w // 7, y + h * 88 // 100, YELLOW)
    p.tri(x + w * 3 // 4, y + h * 88 // 100, x + w * 3 // 4 + w // 14, y + h * 70 // 100,
          x + w * 3 // 4 + w // 7, y + h * 88 // 100, ORANGE)
    p.circle(x + w // 3, y + h * 52 // 100, h // 12, GREY)
    p.circle(x + w * 2 // 3, y + h * 46 // 100, h // 10, LGREY)
    p.rect(x, y + h * 88 // 100, w, h * 12 // 100, BLACK)


def sc_bridges(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SKY2)
    p.rect(x, y + h * 66 // 100, w, h * 34 // 100, SEA)
    for i in range(3):
        bx = x + w * (8 + i * 30) // 100
        p.rect(bx, y + h * 30 // 100, w // 6, h * 36 // 100, (150, 120, 95))
        p.rect(bx + 3, y + h * 30 // 100 + 4, 3, 3, INK)
        p.rect(bx + 3, y + h * 30 // 100 + 12, 3, 3, INK)
    p.line(x, y + h * 66 // 100, x + w, y + h * 58 // 100, INK)
    p.line(x, y + h * 66 // 100, x + w, y + h * 66 // 100, INK)
    p.starburst(x + w * 70 // 100, y + h * 40 // 100, h // 8, FLAME)
    p.starburst(x + w * 70 // 100, y + h * 40 // 100, h // 14, YELLOW)
    p.circle(x + w * 30 // 100, y + h * 20 // 100, h // 12, WHITE)
    p.circle(x + w * 36 // 100, y + h * 16 // 100, h // 9, WHITE)


def sc_cartel(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SAND)
    p.circle(x + w * 82 // 100, y + h * 16 // 100, h // 8, YELLOW)
    p.rect(x, y + h * 72 // 100, w, h * 28 // 100, (196, 148, 96))
    p.rect(x + w // 8, y + h * 40 // 100, w // 22, h // 34, GREEN)
    p.rect(x + w // 8 - w // 40, y + h * 50 // 100, w // 12, h // 14, GREEN)
    p.circle(x + w // 2, y + h * 46 // 100, h // 6, GOLD)
    p.ring(x + w // 2, y + h * 46 // 100, h // 6, DRED, 2)
    p.starburst(x + w // 2, y + h * 46 // 100, h // 10, GOLD)
    p.circle(x + w // 3, y + h * 66 // 100, h // 9, GREY)
    p.ring(x + w // 3, y + h * 66 // 100, h // 9, INK, 2)
    p.circle(x + w * 2 // 3, y + h * 66 // 100, h // 9, GREY)
    p.ring(x + w * 2 // 3, y + h * 66 // 100, h // 9, INK, 2)
    p.line(x + w // 3, y + h * 66 // 100, x + w * 2 // 3, y + h * 66 // 100, INK)


def sc_diplomacy(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SKY2)
    p.rect(x, y + h * 74 // 100, w, h * 26 // 100, LGREEN)
    c1, c2 = (RED, (255, 153, 51)) if v == 0 else (BLUE, TEAL)
    p.vline(x + w // 4, y + h // 6, h // 2, INK)
    p.rect(x + w // 4, y + h // 6, w // 5, h // 6, c1)
    p.rect(x + w // 4, y + h // 6 + h // 12, w // 5, h // 12, WHITE)
    p.vline(x + w * 3 // 4, y + h // 6, h // 2, INK)
    p.rect(x + w * 3 // 4, y + h // 6, w // 5, h // 6, c2)
    p.rect(x + w * 3 // 4, y + h // 6 + h // 12, w // 5, h // 12, WHITE)
    p.rect(x + w * 3 // 8, y + h * 68 // 100, w // 4, h // 6, DRED)
    px, py = x + w // 2, y + h * 34 // 100
    p.ellipse(px, py, w // 6, h // 14, WHITE)
    p.tri(px + w // 8, py - h // 14, px + w // 5, py - h // 5, px + w // 8, py, WHITE)
    p.tri(px - w // 16, py + h // 14, px - w // 8, py + h // 4, px + w // 16, py + h // 14, WHITE)
    p.tri(px + w // 6, py, px + w // 4, py - h // 16, px + w // 4, py + h // 16, WHITE)
    p.line(px - w // 6, py, px - w // 4, py, LGREY)
    p.circle(x + w * 86 // 100, y + h * 12 // 100, h // 10, YELLOW)


def sc_parliament(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SKY)
    p.rect(x, y + h * 76 // 100, w, h * 24 // 100, LGREEN)
    dome = TEAL if v == 0 else MAROON
    p.arch(x + w * 38 // 100, y + h * 18 // 100, w // 4, h // 4, dome)
    p.rect(x + w * 30 // 100, y + h * 40 // 100, w * 2 // 5, h // 4, WHITE)
    for i in range(4):
        cx = x + w * (34 + i * 10) // 100
        p.rect(cx, y + h * 42 // 100, w // 28, h // 5, LGREY)
    p.rect(x + w * 26 // 100, y + h * 64 // 100, w * 48 // 100, h // 6, LGREY)
    p.rect(x + w * 22 // 100, y + h * 70 // 100, w * 56 // 100, h // 6, GREY)
    p.vline(x + w // 2, y + h // 10, h // 10, INK)
    p.rect(x + w // 2, y + h // 10, w // 8, h // 12, RED)


def sc_protest(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SKY2 if v == 0 else (250, 226, 190))
    p.rect(x, y + h * 70 // 100, w, h * 30 // 100, (150, 150, 150))
    cols = [RED, BLUE, GOLD, TEAL] if v == 0 else [ORANGE, PURPLE, GREEN, RED]
    for i in range(5):
        hx = x + w * (10 + i * 18) // 100
        p.circle(hx, y + h * 62 // 100, h // 11, (222, 184, 135) if i % 2 == 0 else (180, 130, 95))
        p.rect(hx - w // 16, y + h * 70 // 100, w // 8, h // 6, cols[i % 4])
    for i, (fx, txt) in enumerate(((14, 0), (46, 1), (76, 2))):
        px = x + w * fx // 100
        p.vline(px, y + h * 26 // 100, h // 4, INK)
        p.rect(px - w // 12, y + h * 14 // 100, w // 6, h // 12, cols[(i + 1) % 4])
        p.border(px - w // 12, y + h * 14 // 100, w // 6, h // 12, INK, 1)


def sc_oilcourt(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SKY)
    p.rect(x, y + h * 70 // 100, w, h * 30 // 100, SEA2)
    p.line(x + w // 4, y + h * 70 // 100, x + w // 4 + w // 10, y + h * 20 // 100, INK)
    p.line(x + w * 3 // 4, y + h * 70 // 100, x + w * 3 // 4 - w // 10, y + h * 20 // 100, INK)
    p.line(x + w // 4 + w // 20, y + h * 55 // 100, x + w * 3 // 4 - w // 20, y + h * 55 // 100, INK)
    p.line(x + w // 4 + w // 14, y + h * 40 // 100, x + w * 3 // 4 - w // 14, y + h * 40 // 100, INK)
    p.circle(x + w // 2, y + h * 18 // 100, h // 12, BLACK)
    p.circle(x + w // 2, y + h * 18 // 100, h // 18, WHITE)
    p.circle(x + w * 82 // 100, y + h * 60 // 100, h // 10, GOLD)
    p.text(x + w * 82 // 100 - 3, y + h * 60 // 100 - 3, "$", INK, 1, True)


def sc_banknote(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, PAPER3)
    note = GREEN if v == 0 else BLUE
    p.rect(x + w // 10, y + h * 22 // 100, w * 4 // 5, h // 3, note)
    p.border(x + w // 10, y + h * 22 // 100, w * 4 // 5, h // 3, WHITE, 2)
    p.circle(x + w // 4, y + h * 38 // 100, h // 8, (222, 184, 135))
    p.circle(x + w // 4, y + h * 38 // 100, h // 8 - 2, (200, 160, 110))
    p.text(x + w * 62 // 100, y + h * 30 // 100, "$", WHITE, 2, True)
    p.rect(x + w // 6, y + h * 62 // 100, w * 2 // 3, h // 4, note)
    p.border(x + w // 6, y + h * 62 // 100, w * 2 // 3, h // 4, WHITE, 2)
    p.circle(x + w // 3, y + h * 74 // 100, h // 9, (222, 184, 135))
    p.circle(x + w * 72 // 100, y + h * 70 // 100, h // 8, GOLD)
    p.text(x + w * 72 // 100 - 3, y + h * 70 // 100 - 3, "$", INK, 1, True)


def sc_health(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, WHITE)
    cross = RED if v == 0 else GREEN
    p.rect(x + w // 8, y + h * 16 // 100, w // 5, h // 4, cross)
    p.rect(x + w // 8 + w // 20, y + h * 8 // 100, w // 10, h // 5, cross)
    p.rect(x + w * 58 // 100, y + h * 55 // 100, w // 3, h // 4, LGREY)
    p.rect(x + w * 58 // 100, y + h * 55 // 100, w // 3, h // 8, cross)
    p.circle(x + w * 72 // 100, y + h * 24 // 100, h // 8, TEAL)
    for k in range(6):
        ang = math.pi * 2 * k / 6
        p.line(x + w * 72 // 100, y + h * 24 // 100,
               int(x + w * 72 // 100 + math.cos(ang) * h // 5),
               int(y + h * 24 // 100 + math.sin(ang) * h // 5), TEAL)
    p.rect(x, y + h * 86 // 100, w, h * 14 // 100, LGREEN)


def sc_ambush(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, (255, 213, 128) if v == 0 else DUSK)
    p.circle(x + w * 80 // 100, y + h * 16 // 100, h // 8, YELLOW if v == 0 else WHITE)
    p.ellipse(x + w // 4, y + h * 78 // 100, w // 2, h // 5, SAND)
    p.ellipse(x + w * 3 // 4, y + h * 84 // 100, w // 2, h // 5, (196, 148, 96))
    p.tri(x + w // 2, y + h * 30 // 100, x + w // 2 - w // 12, y + h * 58 // 100,
          x + w // 2 + w // 12, y + h * 58 // 100, RED)
    p.border(x + w // 2 - w // 12, y + h * 30 // 100, w // 6, h // 7, RED, 1)
    p.text(x + w // 2 - 3, y + h * 40 // 100, "!", WHITE, 2, True)
    p.starburst(x + w // 4, y + h * 55 // 100, h // 10, ORANGE)
    p.starburst(x + w * 3 // 4, y + h * 48 // 100, h // 12, FLAME)


def sc_talks(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, PAPER2)
    for i in range(4):
        fx = x + w * (12 + i * 24) // 100
        p.vline(fx, y + h // 6, h // 5, INK)
        p.rect(fx, y + h // 6, w // 12, h // 10, [RED, BLUE, GREEN, GOLD][i])
    p.rect(x + w // 10, y + h * 52 // 100, w * 4 // 5, h // 8, BROWN)
    for i in range(4):
        hx = x + w * (18 + i * 22) // 100
        p.circle(hx, y + h * 44 // 100, h // 12, (222, 184, 135) if i % 2 == 0 else (150, 100, 70))
        p.rect(hx - w // 16, y + h * 52 // 100, w // 8, h // 6, [NAVY, MAROON, TEAL, PURPLE][i])
    p.rect(x + w * 40 // 100, y + h * 68 // 100, w // 5, h // 6, WHITE)
    p.border(x + w * 40 // 100, y + h * 68 // 100, w // 5, h // 6, INK, 1)


def sc_tech(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, NAVY)
    if v == 2:
        cx, cy = x + w // 2, y + h // 2
        p.rect(cx - w // 8, cy - h // 10, w // 4, h // 5, LGREY)
        p.circle(cx, cy, h // 7, INK)
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            p.line(cx + dx * w // 8, cy + dy * h // 10, cx + dx * w // 5, cy + dy * h // 5, LGREY)
            p.circle(cx + dx * w // 5, cy + dy * h // 5, h // 16, LGREY)
        return
    p.rect(x + w // 4, y + h // 4, w // 2, h // 2, INK)
    p.border(x + w // 4, y + h // 4, w // 2, h // 2, GOLD, 2)
    p.rect(x + w * 38 // 100, y + h * 38 // 100, w // 4, h // 4, TEAL)
    for i in range(3):
        p.vline(x + w * (32 + i * 18) // 100, y + h // 8, h // 8, GOLD)
        p.vline(x + w * (32 + i * 18) // 100, y + h * 3 // 4, h // 8, GOLD)
        p.hline(x + w // 8, y + h * (32 + i * 18) // 100, w // 8, GOLD)
        p.hline(x + w * 3 // 4, y + h * (32 + i * 18) // 100, w // 8, GOLD)
    p.circle(x + w * 82 // 100, y + h * 16 // 100, 2, YELLOW)
    p.circle(x + w * 14 // 100, y + h * 82 // 100, 2, YELLOW)


def sc_energy(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SKY2)
    p.poly([(x + w // 8, y + h * 78 // 100), (x + w // 8 + w // 14, y + h * 30 // 100),
            (x + w // 8 + w // 7, y + h * 30 // 100), (x + w // 8 + w // 5, y + h * 78 // 100)], GREY)
    p.poly([(x + w * 3 // 8, y + h * 78 // 100), (x + w * 3 // 8 + w // 14, y + h * 38 // 100),
            (x + w * 3 // 8 + w // 7, y + h * 38 // 100), (x + w * 3 // 8 + w // 5, y + h * 78 // 100)], LGREY)
    p.rect(x + w * 3 // 4, y + h * 50 // 100, w // 8, h // 4, BROWN)
    p.rect(x + w * 3 // 4 - w // 40, y + h * 44 // 100, w // 5, h // 6, BROWN)
    p.poly([(x + w * 68 // 100, y + h * 10 // 100), (x + w * 60 // 100, y + h * 30 // 100),
            (x + w * 68 // 100, y + h * 30 // 100), (x + w * 60 // 100, y + h * 52 // 100),
            (x + w * 76 // 100, y + h * 22 // 100), (x + w * 68 // 100, y + h * 22 // 100),
            (x + w * 76 // 100, y + h * 10 // 100)], YELLOW)
    p.rect(x, y + h * 78 // 100, w, h * 22 // 100, FOREST)


def sc_aid(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SKY2)
    p.rect(x, y + h * 72 // 100, w, h * 28 // 100, SAND)
    p.rect(x + w // 8, y + h * 44 // 100, w // 4, h // 4, (160, 110, 60))
    p.border(x + w // 8, y + h * 44 // 100, w // 4, h // 4, INK, 1)
    p.rect(x + w // 8 + w // 8 - 2, y + h * 44 // 100, 4, h // 4, WHITE)
    p.rect(x + w * 3 // 8, y + h * 54 // 100, w // 4, h // 5, (140, 95, 50))
    p.border(x + w * 3 // 8, y + h * 54 // 100, w // 4, h // 5, INK, 1)
    p.circle(x + w * 78 // 100, y + h * 30 // 100, h // 9, SEA)
    p.tri(x + w * 78 // 100 - h // 9, y + h * 30 // 100, x + w * 78 // 100 + h // 9,
          y + h * 30 // 100, x + w * 78 // 100, y + h * 8 // 100, SEA)
    p.circle(x + w * 78 // 100, y + h * 30 // 100, h // 14, WHITE)


def sc_market(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, WHITE)
    base = y + h * 78 // 100
    for i, bh in enumerate((20, 34, 26, 48, 40, 62)):
        bx = x + w * (8 + i * 14) // 100
        p.rect(bx, base - h * bh // 100, w // 10, h * bh // 100, GREEN if i % 2 == 0 else TEAL)
    p.line(x + w // 10, base - h * 55 // 100, x + w * 88 // 100, base - h * 18 // 100, RED)
    p.tri(x + w * 88 // 100, base - h * 18 // 100, x + w * 88 // 100 - 8, base - h * 18 // 100 - 4,
          x + w * 88 // 100 - 8, base - h * 18 // 100 + 4, RED)
    p.circle(x + w // 4, y + h * 16 // 100, h // 9, GOLD)
    p.text(x + w // 4 - 3, y + h * 16 // 100 - 3, "$", INK, 1, True)
    p.circle(x + w * 72 // 100, y + h * 14 // 100, h // 11, GOLD)
    p.text(x + w * 72 // 100 - 3, y + h * 14 // 100 - 3, "$", INK, 1, True)


def sc_prison(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SKY2)
    p.rect(x, y + h * 68 // 100, w, h * 32 // 100, GREY)
    p.rect(x + w // 8, y + h * 34 // 100, w * 3 // 4, h // 4, (170, 170, 170))
    for i in range(6):
        p.vline(x + w * (14 + i * 13) // 100, y + h * 30 // 100, h * 38 // 100, INK)
    p.rect(x + w * 3 // 4, y + h * 18 // 100, w // 8, h // 3, BROWN)
    p.tri(x + w * 3 // 4 - w // 40, y + h * 18 // 100, x + w * 3 // 4 + w // 10,
          y + h * 18 // 100, x + w * 3 // 4 + w // 20, y + h * 8 // 100, DRED)
    p.circle(x + w * 16 // 100, y + h * 16 // 100, h // 10, YELLOW)


def sc_election(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, PAPER2)
    p.rect(x + w * 28 // 100, y + h * 34 // 100, w * 44 // 100, h // 3, BLUE)
    p.border(x + w * 28 // 100, y + h * 34 // 100, w * 44 // 100, h // 3, INK, 2)
    p.rect(x + w * 40 // 100, y + h * 28 // 100, w // 5, h // 12, WHITE)
    p.border(x + w * 40 // 100, y + h * 28 // 100, w // 5, h // 12, INK, 1)
    p.line(x + w * 42 // 100, y + h * 34 // 100, x + w * 46 // 100, y + h * 40 // 100, RED)
    p.line(x + w * 46 // 100, y + h * 40 // 100, x + w * 56 // 100, y + h * 24 // 100, RED)
    for i in range(4):
        hx = x + w * (16 + i * 22) // 100
        p.circle(hx, y + h * 78 // 100, h // 12, (222, 184, 135) if i % 2 == 0 else (150, 100, 70))
        p.rect(hx - w // 16, y + h * 84 // 100, w // 8, h // 8, [RED, BLUE, GREEN, GOLD][i])


def sc_plane(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SKY)
    p.circle(x + w * 16 // 100, y + h * 18 // 100, h // 8, WHITE)
    p.circle(x + w * 22 // 100, y + h * 14 // 100, h // 10, WHITE)
    p.circle(x + w * 28 // 100, y + h * 18 // 100, h // 8, WHITE)
    cx, cy = x + w // 2, y + h // 2
    if v == 1:
        p.tri(cx - w // 4, cy, cx + w // 4, cy - h // 10, cx + w // 4, cy + h // 10, GREY)
        p.tri(cx, cy, cx - w // 8, cy - h // 4, cx + w // 12, cy - h // 12, LGREY)
        p.tri(cx, cy, cx - w // 8, cy + h // 4, cx + w // 12, cy + h // 12, LGREY)
        p.line(cx - w // 4, cy, cx - w // 3, cy, ORANGE)
    else:
        p.ellipse(cx, cy, w // 4, h // 10, WHITE)
        p.tri(cx + w // 6, cy - h // 10, cx + w // 4, cy - h // 4, cx + w // 6, cy, WHITE)
        p.tri(cx - w // 12, cy + h // 10, cx - w // 6, cy + h // 4, cx + w // 12, cy + h // 10, WHITE)
        p.line(cx - w // 4, cy, cx - w // 3, cy, WHITE)
    p.line(x + w // 8, y + h * 78 // 100, x + w * 7 // 8, y + h * 78 // 100, WHITE)
    p.line(x + w // 8, y + h * 78 // 100, x + w // 4, y + h * 72 // 100, WHITE)


def sc_navy(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SKY2)
    p.rect(x, y + h * 64 // 100, w, h * 36 // 100, SEA)
    p.waves(x, y + h * 64 // 100, w, h // 6, SEA2, 3, 16)
    p.poly([(x + w // 6, y + h * 64 // 100), (x + w * 5 // 6, y + h * 64 // 100),
            (x + w * 78 // 100, y + h * 78 // 100), (x + w // 5, y + h * 78 // 100)], NAVY)
    p.rect(x + w // 4, y + h * 44 // 100, w // 8, h // 5, NAVY)
    p.rect(x + w * 3 // 8, y + h * 50 // 100, w // 8, h // 6, NAVY)
    p.vline(x + w // 2, y + h * 26 // 100, h // 5, INK)
    p.rect(x + w // 2, y + h * 26 // 100, w // 10, h // 10, RED)
    p.circle(x + w * 82 // 100, y + h * 16 // 100, h // 10, YELLOW)


def sc_court(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, PAPER2)
    p.vline(x + w // 2, y + h * 20 // 100, h // 2, GOLD)
    p.hline(x + w // 4, y + h * 22 // 100, w // 2, GOLD)
    p.line(x + w // 4, y + h * 22 // 100, x + w // 4 - w // 12, y + h * 46 // 100, GOLD)
    p.line(x + w // 4, y + h * 22 // 100, x + w // 4 + w // 12, y + h * 46 // 100, GOLD)
    p.ellipse(x + w // 4, y + h * 46 // 100, w // 10, h // 16, GOLD)
    p.line(x + w * 3 // 4, y + h * 22 // 100, x + w * 3 // 4 - w // 12, y + h * 46 // 100, GOLD)
    p.line(x + w * 3 // 4, y + h * 22 // 100, x + w * 3 // 4 + w // 12, y + h * 46 // 100, GOLD)
    p.ellipse(x + w * 3 // 4, y + h * 46 // 100, w // 10, h // 16, GOLD)
    p.rect(x + w * 3 // 8, y + h * 72 // 100, w // 4, h // 6, BROWN)
    p.rect(x + w * 30 // 100, y + h * 80 // 100, w * 2 // 5, h // 8, BROWN)


def sc_books(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SKY2)
    cols = [RED, BLUE, GREEN, GOLD, PURPLE]
    for i in range(5):
        bx = x + w * (10 + i * 16) // 100
        bh = h * (34 + (i % 3) * 8) // 100
        p.rect(bx, y + h * 78 // 100 - bh, w // 8, bh, cols[i])
        p.rect(bx, y + h * 78 // 100 - bh, w // 8, 3, WHITE)
    p.rect(x, y + h * 78 // 100, w, h // 6, BROWN)
    p.poly([(x + w // 2 - w // 6, y + h * 22 // 100), (x + w // 2, y + h * 10 // 100),
            (x + w // 2 + w // 6, y + h * 22 // 100), (x + w // 2, y + h * 34 // 100)], INK)
    p.rect(x + w // 2 - w // 24, y + h * 30 // 100, w // 12, h // 10, INK)
    p.line(x + w // 2 + w // 6, y + h * 22 // 100, x + w // 2 + w // 6, y + h * 40 // 100, GOLD)
    p.circle(x + w // 2 + w // 6, y + h * 42 // 100, 3, GOLD)


def sc_swim(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, SKY)
    p.rect(x, y + h * 58 // 100, w, h * 42 // 100, SEA)
    p.waves(x, y + h * 58 // 100, w, h // 5, SEA2, 3, 14)
    p.waves(x, y + h * 72 // 100, w, h // 5, WHITE, 2, 18)
    cx, cy = x + w // 2, y + h * 52 // 100
    p.circle(cx, cy, h // 9, (222, 184, 135))
    p.circle(cx, cy - h // 12, h // 11, RED)
    p.line(cx - w // 8, cy + h // 12, cx + w // 8, cy - h // 12, (222, 184, 135))
    p.line(cx - w // 8, cy + h // 6, cx + w // 8, cy + h // 24, (222, 184, 135))
    p.circle(x + w * 84 // 100, y + h * 14 // 100, h // 9, YELLOW)


def sc_sport(p, x, y, w, h, v=0):
    p.rect(x, y, w, h, LGREEN)
    p.rect(x, y + h * 70 // 100, w, h * 30 // 100, GREEN)
    p.hline(x, y + h * 70 // 100, w, WHITE)
    cx, cy = x + w // 2, y + h * 38 // 100
    if v == 1:
        p.circle(cx, cy, h // 6, YELLOW)
        p.ring(cx, cy, h // 6, WHITE, 2)
        p.line(cx - w // 4, cy + h // 4, cx + w // 4, cy + h // 4, WHITE)
    elif v == 2:
        p.ellipse(cx, cy, w // 5, h // 8, (139, 69, 19))
        p.hline(cx - w // 5, cy, w // 5 * 2, WHITE)
    elif v == 3:
        p.circle(cx, cy, h // 6, WHITE)
        p.circle(cx, cy - h // 12, 3, INK)
        p.circle(cx - h // 12, cy + h // 14, 3, INK)
        p.circle(cx + h // 12, cy + h // 14, 3, INK)
    elif v == 4:
        p.circle(cx, cy, h // 7, DRED)
        p.line(cx - w // 4, cy + h // 5, cx + w // 4, cy + h // 5, (200, 170, 120))
        p.rect(cx + w // 5, cy + h // 5 - 2, w // 8, 4, (200, 170, 120))
    else:
        p.circle(cx, cy, h // 6, WHITE)
        p.circle(cx, cy, h // 12, INK)
        p.circle(cx, cy, 2, WHITE)
    p.rect(x + w * 76 // 100, y + h * 14 // 100, w // 10, h // 8, GOLD)
    p.rect(x + w * 76 // 100 + w // 40, y + h * 14 // 100 - h // 10, w // 20, h // 10, GOLD)


SCENES = {
    "missile": sc_missile, "climate": sc_climate, "quake": sc_quake,
    "shipfire": sc_shipfire, "cityfire": sc_cityfire, "bridges": sc_bridges,
    "cartel": sc_cartel, "diplomacy": sc_diplomacy, "parliament": sc_parliament,
    "protest": sc_protest, "oilcourt": sc_oilcourt, "banknote": sc_banknote,
    "health": sc_health, "ambush": sc_ambush, "talks": sc_talks,
    "tech": sc_tech, "energy": sc_energy, "aid": sc_aid, "market": sc_market,
    "prison": sc_prison, "election": sc_election, "plane": sc_plane,
    "navy": sc_navy, "court": sc_court, "books": sc_books, "swim": sc_swim,
    "sport": sc_sport,
}


# ----------------------------------------------------------------- stories ---
# (tag, headline, caption, scene, variant). All verified against live
# reporting of 22 November 2026 (and the weekend's news it carried).

HERO = [
    ("MIDDLE EAST",
     "IRAN HITS US BASES IN BAHRAIN",
     "IRGC missiles and drones strike Patriot radars; Bahrain says a plant was hit and defences downed the rest.",
     "missile", 0),
    ("CLIMATE",
     "COP31 DRAFT DROPS FOSSIL FUELS",
     "Antalya talks drag on as the new text erases coal, oil and gas and admits a 1.5C overshoot.",
     "climate", 0),
    ("DISASTER",
     "PERU QUAKE M6.7 SHAKES THE ANDES",
     "Lima residents flee into the streets; no damage or casualties reported so far.",
     "quake", 0),
]

SECOND = [
    ("BALTIC",
     "SPARTA II BURNS AFTER DRONE HIT",
     "Russian cargo ship ablaze in the Gulf of Finland; crew evacuated.",
     "shipfire", 0),
    ("UKRAINE",
     "KRYVYI RIH: 2 KILLED, 60 HURT",
     "Triple-tap strike hits Zelenskyy's hometown; rescuers targeted.",
     "cityfire", 0),
    ("MEXICO",
     "EL CHAPO ISIDRO CAUGHT IN SINALOA",
     "Troops seize the cartel kingpin after a US tip; gunfire erupts.",
     "cartel", 0),
    ("ASIA",
     "NEPAL PM LANDS IN DELHI",
     "Balendra Shah begins a two-day state visit; talks with Modi on Monday.",
     "diplomacy", 0),
]

GRID = [
    ("ISRAEL: EISENKOT TO FORM GOVT", "parliament", 0),
    ("FRANCE: 4TH WEEKEND OF PROTESTS", "protest", 0),
    ("NORWAY COURT VOIDS OIL LICENCES", "oilcourt", 0),
    ("GHANA UNVEILS HERITAGE BANKNOTES", "banknote", 0),
    ("KENYA FREES LAST EBOLA PATIENT", "health", 0),
    ("AL-SHABAAB CLAIMS AMBUSH DEATHS", "ambush", 0),
    ("SUDAN: REBELS SEIZE BAU REGION", "ambush", 1),
    ("UN: KILLER-ROBOT RULES BY 2028", "tech", 0),
    ("MYANMAR: M4.1 QUAKE AT DAWN", "quake", 1),
    ("BASRA PLANT FIRE KILLS 4", "energy", 0),
    ("GAZA: 4 NATIONS URGE AID ACCESS", "aid", 0),
    ("VENEZUELA: $12BN OIL CASH TRAIL", "market", 0),
    ("HAITI INKS PRISON DEAL WITH EL SALVADOR", "prison", 0),
    ("SAO TOME: RAMOS BACK AS PM", "parliament", 1),
    ("TIGRAY MAYOR VOWS VOTE IN 6 MONTHS", "election", 0),
    ("SAHEL STATES TALK TO ECOWAS AGAIN", "talks", 0),
    ("KENYA WINS 293,600 SAUDI JOBS", "plane", 0),
    ("NIGERIA STARTS BUILDING WARSHIPS", "navy", 0),
    ("DRC SIGNS CONSTITUTION REFORM LAW", "court", 0),
    ("S. AFRICA: ANTI-MIGRANT RALLY BARRED", "protest", 1),
    ("DENMARK EXPELS RUSSIAN ATTACHE", "diplomacy", 1),
    ("POLAND: RUSSIAN MISSILES HIT LAND", "missile", 1),
    ("HEGSETH CURBS US-CANADA DEFENCE", "talks", 1),
    ("TRUMP: BRING BACK NVIDIA'S HUANG", "tech", 1),
    ("ECB HUNTS NEW CHIEF AS LAGARDE GOES", "banknote", 1),
    ("INDIA: 11 DIE FROM TOXIC ALCOHOL", "health", 1),
    ("CROATIA RALLIES OVER HOSPITAL DEATH", "protest", 0),
    ("TAIWAN TURNS TO DRONE WARFARE", "tech", 2),
    ("S. KOREA: $75,000 EXAM-TIP REWARD", "books", 0),
    ("UK SWIMMER DIVES IN HORMUZ", "swim", 0),
    ("ALCARAZ FACES ZVEREV FOR ATP CROWN", "sport", 1),
    ("FRANCE INTO RUGBY FINAL VS BOKS", "sport", 2),
    ("EVANILSON SCORES IN 6TH STRAIGHT", "sport", 3),
    ("CRICKET: SMITH OUT OF DECIDER", "sport", 4),
    ("MOSCOW HITS 3 KYIV BRIDGES", "bridges", 0),
    ("GRIPEN FAILS TO DOWN RUSSIAN MISSILE", "plane", 1),
]

TICKER = ("ALSO TODAY: IOWA COURT HALTS TOXIC BARREL BLAST | AWAR ODHIANG "
          "NAMED MODEL OF THE YEAR | TYLA, TEMS AND KIDJO LEAD GRAMMY HOPES "
          "| DEPARDIEU UNDER INVESTIGATION")

TOTAL_STORIES = len(HERO) + len(SECOND) + len(GRID) + 4


# ------------------------------------------------------------------ layout ---
def chip(p, x, y, tag, color):
    w = text_width(tag, 1) + 10
    p.rect(x, y, w, 13, color)
    p.text(x + 5, y + 3, tag, WHITE, 1, True)


def round_top(p, x, y, w, r):
    """Round the two top corners of an illustration box with paper discs."""
    p.circle(x, y, r, PAPER)
    p.circle(x + w, y, r, PAPER)


def hero_card(p, x, y, w, h, story):
    tag, headline, caption, scene, v = story
    p.rect(x, y, w, h, PAPER2)
    p.border(x, y, w, h, INK, 1)
    SCENES[scene](p, x + 1, y + 1, w - 2, 150, v)
    round_top(p, x + 1, y + 1, w - 2, 12)
    chip(p, x + 8, y + 8, tag, RED)
    p.rect(x, y + 151, w, 3, RED)
    lines = wrap_text(headline, w - 16, 3)[:2]
    yy = y + 162
    for ln in lines:
        p.text(x + 8, yy, ln, INK, 3, True)
        yy += 24
    clines = wrap_text(caption.upper(), w - 16, 1)[:3]
    yy += 4
    for ln in clines:
        p.text(x + 8, yy, ln, INK2, 1)
        yy += 10


def second_card(p, x, y, w, h, story):
    tag, headline, caption, scene, v = story
    p.rect(x, y, w, h, PAPER2)
    p.border(x, y, w, h, INK, 1)
    SCENES[scene](p, x + 1, y + 1, w - 2, 96, v)
    round_top(p, x + 1, y + 1, w - 2, 8)
    chip(p, x + 6, y + 6, tag, BLUE)
    p.rect(x, y + 97, w, 2, BLUE)
    lines = wrap_text(headline, w - 12, 2)[:2]
    yy = y + 106
    for ln in lines:
        p.text(x + 6, yy, ln, INK, 2, True)
        yy += 17
    clines = wrap_text(caption.upper(), w - 12, 1)[:2]
    yy += 3
    for ln in clines:
        p.text(x + 6, yy, ln, INK2, 1)
        yy += 10


def grid_card(p, x, y, w, h, headline, scene, v, idx):
    color = TAG_COLORS[idx % len(TAG_COLORS)]
    p.rect(x, y, w, h, PAPER)
    p.rect(x, y, w, 3, color)
    p.border(x, y, w, h, INK, 1)
    SCENES[scene](p, x + 5, y + 8, 44, 44, v)
    p.border(x + 5, y + 8, 44, 44, color, 2)
    lines = wrap_text(headline, w - 60, 1)[:3]
    yy = y + 8
    for ln in lines:
        p.text(x + 55, yy, ln, INK, 1, True)
        yy += 10


def build():
    p = Pix()
    p.border(0, 0, W, H, INK, 6)
    # Masthead.
    p.text_c(W // 2, 16, "THE GLOBAL SUNDAY", INK, 5, True)
    p.rect(14, 62, W - 28, 2, RED)
    p.text(14, 72, "VOL. I - NO. 326", INK2, 1, True)
    p.text_c(W // 2, 72, "SUNDAY 22 NOVEMBER 2026", RED, 2, True)
    p.text(W - 14 - text_width("ONE PAGE - ONE DAY", 1), 72, "ONE PAGE - ONE DAY", INK2, 1, True)
    p.rect(14, 94, W - 28, 2, INK)
    # Hero row: 3 big stories.
    for i, story in enumerate(HERO):
        hero_card(p, 10 + i * 337, 106, 329, 276, story)
    # Second row: 4 stories.
    for i, story in enumerate(SECOND):
        second_card(p, 10 + i * 253, 386, 245, 194, story)
    # Grid: 6 x 6 small stories.
    for r in range(6):
        for c in range(6):
            idx = r * 6 + c
            headline, scene, v = GRID[idx]
            grid_card(p, 10 + c * 168, 584 + r * 58, 162, 58, headline, scene, v, idx)
    # Ticker.
    p.rect(10, 936, 1004, 28, INK)
    tlines = wrap_text(TICKER, 990, 1)
    yy = 942
    for ln in tlines[:2]:
        p.text_c(W // 2, yy, ln, WHITE, 1)
        yy += 10
    # Footer.
    foot = ("THE GLOBAL SUNDAY  -  SUNDAY 22 NOVEMBER 2026  -  %d STORIES FROM "
            "EVERY CONTINENT  -  DRAWN IN PURE PYTHON" % TOTAL_STORIES)
    p.text_c(W // 2, 978, foot, INK2, 1)
    p.text_c(W // 2, 994, "THE WORLD IN ONE DAY", INK, 1, True)
    return p


# --------------------------------------------------------------------- png ---
def _chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF))


def save_png(pix, path):
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += pix.buf[yy * W * 3:(yy + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
           _chunk(b"IDAT", comp) + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    pix = build()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not outdir:
        outdir = "/output" if os.path.isdir("/output") else "out"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = save_png(pix, path)
    print("wrote %s (%d bytes, %d stories)" % (path, size, TOTAL_STORIES))


if __name__ == "__main__":
    main()
