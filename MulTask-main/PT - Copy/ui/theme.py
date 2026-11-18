"""Colours, font preferences, layout constants and button colour sets."""

from __future__ import annotations

from typing import Dict, List, Tuple


APP_TITLE = "MultiTask - Banker's Algorithm Simulator"

WHITE = "#FFFFFF"
INK = "#1B2237"
MUTED = "#667085"
LINE = "#E3E7F0"
LINE_STRONG = "#B7BFD3"
ACCENT = "#4F46E5"
ACCENT_DARK = "#4338CA"
ACCENT_PRESS = "#3730A3"
ACCENT_SOFT = "#EEF0FF"
GOOD = "#16A34A"
GOOD_SOFT = "#DCFCE7"
BAD = "#DC2626"
CHIP = "#EEF0F6"
STRIP_BG = "#F5F7FC"
SELECT = "#C7D2FE"

BG_TOP = "#F8F9FD"
BG_BOTTOM = "#E3E8F5"
DECOR_A = "#E4E7FB"
DECOR_B = "#EBEEFB"
DECOR_RING = "#D7DDF4"
CARD_BORDER = "#E3E7F0"
CARD_SHADOW = "#D1D8E8"

HEAD_LEFT = "#1E1B4B"
HEAD_RIGHT = "#4F46E5"
HEAD_SUB = "#C7D2FE"

TERM_BG = "#111827"
TERM_FG = "#E5E7EB"
TERM_GOOD = "#4ADE80"
TERM_BAD = "#F87171"
TERM_HEAD = "#A5B4FC"
TERM_RULE = "#374151"
TERM_SELECT = "#334155"

UI_FAMILIES = (
    "Inter", "Poppins", "Segoe UI Variable Text", "Segoe UI", "SF Pro Text",
    "Helvetica Neue", "Noto Sans", "DejaVu Sans", "Arial",
)
TITLE_FAMILIES = (
    "Poppins", "Montserrat", "Segoe UI Variable Display", "Segoe UI Semibold",
    "SF Pro Display", "Avenir Next", "Inter",
)
MONO_FAMILIES = (
    "JetBrains Mono", "Cascadia Code", "Cascadia Mono", "Fira Code", "Consolas",
    "SF Mono", "Menlo", "DejaVu Sans Mono", "Courier New",
)

BASE_W = 1120
BASE_H = 760
HEADER_H = 84
FOOTER_H = 48
OUTER = 28
GAP = 20
LEFT_W = 480
CARD_PAD = 18
MATRIX_H = 200
MIN_ZOOM = 0.7
MAX_ZOOM = 3.0
MAX_DIGITS = 3

SPEEDS: List[Tuple[str, float]] = [("Off", 0.0), ("Fast", 0.5), ("Normal", 1.0), ("Slow", 2.0)]
DEFAULT_SPEED = 2

BUTTON_COLORS: Dict[str, Dict[str, str]] = {
    "primary": {"fill": ACCENT, "text": WHITE, "hover": ACCENT_DARK, "press": ACCENT_PRESS},
    "secondary": {"fill": ACCENT_SOFT, "text": ACCENT, "hover": "#E0E4FF", "press": "#D0D6FF"},
    "ghost": {"fill": WHITE, "text": MUTED, "hover": "#F1F3F9", "hover_text": ACCENT, "press": "#E5E8F2"},
    "chip": {"fill": CHIP, "text": "#475467", "hover": "#E1E5F0", "press": "#D5DAE8"},
    "chip_on": {"fill": ACCENT, "text": WHITE, "hover": ACCENT_DARK, "press": ACCENT_PRESS},
}
