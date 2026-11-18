"""Button actions (load sample, safety check, request) and their animations."""

from __future__ import annotations

import tkinter as tk
from typing import Callable

import display
from banker import BankerError, request_resources
from sample_data import sample_state

from .theme import (
    WHITE,
    INK,
    GOOD,
    GOOD_SOFT,
    HEADER_H,
    GAP,
    SPEEDS,
)
from .helpers import mix_color, lerp


class ActionsMixin:
    """Button actions (load sample, safety check, request) and their animations."""

    def load_sample(self) -> None:
        """Load the classic safe state into the grid."""
        state = sample_state()
        self.process_count.set(state.process_count)
        self.resource_count.set(state.resource_count)
        self.build_table()

        self.total_input.set(state.total)
        self._populate(self.allocation_entries, state.allocation)
        self._populate(self.max_entries, state.maximum)

        if state.process_count > 1:
            self.chip_selector.select(state.process_names[1])
        self.request_input.set([1, 0, 2])

        self._reset_sequence()
        self.set_status("Sample scenario loaded: 5 processes, 3 resource types.")
        self.write("Sample scenario loaded.")
        self.write(display.render_state(state))

    def run_safety(self) -> None:
        """Run the Banker's Safety Algorithm on the values in the grid."""
        try:
            state = self._current_state()
            result = state.safety()
        except (BankerError, ValueError) as exc:
            self.show_error(exc)
            return

        self.write_rule()
        self.write("BANKER'S SAFETY ALGORITHM", "head")
        self.write(display.render_state(state))
        self.write(display.render_safety(result, state.process_names))

        if result.safe:
            sequence = display.format_sequence(result.sequence, state.process_names)
            self.set_status(f"SAFE STATE - safe sequence: {sequence}", ok=True)
        else:
            self.set_status("UNSAFE STATE - no safe sequence exists.", ok=False)
        self.play_sequence(result, state.process_names, "No safe sequence exists.")

    def submit_request(self) -> None:
        """Apply the Resource-Request Algorithm to the selected process."""
        try:
            state = self._current_state()
            selected = self.process_var.get().strip()
            if selected not in state.process_names:
                raise BankerError("Choose the requesting process.")
            process = state.process_names.index(selected)
            request = self.request_input.read("Request vector")
            result = request_resources(state, process, request)
        except (BankerError, ValueError) as exc:
            self.show_error(exc)
            return

        self.write_rule()
        self.write("RESOURCE REQUEST", "head")
        self.write(display.render_request(result, state))

        if result.safety is not None:
            self.play_sequence(result.safety, state.process_names, "The tentative state is unsafe.")
        else:
            self._reset_sequence("Not checked: the request exceeds Available.")

        if result.status == "GRANT":
            state.grant(process, request)

            for j in range(state.resource_count):
                new_value = state.allocation[process][j]
                self._animate_value(
                    self.allocation_entries[process][j], new_value - request[j], new_value
                )

            self.write("")
            self.write("Committed state after the granted request:")
            self.write(display.render_state(state))
            self.set_status(
                f"GRANT - {state.process_names[process]} received "
                f"{display.format_vector(request)}; Available is now "
                f"{display.format_vector(state.available)}.",
                ok=True,
            )
        else:
            self.set_status(
                "WAIT - the request was not granted; the state is unchanged.",
                ok=False,
            )

    def _fade_in(self) -> None:
        """Ease the window in on launch."""
        try:
            self.root.attributes("-alpha", 0.0)
        except tk.TclError:
            return
        self.root.update_idletasks()
        self.anim.tween(
            ("fade",), 0.0, 1.0, 360,
            lambda value: self.root.attributes("-alpha", value),
            mix=lerp,
            on_done=lambda: self.root.attributes("-alpha", 1.0),
        )

    def _intro(self) -> None:
        """Slide the two cards up into place, one after the other."""
        base = self.px(HEADER_H + GAP)

        for index, (frame, _kind) in enumerate(self._cards):
            def move(factor: float, frame: tk.Frame = frame) -> None:
                frame.place_configure(y=base + int(factor * self.px(26)))

            def start(index: int = index, move: Callable = move) -> None:
                self.anim.tween(("intro", index), 1.0, 0.0, 620, move, mix=lerp)

            self.anim.later(("intro-delay", index), 110 * index, start)

    def cycle_speed(self) -> None:
        """Step through Off / Fast / Normal / Slow."""
        self._speed_index = (self._speed_index + 1) % len(SPEEDS)
        label, scale = SPEEDS[self._speed_index]
        self.anim.scale = scale
        self.speed_button.set_text(f"Animation: {label}")
        self._layout_header_controls()

    def _flash_row(self, index: int, duration: float = 1000) -> None:
        """Tint one process row green, then fade it back."""
        if index >= len(self.row_labels):
            return
        label = self.row_labels[index]
        entries = [*self.allocation_entries[index], *self.max_entries[index]]

        def apply(t: float) -> None:
            tint = mix_color(GOOD_SOFT, WHITE, t)
            label.configure(bg=tint, fg=mix_color(GOOD, INK, t))
            for entry in entries:
                entry.configure(bg=tint)

        self.anim.tween(("row", index), 0.0, 1.0, duration, apply, mix=lerp)

    def _animate_value(self, entry: tk.Entry, old: int, new: int) -> None:
        """Count an entry from its old value to its new one, with a soft flash."""
        def apply(value: float) -> None:
            entry.delete(0, tk.END)
            entry.insert(0, str(round(value)))

        self.anim.tween(("value", id(entry)), float(old), float(new), 500, apply, mix=lerp)
        self.anim.tween(("flash", id(entry)), GOOD_SOFT, WHITE, 1000, lambda c: entry.configure(bg=c))
