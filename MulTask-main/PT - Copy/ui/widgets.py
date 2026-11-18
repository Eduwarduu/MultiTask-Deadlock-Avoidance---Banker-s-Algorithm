"""Reusable widgets: rounded button, stepper, chip selector and vector input."""

from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from typing import Callable, Dict, List, Optional, Sequence, TYPE_CHECKING, Tuple

from banker import BankerError, default_resource_names

from .theme import (
    WHITE,
    INK,
    MUTED,
    ACCENT,
    SELECT,
    BUTTON_COLORS,
)
from .helpers import mix_color, lerp, rounded_points
from .animator import Animator

if TYPE_CHECKING:
    from .app import BankerApp


class RoundButton(tk.Canvas):
    """A rounded, flat button (or pill) drawn on a canvas, with smooth colour fades."""

    def __init__(
        self,
        parent: tk.Misc,
        text: str,
        command: Optional[Callable[[], None]],
        animator: Animator,
        font: tkfont.Font,
        colors: Dict[str, str],
        bg: str,
        padx: int = 16,
        pady: int = 7,
        min_width: int = 0,
        cursor: str = "hand2",
    ) -> None:
        self._font = font
        self._padx = padx
        self._min_width = min_width
        self._text = text
        width = max(font.measure(text) + 2 * padx, min_width)
        height = font.metrics("linespace") + 2 * pady
        super().__init__(
            parent, width=width, height=height, bg=bg, bd=0,
            highlightthickness=0, cursor=cursor, takefocus=1 if command else 0,
        )
        self._bw = width
        self._bh = height
        self._command = command
        self._anim = animator
        self._colors = dict(colors)
        self._fill = colors["fill"]
        self._ink = colors["text"]
        self._shape = self.create_polygon(
            rounded_points(1, 1, width - 1, height - 1, min(height, width) / 2 - 1),
            smooth=True, fill=self._fill, outline="", width=2,
        )
        self._caption = self.create_text(
            width / 2, height / 2, text=text, font=font, fill=self._ink
        )
        if command is not None:
            self.bind("<Enter>", lambda event: self._go(
                self._colors["hover"], self._colors.get("hover_text", self._colors["text"])))
            self.bind("<Leave>", lambda event: self._go(self._colors["fill"], self._colors["text"]))
            self.bind("<ButtonPress-1>", self._pressed)
            self.bind("<ButtonRelease-1>", self._released)
            self.bind("<FocusIn>", lambda event: self.itemconfigure(self._shape, outline=SELECT))
            self.bind("<FocusOut>", lambda event: self.itemconfigure(self._shape, outline=""))
            self.bind("<Return>", lambda event: self._command())
            self.bind("<space>", lambda event: self._command())

    @property
    def pixel_width(self) -> int:
        return self._bw

    def _redraw(self) -> None:
        self.configure(width=self._bw, height=self._bh)
        self.coords(
            self._shape,
            *rounded_points(1, 1, self._bw - 1, self._bh - 1, min(self._bh, self._bw) / 2 - 1),
        )
        self.coords(self._caption, self._bw / 2, self._bh / 2)

    def set_text(self, text: str) -> None:
        self._text = text
        self._bw = max(self._font.measure(text) + 2 * self._padx, self._min_width)
        self.itemconfigure(self._caption, text=text)
        self._redraw()

    def set_width(self, width: float) -> None:
        self._bw = max(int(width), 2)
        self._redraw()

    def paint(self, fill: str, ink: Optional[str] = None) -> None:
        self._fill = fill
        if ink is not None:
            self._ink = ink
        self.itemconfigure(self._shape, fill=self._fill)
        self.itemconfigure(self._caption, fill=self._ink)

    def _go(self, fill: str, ink: str, duration: float = 140) -> None:
        start_fill, start_ink = self._fill, self._ink
        self._anim.tween(
            ("button", id(self)), 0.0, 1.0, duration,
            lambda t: self.paint(mix_color(start_fill, fill, t), mix_color(start_ink, ink, t)),
            mix=lerp,
        )

    def restyle(self, colors: Dict[str, str]) -> None:
        """Fade to a new colour set (used by selectable chips)."""
        self._colors = dict(colors)
        self._go(colors["fill"], colors["text"], 200)

    def _pressed(self, event: tk.Event) -> None:
        self._anim.cancel(("button", id(self)))
        self.paint(self._colors["press"])

    def _released(self, event: tk.Event) -> None:
        inside = 0 <= event.x <= self._bw and 0 <= event.y <= self._bh
        if inside:
            self._go(self._colors["hover"], self._colors.get("hover_text", self._colors["text"]))
            self._command()
        else:
            self._go(self._colors["fill"], self._colors["text"])


