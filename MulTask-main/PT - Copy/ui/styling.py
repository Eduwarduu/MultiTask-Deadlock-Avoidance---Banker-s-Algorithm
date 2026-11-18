"""Fonts, ttk styles and small widget factories."""

from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from typing import Callable, Sequence

from .theme import (
    WHITE,
    INK,
    MUTED,
    LINE,
    LINE_STRONG,
    ACCENT,
    SELECT,
    TERM_BG,
    UI_FAMILIES,
    TITLE_FAMILIES,
    MONO_FAMILIES,
    BUTTON_COLORS,
)
from .widgets import RoundButton


class StyleMixin:
    """Fonts, ttk styles and small widget factories."""

    def _init_fonts(self) -> None:
        installed = set(tkfont.families(self.root))

        def pick(candidates: Sequence[str], fallback: str) -> str:
            return next((name for name in candidates if name in installed), fallback)

        base_ui = tkfont.nametofont("TkDefaultFont").actual("family")
        ui = pick(UI_FAMILIES, base_ui)
        title = pick(TITLE_FAMILIES, ui)
        mono = pick(MONO_FAMILIES, tkfont.nametofont("TkFixedFont").actual("family"))

        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont",
                     "TkCaptionFont", "TkTooltipFont", "TkIconFont"):
            try:
                tkfont.nametofont(name).configure(family=ui, size=10)
            except tk.TclError:
                pass
        tkfont.nametofont("TkFixedFont").configure(family=mono, size=9)

        self.f_ui = tkfont.Font(family=ui)
        self.f_ui_bold = tkfont.Font(family=ui, weight="bold")
        self.f_small = tkfont.Font(family=ui)
        self.f_small_bold = tkfont.Font(family=ui, weight="bold")
        self.f_eyebrow = tkfont.Font(family=ui, weight="bold")
        self.f_title = tkfont.Font(family=title, weight="bold")
        self.f_mono = tkfont.Font(family=mono)
        self.f_mono_bold = tkfont.Font(family=mono, weight="bold")
        self._size_fonts()

    def _size_fonts(self) -> None:
        """Set every font to its design size at the current zoom (pixel sizes)."""
        def size(points: float) -> int:
            return -max(8, int(round(points * 96.0 / 72.0 * self.k)))

        self.f_ui.configure(size=size(10))
        self.f_ui_bold.configure(size=size(10))
        self.f_small.configure(size=size(9))
        self.f_small_bold.configure(size=size(9))
        self.f_eyebrow.configure(size=size(8))
        self.f_title.configure(size=size(22))
        self.f_mono.configure(size=size(9))
        self.f_mono_bold.configure(size=size(9))

    def _init_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")

        themes = {
            "Minimal": (WHITE, "#CFD5E3", "#AEB6CB", "#8E98B3"),
            "Dark": (TERM_BG, "#3B4458", "#5B6679", "#7B8699"),
        }
        for prefix, (trough, thumb, active, pressed) in themes.items():
            for orient in ("Vertical", "Horizontal"):
                name = f"{prefix}.{orient}.TScrollbar"
                sticky = "ns" if orient == "Vertical" else "ew"
                style.layout(name, [
                    (f"{orient}.Scrollbar.trough", {
                        "sticky": sticky,
                        "children": [(f"{orient}.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})],
                    }),
                ])
                style.configure(
                    name, troughcolor=trough, background=thumb, bordercolor=trough,
                    lightcolor=thumb, darkcolor=thumb, relief="flat",
                    width=self.px(8), arrowsize=self.px(8),
                )
                style.map(name, background=[("active", active), ("pressed", pressed)])

    def _label(self, parent: tk.Misc, text: str, muted: bool = False, bold: bool = False) -> tk.Label:
        return tk.Label(
            parent, text=text, bg=WHITE, fg=MUTED if muted else INK,
            font=self.f_ui_bold if bold else self.f_ui, anchor="w",
        )

    def _eyebrow(self, parent: tk.Misc, text: str) -> tk.Label:
        return tk.Label(parent, text=text.upper(), font=self.f_eyebrow, bg=WHITE, fg=ACCENT, anchor="w")

    def _button(self, parent: tk.Misc, text: str, command: Callable[[], None],
                style: str = "secondary", bg: str = WHITE, small: bool = False) -> RoundButton:
        return RoundButton(
            parent, text, command, self.anim,
            self.f_small_bold if small else self.f_ui_bold,
            BUTTON_COLORS[style], bg,
            padx=self.px(12 if small else 18), pady=self.px(4 if small else 8),
        )

    def _cell(self, parent: tk.Misc) -> tk.Entry:
        """A digits-only number box with a fading focus ring."""
        entry = tk.Entry(
            parent, width=3, justify="center", font=self.f_ui_bold, bg=WHITE, fg=INK,
            insertbackground=ACCENT, relief="flat", highlightthickness=1,
            highlightbackground=LINE, highlightcolor=LINE,
            selectbackground=SELECT, selectforeground=INK,
            validate="key", validatecommand=self._vcmd,
        )
        entry.bind("<FocusIn>", self._cell_focus_in)
        entry.bind("<FocusOut>", self._cell_focus_out)
        entry.bind("<Enter>", lambda event: self._cell_hover(event.widget, True))
        entry.bind("<Leave>", lambda event: self._cell_hover(event.widget, False))
        return entry

    def _cell_focus_in(self, event: tk.Event) -> None:
        entry = event.widget
        entry.after_idle(entry.select_range, 0, "end")
        self.anim.cancel(("hover", id(entry)))
        self.anim.tween(
            ("ring", id(entry)), LINE, ACCENT, 200,
            lambda color: entry.configure(highlightcolor=color),
        )

    def _cell_focus_out(self, event: tk.Event) -> None:
        entry = event.widget
        self.anim.cancel(("ring", id(entry)))
        entry.configure(highlightcolor=LINE, highlightbackground=LINE)

    def _cell_hover(self, entry: tk.Entry, inside: bool) -> None:
        if entry is self.root.focus_get():
            return
        target = LINE_STRONG if inside else LINE
        self.anim.tween(
            ("hover", id(entry)), entry.cget("highlightbackground"), target, 140,
            lambda color: entry.configure(highlightbackground=color),
        )
