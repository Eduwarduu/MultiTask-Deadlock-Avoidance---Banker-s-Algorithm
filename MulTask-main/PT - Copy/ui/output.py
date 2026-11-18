"""Safe-sequence strip, output transcript, status line and dialogs."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Sequence, Tuple

from banker import SafetyResult

from .theme import (
    WHITE,
    INK,
    MUTED,
    LINE_STRONG,
    ACCENT,
    GOOD,
    GOOD_SOFT,
    BAD,
    STRIP_BG,
)
from .helpers import mix_color, lerp
from .widgets import RoundButton


class OutputMixin:
    """Safe-sequence strip, output transcript, status line and dialogs."""

    def _set_hint(self, text: str, color: str, fade: bool = True) -> None:
        """Show a one-line note in the sequence strip, fading it in."""
        self._seq_state = ("hint", text, color)
        self.seq_hint.configure(text=text, fg=STRIP_BG if fade else color)
        self.seq_hint.pack(side="left", padx=(self.px(12), 0))
        if fade:
            self.anim.tween(
                ("hint",), STRIP_BG, color, 380, lambda c: self.seq_hint.configure(fg=c)
            )

    def _clear_chips(self) -> None:
        self.anim.cancel(("seq",))
        for widget in self.chips:
            widget.destroy()
        self.chips = []
        self.seq_hint.pack_forget()

    def _reset_sequence(self, text: str = "Run a check to see the order.") -> None:
        self._clear_chips()
        self._set_hint(text, MUTED, fade=False)

    def _add_chip(self, name: str, settled: bool) -> Tuple[RoundButton, Optional[tk.Label]]:
        """Append one process pill (and the separator before it) to the sequence strip."""
        separator: Optional[tk.Label] = None
        if self.chips:
            separator = tk.Label(
                self.seq_holder, text="\u203a", font=self.f_ui_bold, bg=STRIP_BG,
                fg=LINE_STRONG if settled else STRIP_BG,
            )
            separator.pack(side="left", padx=(0, self.px(4)))
            self.chips.append(separator)
        colors = (
            {"fill": GOOD_SOFT, "text": GOOD, "hover": GOOD_SOFT, "press": GOOD_SOFT}
            if settled
            else {"fill": ACCENT, "text": WHITE, "hover": ACCENT, "press": ACCENT}
        )
        chip = RoundButton(
            self.seq_holder, name, None, self.anim, self.f_ui_bold, colors, STRIP_BG,
            padx=self.px(10), pady=self.px(3), cursor="",
        )
        first = not self.chips
        chip.pack(side="left", padx=(self.px(12) if first else 0, self.px(4)))
        self.chips.append(chip)
        return chip, separator

    def _restore_sequence(self) -> None:
        """Redraw the sequence strip, fully settled, after a rebuild."""
        state = self._seq_state
        if state[0] == "chips":
            for name in state[1]:
                self._add_chip(name, settled=True)
        else:
            self._set_hint(state[1], state[2], fade=False)

    def play_sequence(
        self, result: SafetyResult, names: Sequence[str], unsafe_text: str
    ) -> None:
        """Reveal the safe sequence one process at a time."""
        self._clear_chips()
        if not result.safe:
            self._set_hint(unsafe_text, BAD)
            return

        order = list(result.sequence)
        self._seq_state = ("chips", [names[index] for index in order])

        def reveal(step: int) -> None:
            if step >= len(order):
                return
            index = order[step]
            chip, separator = self._add_chip(names[index], settled=False)
            full = chip.pixel_width

            def pop(t: float) -> None:
                chip.set_width(lerp(full * 0.5, full, t))
                chip.paint(mix_color(ACCENT, GOOD_SOFT, t), mix_color(WHITE, GOOD, t))

            self.anim.tween(("chip", step), 0.0, 1.0, 560, pop, mix=lerp)
            if separator is not None:
                self.anim.tween(
                    ("sep", step), STRIP_BG, LINE_STRONG, 400,
                    lambda color: separator.configure(fg=color),
                )
            self._flash_row(index)
            self.anim.later(("seq",), 420, lambda: reveal(step + 1))

        reveal(0)

    @staticmethod
    def _tag_for(line: str) -> Optional[str]:
        text = line.strip()
        if "UNSAFE STATE" in text or text.startswith("Request result: WAIT"):
            return "bad"
        if "SAFE STATE" in text or text.startswith("Request result: GRANT"):
            return "good"
        return None

    def _insert_lines(self, entries: Sequence[Tuple[str, Optional[str]]]) -> None:
        self.output.configure(state="normal")
        for line, tags in entries:
            if tags:
                self.output.insert("end", line + "\n", tags)
            else:
                self.output.insert("end", line + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def _render_transcript(self) -> None:
        self._insert_lines(self.transcript)

    def _pump(self) -> None:
        """Stream queued output lines onto the screen in quick batches."""
        if not self._stream_queue:
            return
        batch = max(2, len(self._stream_queue) // 12)
        chunk = self._stream_queue[:batch]
        del self._stream_queue[:batch]
        self._insert_lines(chunk)
        if self._stream_queue:
            self.anim.later(("stream",), 14, self._pump)

    def write(self, text: str, tag: Optional[str] = None) -> None:
        """Append one block of text to the output pane."""
        entries = [(line, tag or self._tag_for(line)) for line in text.split("\n")]
        self.transcript.extend(entries)
        if self.anim.scale <= 0:
            self._insert_lines(self._stream_queue + entries)
            self._stream_queue = []
            return
        self._stream_queue.extend(entries)
        if not self.anim.active(("stream",)):
            self._pump()

    def write_rule(self) -> None:
        self.write("-" * 64, "rule")

    def clear_output(self) -> None:
        """Empty the output pane."""
        self.anim.cancel(("stream",))
        self._stream_queue = []
        self.transcript = []
        self.output.configure(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.configure(state="disabled")

    def _ping(self, color: str) -> None:
        """Send a ring outwards from the status dot."""
        size = self.px(22)
        center = size / 2
        start, end = self.px(4), self.px(10)
        self.status_dot.itemconfigure(self._ring, state="normal")

        def apply(t: float) -> None:
            radius = lerp(start, end, t)
            self.status_dot.coords(
                self._ring, center - radius, center - radius, center + radius, center + radius
            )
            self.status_dot.itemconfigure(self._ring, outline=mix_color(color, WHITE, t))

        self.anim.tween(
            ("ping",), 0.0, 1.0, 700, apply, mix=lerp,
            on_done=lambda: self.status_dot.itemconfigure(self._ring, state="hidden"),
        )

    def set_status(self, text: str, ok: bool | None = None) -> None:
        """Update the status bar; green for success, red for problems."""
        self.status_var.set(text)
        text_to = GOOD if ok is True else BAD if ok is False else INK
        dot_to = GOOD if ok is True else BAD if ok is False else ACCENT
        text_from, dot_from = self._status_color, self._dot_color

        def apply(t: float) -> None:
            self._status_color = mix_color(text_from, text_to, t)
            self._dot_color = mix_color(dot_from, dot_to, t)
            self.status_label.configure(fg=self._status_color)
            self.status_dot.itemconfigure(self._dot, fill=self._dot_color)

        self.anim.tween(("status",), 0.0, 1.0, 320, apply, mix=lerp)
        if ok is not None:
            self._ping(dot_to)

    def show_error(self, error: Exception | str) -> None:
        """Show a validation error in the status bar and a dialog."""
        message = str(error)
        self.set_status("Error: " + message, ok=False)
        messagebox.showerror("Invalid input", message, parent=self.root)

    def show_about(self) -> None:
        """Show a short description of the project."""
        messagebox.showinfo(
            "About MultiTask",
            "MultiTask - Banker's Algorithm Simulator\n\n"
            "PT 101 Final Project - Topic 5: Deadlock Avoidance\n\n"
            "Need = Max - Allocation\n"
            "Available = Total - column sums of Allocation\n\n"
            "Before a request is granted, the tentative allocation is checked "
            "with the Banker's Safety Algorithm.",
            parent=self.root,
        )
