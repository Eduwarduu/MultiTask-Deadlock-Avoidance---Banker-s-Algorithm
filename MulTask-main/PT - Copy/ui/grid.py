"""The allocation/max grid: creation, keyboard navigation, scrolling and reading."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Sequence

from banker import BankerError, SystemState, default_resource_names

from .theme import (
    WHITE,
    INK,
    MUTED,
)
from .widgets import ChipSelector, VectorInput


class GridMixin:
    """The allocation/max grid: creation, keyboard navigation, scrolling and reading."""

    def _scroll_set(self, bar: ttk.Scrollbar, grid_options: dict, low: str, high: str) -> None:
        """Show a scrollbar only when there is something to scroll."""
        bar.set(low, high)
        if float(low) <= 0.0 and float(high) >= 1.0:
            bar.grid_remove()
        else:
            bar.grid(**grid_options)

    def _on_wheel(self, event: tk.Event) -> None:
        """Scroll the grid when the pointer is over it."""
        try:
            widget = self.root.winfo_containing(event.x_root, event.y_root)
        except (KeyError, tk.TclError):
            return
        while widget is not None and widget is not self.matrix_box:
            widget = widget.master
        if widget is None:
            return

        if getattr(event, "num", None) == 4:
            direction = -1
        elif getattr(event, "num", None) == 5:
            direction = 1
        else:
            direction = -1 if event.delta > 0 else 1

        if event.state & 0x0001:
            self.matrix_canvas.xview_scroll(direction, "units")
        else:
            self.matrix_canvas.yview_scroll(direction, "units")

    def _focus_at(self, row: int, index: int) -> None:
        if not self.allocation_entries:
            return
        row = min(max(row, 0), len(self.allocation_entries) - 1)
        cells = self.allocation_entries[row] + self.max_entries[row]
        cells[min(max(index, 0), len(cells) - 1)].focus_set()

    def _arrow(self, event: tk.Event, row: int, index: int, direction: int) -> Optional[str]:
        entry = event.widget
        at_edge = entry.index("insert") == (len(entry.get()) if direction > 0 else 0)
        if at_edge or entry.selection_present():
            self._focus_at(row, index + direction)
            return "break"
        return None

    def _bind_navigation(self, entry: tk.Entry, row: int, index: int) -> None:
        entry.bind("<Up>", lambda event: (self._focus_at(row - 1, index), "break")[1])
        entry.bind("<Down>", lambda event: (self._focus_at(row + 1, index), "break")[1])
        entry.bind("<Return>", lambda event: (self._focus_at(row + 1, index), "break")[1])
        entry.bind("<Left>", lambda event: self._arrow(event, row, index, -1))
        entry.bind("<Right>", lambda event: self._arrow(event, row, index, 1))

    def _create_grid(
        self,
        n: int,
        m: int,
        allocation: Optional[Sequence[Sequence[str]]] = None,
        maximum: Optional[Sequence[Sequence[str]]] = None,
        total: Optional[Sequence[str]] = None,
        request: Optional[Sequence[str]] = None,
    ) -> None:
        """Create the entry grid, the vector boxes and the process chips for n x m."""
        holder = self.matrix_holder
        for child in holder.winfo_children():
            child.destroy()
        for column in range(20):
            holder.columnconfigure(column, minsize=0)

        self.allocation_entries = []
        self.max_entries = []
        self.row_labels = []
        resource_names = default_resource_names(m)
        max_start = m + 2
        holder.columnconfigure(m + 1, minsize=self.px(18))

        def heading(text: str, column: int) -> None:
            tk.Label(
                holder, text=text.upper(), font=self.f_eyebrow, bg=WHITE, fg=MUTED, anchor="w"
            ).grid(row=0, column=column, columnspan=m, sticky="w", padx=self.px(3))

        heading("Allocation", 1)
        heading("Max", max_start)
        for j, resource in enumerate(resource_names):
            for start in (1, max_start):
                tk.Label(holder, text=resource, width=3, font=self.f_small_bold, bg=WHITE, fg=MUTED).grid(
                    row=1, column=start + j, padx=self.px(2)
                )

        for i in range(n):
            label = tk.Label(holder, text=f"P{i}", width=4, anchor="w", font=self.f_ui_bold, bg=WHITE, fg=INK)
            label.grid(row=2 + i, column=0, sticky="w")
            self.row_labels.append(label)

            allocation_row: List[tk.Entry] = []
            maximum_row: List[tk.Entry] = []
            for start, target, source in (
                (1, allocation_row, allocation),
                (max_start, maximum_row, maximum),
            ):
                for j in range(m):
                    entry = self._cell(holder)
                    entry.grid(row=2 + i, column=start + j, padx=self.px(2), pady=self.px(2), ipady=self.px(4))
                    entry.insert(0, source[i][j] if source else "0")
                    index = j if start == 1 else m + j
                    self._bind_navigation(entry, i, index)
                    target.append(entry)

            self.allocation_entries.append(allocation_row)
            self.max_entries.append(maximum_row)

        self.matrix_canvas.xview_moveto(0)
        self.matrix_canvas.yview_moveto(0)

        for slot in (self.total_slot, self.request_slot, self.chip_slot):
            for child in slot.winfo_children():
                child.destroy()
        self.total_input = VectorInput(self, self.total_slot, m)
        self.total_input.pack()
        self.request_input = VectorInput(self, self.request_slot, m, self.submit_request)
        self.request_input.pack()
        if total:
            self.total_input.set(total)
        if request:
            self.request_input.set(request)

        names = [f"P{i}" for i in range(n)]
        if self.process_var.get() not in names:
            self.process_var.set(names[0])
        self.chip_selector = ChipSelector(self, self.chip_slot, names, self.process_var)
        self.chip_selector.pack()

    def build_table(self) -> None:
        """Create a fresh grid of zeros for the selected dimensions."""
        try:
            n = int(self.process_count.get())
            m = int(self.resource_count.get())
        except (tk.TclError, ValueError):
            self.show_error("Process and resource counts must be whole numbers.")
            return

        if not 1 <= n <= 10 or not 1 <= m <= 8:
            self.show_error("Use 1 to 10 processes and 1 to 8 resource types.")
            return

        self.process_var.set("P0")
        self._create_grid(n, m)
        self.set_status(
            f"Table built: {n} process(es), {m} resource type(s). "
            "Enter values or load the sample."
        )

    def _read_matrix(
        self, entries: Sequence[Sequence[tk.Entry]], label: str
    ) -> List[List[int]]:
        matrix = []
        for i, row in enumerate(entries):
            values = []
            for j, entry in enumerate(row):
                text = entry.get().strip()
                if not text:
                    raise BankerError(f"{label} for P{i}, resource {j + 1} is empty.")
                values.append(int(text))
            matrix.append(values)
        return matrix

    def _current_state(self) -> SystemState:
        """Read the grid and build a validated SystemState."""
        if not self.allocation_entries or self.total_input is None:
            raise BankerError("Build the table first, or load the sample scenario.")

        n = len(self.allocation_entries)
        m = len(self.allocation_entries[0])
        total = self.total_input.read("Total vector")
        allocation = self._read_matrix(self.allocation_entries, "Allocation")
        maximum = self._read_matrix(self.max_entries, "Max")

        return SystemState.from_vectors(
            total=total,
            allocation=allocation,
            maximum=maximum,
            process_names=[f"P{i}" for i in range(n)],
            resource_names=default_resource_names(m),
        )

    @staticmethod
    def _populate(entries: Sequence[Sequence[tk.Entry]], values: Sequence[Sequence[int]]) -> None:
        for row_entries, row_values in zip(entries, values):
            for entry, value in zip(row_entries, row_values):
                entry.delete(0, tk.END)
                entry.insert(0, str(value))
