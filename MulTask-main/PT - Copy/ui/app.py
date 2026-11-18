"""The main application window, assembled from focused mixins."""

from __future__ import annotations

import tkinter as tk
from typing import List, Optional, Tuple

from .theme import (
    APP_TITLE,
    INK,
    MUTED,
    ACCENT,
    BG_TOP,
    BASE_W,
    BASE_H,
    MIN_ZOOM,
    MAX_ZOOM,
    MAX_DIGITS,
    DEFAULT_SPEED,
)
from .helpers import load_bundled_fonts
from .animator import Animator
from .widgets import ChipSelector, VectorInput

from .styling import StyleMixin
from .layout import LayoutMixin
from .grid import GridMixin
from .actions import ActionsMixin
from .output import OutputMixin


class BankerApp(StyleMixin, LayoutMixin, GridMixin, ActionsMixin, OutputMixin):
    """Main window: editable state grid, actions, and trace output."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title(APP_TITLE)
        root.configure(bg=BG_TOP)

        self.dpi_scale = self._display_scale()
        self.min_k = self.dpi_scale * MIN_ZOOM
        self.max_k = self.dpi_scale * MAX_ZOOM
        fit = min(
            (root.winfo_screenwidth() - 40) / BASE_W,
            (root.winfo_screenheight() - 120) / BASE_H,
        )
        self.k = round(max(self.min_k, min(self.dpi_scale, fit)), 2)

        self.anim = Animator(root)
        self._speed_index = DEFAULT_SPEED
        self._resize_job: Optional[str] = None
        self._vcmd = (root.register(self._digits_only), "%P")

        self._init_fonts()

        width, height = int(round(BASE_W * self.k)), int(round(BASE_H * self.k))
        root.minsize(int(round(BASE_W * self.min_k)), int(round(BASE_H * self.min_k)))
        x = max((root.winfo_screenwidth() - width) // 2, 0)
        y = max((root.winfo_screenheight() - height) // 2 - 20, 0)
        root.geometry(f"{width}x{height}+{x}+{y}")

        self.process_count = tk.IntVar(value=5)
        self.resource_count = tk.IntVar(value=3)
        self.process_var = tk.StringVar(value="P0")
        self.status_var = tk.StringVar(value="Ready.")
        self._status_color = INK
        self._dot_color = ACCENT

        self.allocation_entries: List[List[tk.Entry]] = []
        self.max_entries: List[List[tk.Entry]] = []
        self.row_labels: List[tk.Label] = []
        self.chips: List[tk.Widget] = []
        self.transcript: List[Tuple[str, Optional[str]]] = []
        self._stream_queue: List[Tuple[str, Optional[str]]] = []
        self._seq_state: Tuple = ("hint", "Run a check to see the order.", MUTED)
        self.total_input: Optional[VectorInput] = None
        self.request_input: Optional[VectorInput] = None
        self.chip_selector: Optional[ChipSelector] = None
        self._cards: List[Tuple[tk.Frame, str]] = []
        self.stage: Optional[tk.Canvas] = None

        self._compose(intro=True)
        self.load_sample()
        self.set_status("Ready.")

        self.root.bind_all("<MouseWheel>", self._on_wheel, add="+")
        self.root.bind_all("<Button-4>", self._on_wheel, add="+")
        self.root.bind_all("<Button-5>", self._on_wheel, add="+")
        self._fade_in()
        self._intro()
        self.root.bind("<Configure>", self._on_configure)

    def _display_scale(self) -> float:
        """Ratio of this display's DPI to 96, never below 1."""
        try:
            return max(1.0, float(self.root.winfo_fpixels("1i")) / 96.0)
        except tk.TclError:
            return 1.0

    def px(self, value: float) -> int:
        """Convert a design pixel size to a real pixel size at the current zoom."""
        return max(1, int(round(value * self.k)))

    @staticmethod
    def _digits_only(proposed: str) -> bool:
        return proposed == "" or (
            proposed.isascii() and proposed.isdigit() and len(proposed) <= MAX_DIGITS
        )


def main() -> None:
    """Start the Tkinter application."""
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    load_bundled_fonts()
    root = tk.Tk()
    BankerApp(root)
    root.mainloop()
