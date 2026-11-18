"""Tween engine built on Tk's after() timer."""

from __future__ import annotations

import time
import tkinter as tk
from typing import Callable, Dict, Optional

from .theme import (
    SPEEDS,
    DEFAULT_SPEED,
)
from .helpers import mix_color


class Animator:
    """Small tween engine built on Tk's after() timer."""

    FRAME_MS = 16

    def __init__(self, root: tk.Misc) -> None:
        self.root = root
        self.scale = SPEEDS[DEFAULT_SPEED][1]
        self._jobs: Dict[object, str] = {}

    def active(self, key: object) -> bool:
        return key in self._jobs

    def cancel(self, key: object) -> None:
        job = self._jobs.pop(key, None)
        if job is not None:
            try:
                self.root.after_cancel(job)
            except tk.TclError:
                pass

    def clear(self) -> None:
        """Stop every running animation."""
        for key in list(self._jobs):
            self.cancel(key)

    def tween(
        self,
        key: object,
        start,
        end,
        duration_ms: float,
        apply: Callable[[object], None],
        mix: Callable = mix_color,
        on_done: Optional[Callable[[], None]] = None,
    ) -> None:
        """Call apply(value) repeatedly while easing from start to end."""
        self.cancel(key)
        duration = duration_ms * self.scale
        if duration <= 0:
            try:
                apply(end)
            except tk.TclError:
                return
            if on_done:
                on_done()
            return

        began = time.monotonic()

        def step() -> None:
            t = min((time.monotonic() - began) * 1000.0 / duration, 1.0)
            value = end if t >= 1.0 else mix(start, end, 1.0 - (1.0 - t) ** 3)
            try:
                apply(value)
            except tk.TclError:
                self._jobs.pop(key, None)
                return
            if t >= 1.0:
                self._jobs.pop(key, None)
                if on_done:
                    on_done()
            else:
                self._jobs[key] = self.root.after(self.FRAME_MS, step)

        step()

    def later(self, key: object, delay_ms: float, action: Callable[[], None]) -> None:
        """Run action after a delay that follows the speed setting."""
        self.cancel(key)
        delay = delay_ms * self.scale
        if delay <= 0:
            action()
            return

        def fire() -> None:
            self._jobs.pop(key, None)
            action()

        self._jobs[key] = self.root.after(int(delay), fire)