class Stepper(tk.Frame):
    """A labelled - value + control for choosing a whole number in a range."""

    def __init__(self, app: "BankerApp", parent: tk.Misc, title: str,
                 variable: tk.IntVar, low: int, high: int) -> None:
        super().__init__(parent, bg=WHITE)
        self._app = app
        self._variable = variable
        self._low = low
        self._high = high

        tk.Label(self, text=title, font=app.f_small, bg=WHITE, fg=MUTED, anchor="w").grid(
            row=0, column=0, columnspan=3, sticky="w"
        )
        pad = app.px(4)
        size = app.f_ui_bold.metrics("linespace") + 2 * pad
        minus = RoundButton(self, "\u2212", lambda: self._step(-1), app.anim, app.f_ui_bold,
                            BUTTON_COLORS["chip"], WHITE, padx=0, pady=pad, min_width=size)
        plus = RoundButton(self, "+", lambda: self._step(1), app.anim, app.f_ui_bold,
                           BUTTON_COLORS["chip"], WHITE, padx=0, pady=pad, min_width=size)
        self._value = tk.Label(self, textvariable=variable, width=3, font=app.f_ui_bold,
                               bg=WHITE, fg=INK)
        minus.grid(row=1, column=0, pady=(app.px(4), 0))
        self._value.grid(row=1, column=1, pady=(app.px(4), 0))
        plus.grid(row=1, column=2, pady=(app.px(4), 0))

    def _step(self, direction: int) -> None:
        try:
            current = int(self._variable.get())
        except tk.TclError:
            current = self._low
        new = min(self._high, max(self._low, current + direction))
        if new != current:
            self._variable.set(new)
            self._app.anim.tween(
                ("pop", id(self)), ACCENT, INK, 360,
                lambda color: self._value.configure(fg=color),
            )


class ChipSelector(tk.Frame):
    """A row of pills of which exactly one is selected."""

    def __init__(self, app: "BankerApp", parent: tk.Misc, names: Sequence[str],
                 variable: tk.StringVar) -> None:
        super().__init__(parent, bg=WHITE)
        self._variable = variable
        self._buttons: List[Tuple[str, RoundButton]] = []
        pad = app.px(8)
        width = app.f_ui_bold.measure("P00") + 2 * pad
        for name in names:
            on = name == variable.get()
            button = RoundButton(
                self, name, lambda value=name: self.select(value), app.anim, app.f_ui_bold,
                BUTTON_COLORS["chip_on" if on else "chip"], WHITE,
                padx=pad, pady=app.px(4), min_width=width,
            )
            button.pack(side="left", padx=(0, app.px(4)))
            self._buttons.append((name, button))

    def select(self, name: str) -> None:
        self._variable.set(name)
        for value, button in self._buttons:
            button.restyle(BUTTON_COLORS["chip_on" if value == name else "chip"])


class VectorInput(tk.Frame):
    """One labelled box per resource type, for entering a vector formally."""

    def __init__(self, app: "BankerApp", parent: tk.Misc, count: int,
                 on_submit: Optional[Callable[[], None]] = None) -> None:
        super().__init__(parent, bg=WHITE)
        self._app = app
        self._on_submit = on_submit
        self.names = default_resource_names(count)
        self.entries: List[tk.Entry] = []

        for j, name in enumerate(self.names):
            tk.Label(self, text=name, font=app.f_small_bold, bg=WHITE, fg=MUTED).grid(
                row=0, column=j
            )
            entry = app._cell(self)
            entry.grid(row=1, column=j, padx=app.px(3), ipady=app.px(4))
            entry.insert(0, "0")
            entry.bind("<Left>", lambda event, index=j: self._arrow(event, index, -1))
            entry.bind("<Right>", lambda event, index=j: self._arrow(event, index, 1))
            entry.bind("<Return>", lambda event, index=j: self._enter(index))
            self.entries.append(entry)

    def _arrow(self, event: tk.Event, index: int, direction: int) -> Optional[str]:
        entry = event.widget
        at_edge = entry.index("insert") == (len(entry.get()) if direction > 0 else 0)
        target = index + direction
        if (at_edge or entry.selection_present()) and 0 <= target < len(self.entries):
            self.entries[target].focus_set()
            return "break"
        return None

    def _enter(self, index: int) -> str:
        if index + 1 < len(self.entries):
            self.entries[index + 1].focus_set()
        elif self._on_submit is not None:
            self._on_submit()
        return "break"

    def values(self) -> List[str]:
        return [entry.get() for entry in self.entries]

    def set(self, values: Sequence[object]) -> None:
        for entry, value in zip(self.entries, values):
            entry.delete(0, tk.END)
            entry.insert(0, str(value))

    def read(self, label: str) -> List[int]:
        """Return the vector as integers, naming the resource of any empty box."""
        result = []
        for name, entry in zip(self.names, self.entries):
            text = entry.get().strip()
            if not text:
                raise BankerError(f"{label}: enter a value for resource {name}.")
            result.append(int(text))
        return result
