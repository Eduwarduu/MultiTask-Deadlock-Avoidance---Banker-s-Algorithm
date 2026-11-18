"""Small colour, geometry and font helpers."""

from __future__ import annotations

import os
import sys
from typing import Dict, List, Tuple

from .theme import (
    WHITE,
)


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _hex_to_rgb(color: str) -> Tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def mix_color(start: str, end: str, t: float) -> str:
    """Blend two #rrggbb colours; t=0 gives start, t=1 gives end."""
    a, b = _hex_to_rgb(start), _hex_to_rgb(end)
    r, g, bl = (round(x + (y - x) * t) for x, y in zip(a, b))
    return f"#{r:02x}{g:02x}{bl:02x}"


def lerp(start: float, end: float, t: float) -> float:
    """Blend two numbers."""
    return start + (end - start) * t


def glass_colors(base: str) -> Dict[str, str]:
    """Translucent-looking button colours for use on the header gradient."""
    return {
        "fill": mix_color(base, WHITE, 0.14),
        "text": WHITE,
        "hover": mix_color(base, WHITE, 0.28),
        "press": mix_color(base, WHITE, 0.08),
    }


def rounded_points(x1: float, y1: float, x2: float, y2: float, r: float) -> List[float]:
    """Polygon points that draw a rounded rectangle when the polygon is smoothed."""
    return [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]


def load_bundled_fonts() -> int:
    """Register .ttf/.otf files from a 'fonts' folder next to gui_v3.py (Windows)."""
    folder = os.path.join(PROJECT_ROOT, "fonts")
    if sys.platform != "win32" or not os.path.isdir(folder):
        return 0
    loaded = 0
    try:
        import ctypes

        for name in sorted(os.listdir(folder)):
            if name.lower().endswith((".ttf", ".otf")):
                path = os.path.join(folder, name)
                if ctypes.windll.gdi32.AddFontResourceExW(path, 0x10, 0):
                    loaded += 1
    except Exception:
        return loaded
    return loaded
