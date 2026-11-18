"""Window composition: header, cards, left/right panels, footer and resizing."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Dict

from .theme import (
    WHITE,
    INK,
    MUTED,
    LINE,
    LINE_STRONG,
    STRIP_BG,
    BG_TOP,
    BG_BOTTOM,
    DECOR_A,
    DECOR_B,
    DECOR_RING,
    CARD_BORDER,
    CARD_SHADOW,
    HEAD_LEFT,
    HEAD_RIGHT,
    HEAD_SUB,
    TERM_BG,
    TERM_FG,
    TERM_GOOD,
    TERM_BAD,
    TERM_HEAD,
    TERM_RULE,
    TERM_SELECT,
    BASE_W,
    BASE_H,
    HEADER_H,
    FOOTER_H,
    OUTER,
    GAP,
    LEFT_W,
    CARD_PAD,
    MATRIX_H,
    SPEEDS,
)
from .helpers import mix_color, glass_colors, rounded_points
from .widgets import RoundButton, Stepper


class LayoutMixin:
    """Window composition: header, cards, left/right panels, footer and resizing."""

    def _compose(self, intro: bool = False) -> None:
        """Build the whole interface at the current zoom."""
        self._size_fonts()
        self._init_style()
        self._cards = []
        self.stage = tk.Canvas(self.root, highlightthickness=0, bd=0, bg=BG_TOP)
        self.stage.pack(fill="both", expand=True)
        self.stage.bind("<Configure>", self._paint_stage)

        self._build_header()
        self._build_left()
        self._build_right()
        self._build_footer()

        offset = self.px(26) if intro else 0
        for frame, kind in self._cards:
            frame.place(**self._card_place(kind, offset))
        self.footer.place(x=0, rely=1.0, y=-self.px(FOOTER_H), relwidth=1.0, height=self.px(FOOTER_H))
        self.header.place(x=0, y=0, relwidth=1.0, height=self.px(HEADER_H))

    def _card_place(self, kind: str, offset: int = 0) -> Dict[str, object]:
        top = self.px(HEADER_H + GAP)
        bottom = self.px(FOOTER_H + GAP)
        outer, left_w, gap = self.px(OUTER), self.px(LEFT_W), self.px(GAP)
        options: Dict[str, object] = {"y": top + offset, "relheight": 1.0, "height": -(top + bottom)}
        if kind == "left":
            options.update(x=outer, width=left_w)
        else:
            options.update(x=outer + left_w + gap, relwidth=1.0, width=-(2 * outer + left_w + gap))
        return options

    def _card(self, kind: str) -> tk.Frame:
        """A white card with a hairline border and an offset shadow; returns its content frame."""
        shadow = tk.Frame(self.stage, bg=CARD_SHADOW)
        border = tk.Frame(shadow, bg=CARD_BORDER)
        border.pack(fill="both", expand=True, padx=(0, self.px(3)), pady=(0, self.px(3)))
        inner = tk.Frame(border, bg=WHITE)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        content = tk.Frame(inner, bg=WHITE)
        content.pack(fill="both", expand=True, padx=self.px(CARD_PAD), pady=self.px(CARD_PAD))
        self._cards.append((shadow, kind))
        return content

    def _paint_stage(self, event: tk.Event) -> None:
        """Draw the window background: a soft gradient with a few large shapes."""
        canvas = self.stage
        width, height = event.width, event.height
        canvas.delete("bg")
        bands = 72
        for i in range(bands):
            y0 = height * i / bands
            y1 = height * (i + 1) / bands + 1
            canvas.create_rectangle(
                0, y0, width, y1, outline="",
                fill=mix_color(BG_TOP, BG_BOTTOM, i / (bands - 1)), tags="bg",
            )
        size = min(width, height)
        canvas.create_oval(
            width * 0.88 - size * 0.34, height * 0.22 - size * 0.34,
            width * 0.88 + size * 0.34, height * 0.22 + size * 0.34,
            fill=DECOR_A, outline="", tags="bg",
        )
        canvas.create_oval(
            width * 0.05 - size * 0.28, height * 0.95 - size * 0.28,
            width * 0.05 + size * 0.28, height * 0.95 + size * 0.28,
            fill=DECOR_B, outline="", tags="bg",
        )
        canvas.create_oval(
            width * 0.55 - size * 0.18, height * 1.02 - size * 0.18,
            width * 0.55 + size * 0.18, height * 1.02 + size * 0.18,
            fill="", outline=DECOR_RING, width=max(2, self.px(2)), tags="bg",
        )

    def _build_header(self) -> None:
        self.header = tk.Canvas(self.stage, highlightthickness=0, bd=0, bg=HEAD_LEFT)
        base = mix_color(HEAD_LEFT, HEAD_RIGHT, 0.94)
        glass = glass_colors(base)
        self.about_button = RoundButton(
            self.header, "About", self.show_about, self.anim, self.f_small_bold, glass, base,
            padx=self.px(16), pady=self.px(6),
        )
        self.speed_button = RoundButton(
            self.header, f"Animation: {SPEEDS[self._speed_index][0]}", self.cycle_speed,
            self.anim, self.f_small_bold, glass, base, padx=self.px(16), pady=self.px(6),
        )
        self.header.bind("<Configure>", self._draw_header)

    def _draw_header(self, event: tk.Event) -> None:
        canvas = self.header
        width, height = event.width, event.height
        canvas.delete("hg")
        canvas.delete("hc")
        bands = min(max(width, 2), 96)
        for i in range(bands):
            x0 = width * i / bands
            x1 = width * (i + 1) / bands + 1
            canvas.create_rectangle(
                x0, 0, x1, height, outline="",
                fill=mix_color(HEAD_LEFT, HEAD_RIGHT, i / (bands - 1)), tags="hg",
            )
        canvas.tag_lower("hg")

        outer = self.px(OUTER)
        block = self.px(10)
        gap = self.px(4)
        top = height / 2 - block - gap / 2
        tints = ((WHITE, "#A5B4FC"), ("#C7D2FE", "#818CF8"))
        for row in range(2):
            for column in range(2):
                x = outer + column * (block + gap)
                y = top + row * (block + gap)
                canvas.create_polygon(
                    rounded_points(x, y, x + block, y + block, self.px(3)),
                    smooth=True, fill=tints[row][column], outline="", tags="hc",
                )

        title_x = outer + 2 * block + gap + self.px(16)
        canvas.create_text(
            title_x, height / 2, text="MultiTask", font=self.f_title, fill=WHITE,
            anchor="w", tags="hc",
        )
        canvas.create_text(
            title_x + self.f_title.measure("MultiTask") + self.px(16), height / 2 + self.px(5),
            text="Banker's Algorithm simulator", font=self.f_ui, fill=HEAD_SUB,
            anchor="w", tags="hc",
        )
        self._layout_header_controls()

    def _layout_header_controls(self) -> None:
        width = self.header.winfo_width()
        height = self.header.winfo_height()
        if width <= 1:
            return
        self.header.delete("hw")
        x = width - self.px(OUTER)
        for button in (self.about_button, self.speed_button):
            self.header.create_window(x, height / 2, window=button, anchor="e", tags="hw")
            x -= button.pixel_width + self.px(10)

    def _build_left(self) -> None:
        content = self._card("left")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(3, weight=1)

        top = tk.Frame(content, bg=WHITE)
        top.grid(row=0, column=0, sticky="ew")
        self._eyebrow(top, "System state").pack(side="left")
        self._button(top, "Load sample", self.load_sample, "ghost", small=True).pack(side="right")

        dims = tk.Frame(content, bg=WHITE)
        dims.grid(row=1, column=0, sticky="w", pady=(self.px(8), 0))
        Stepper(self, dims, "Processes", self.process_count, 1, 10).pack(side="left")
        Stepper(self, dims, "Resources", self.resource_count, 1, 8).pack(side="left", padx=(self.px(20), 0))
        self._button(dims, "Build table", self.build_table, "secondary").pack(
            side="left", anchor="s", padx=(self.px(22), 0)
        )

        total_row = tk.Frame(content, bg=WHITE)
        total_row.grid(row=2, column=0, sticky="w", pady=(self.px(12), 0))
        total_row.columnconfigure(0, minsize=self.px(62))
        self._label(total_row, "Total", bold=True).grid(row=0, column=0, sticky="sw", pady=(0, self.px(6)))
        self.total_slot = tk.Frame(total_row, bg=WHITE)
        self.total_slot.grid(row=0, column=1, sticky="w")

        box = tk.Frame(content, bg=WHITE)
        box.grid(row=3, column=0, sticky="nsew", pady=(self.px(10), 0))
        box.columnconfigure(0, weight=1)
        box.rowconfigure(0, weight=1)
        box.columnconfigure(1, minsize=self.px(12))
        box.rowconfigure(1, minsize=self.px(12))
        self.matrix_box = box

        self.matrix_canvas = tk.Canvas(
            box, width=self.px(LEFT_W - 2 * CARD_PAD - 14), height=self.px(MATRIX_H), bg=WHITE,
            highlightthickness=0, yscrollincrement=self.px(32), xscrollincrement=self.px(20),
        )
        self.matrix_canvas.grid(row=0, column=0, sticky="nsew")
        vbar = ttk.Scrollbar(box, orient="vertical", style="Minimal.Vertical.TScrollbar",
                             command=self.matrix_canvas.yview)
        hbar = ttk.Scrollbar(box, orient="horizontal", style="Minimal.Horizontal.TScrollbar",
                             command=self.matrix_canvas.xview)
        self.matrix_canvas.configure(
            yscrollcommand=lambda lo, hi: self._scroll_set(vbar, {"row": 0, "column": 1, "sticky": "ns"}, lo, hi),
            xscrollcommand=lambda lo, hi: self._scroll_set(hbar, {"row": 1, "column": 0, "sticky": "ew"}, lo, hi),
        )
        self.matrix_holder = tk.Frame(self.matrix_canvas, bg=WHITE)
        self.matrix_canvas.create_window((0, 0), window=self.matrix_holder, anchor="nw")
        self.matrix_holder.bind(
            "<Configure>",
            lambda event: self.matrix_canvas.configure(scrollregion=self.matrix_canvas.bbox("all")),
        )

        tk.Frame(content, bg=LINE, height=1).grid(
            row=4, column=0, sticky="ew", pady=(self.px(10), self.px(12))
        )
        self._eyebrow(content, "Resource request").grid(row=5, column=0, sticky="w")

        chip_row = tk.Frame(content, bg=WHITE)
        chip_row.grid(row=6, column=0, sticky="w", pady=(self.px(8), 0))
        chip_row.columnconfigure(0, minsize=self.px(62))
        self._label(chip_row, "From", bold=True).grid(row=0, column=0, sticky="w")
        self.chip_slot = tk.Frame(chip_row, bg=WHITE)
        self.chip_slot.grid(row=0, column=1, sticky="w")

        request_row = tk.Frame(content, bg=WHITE)
        request_row.grid(row=7, column=0, sticky="w", pady=(self.px(10), 0))
        request_row.columnconfigure(0, minsize=self.px(62))
        self._label(request_row, "Vector", bold=True).grid(row=0, column=0, sticky="sw", pady=(0, self.px(6)))
        self.request_slot = tk.Frame(request_row, bg=WHITE)
        self.request_slot.grid(row=0, column=1, sticky="w")

        buttons = tk.Frame(content, bg=WHITE)
        buttons.grid(row=8, column=0, sticky="w", pady=(self.px(12), 0))
        self._button(buttons, "Run safety check", self.run_safety, "primary").pack(side="left")
        self._button(buttons, "Request resources", self.submit_request, "secondary").pack(
            side="left", padx=(self.px(10), 0)
        )

    def _build_right(self) -> None:
        content = self._card("right")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(2, weight=1)

        toolbar = tk.Frame(content, bg=WHITE)
        toolbar.grid(row=0, column=0, sticky="ew")
        self._eyebrow(toolbar, "Output").pack(side="left")
        self._button(toolbar, "Clear", self.clear_output, "ghost", small=True).pack(side="right")

        self.seq_holder = tk.Frame(
            content, bg=STRIP_BG, height=self.px(46),
            highlightthickness=1, highlightbackground=LINE_STRONG, highlightcolor=LINE_STRONG,
        )
        self.seq_holder.grid(row=1, column=0, sticky="ew", pady=(self.px(10), self.px(10)))
        self.seq_holder.pack_propagate(False)
        tk.Label(
            self.seq_holder, text="Safe sequence", font=self.f_small_bold, bg=STRIP_BG, fg=INK
        ).pack(side="left", padx=(self.px(14), self.px(12)))
        tk.Frame(self.seq_holder, bg=LINE_STRONG, width=1).pack(
            side="left", fill="y", pady=self.px(9)
        )
        self.seq_hint = tk.Label(
            self.seq_holder, text="", font=self.f_small, bg=STRIP_BG, fg=MUTED, anchor="w"
        )

        frame = tk.Frame(content, bg=TERM_BG)
        frame.grid(row=2, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.output = tk.Text(
            frame, wrap="none", font=self.f_mono, bg=TERM_BG, fg=TERM_FG,
            insertbackground=TERM_FG, relief="flat", highlightthickness=0,
            selectbackground=TERM_SELECT, selectforeground=WHITE,
            padx=self.px(16), pady=self.px(14), spacing1=1, spacing3=1,
        )
        self.output.grid(row=0, column=0, sticky="nsew")
        self.output.tag_configure("good", foreground=TERM_GOOD, font=self.f_mono_bold)
        self.output.tag_configure("bad", foreground=TERM_BAD, font=self.f_mono_bold)
        self.output.tag_configure("head", foreground=TERM_HEAD, font=self.f_mono_bold)
        self.output.tag_configure("rule", foreground=TERM_RULE)

        yscroll = ttk.Scrollbar(frame, orient="vertical", style="Dark.Vertical.TScrollbar",
                                command=self.output.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll = ttk.Scrollbar(frame, orient="horizontal", style="Dark.Horizontal.TScrollbar",
                                command=self.output.xview)
        xscroll.grid(row=1, column=0, sticky="ew")
        self.output.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.output.configure(state="disabled")

    def _build_footer(self) -> None:
        self.footer = tk.Frame(self.stage, bg=WHITE)
        tk.Frame(self.footer, bg=LINE, height=1).pack(side="top", fill="x")
        row = tk.Frame(self.footer, bg=WHITE)
        row.pack(fill="both", expand=True, padx=self.px(OUTER))

        size = self.px(22)
        center = size / 2
        radius = self.px(4)
        self.status_dot = tk.Canvas(row, width=size, height=size, bg=WHITE, highlightthickness=0, bd=0)
        self.status_dot.pack(side="left")
        self._dot = self.status_dot.create_oval(
            center - radius, center - radius, center + radius, center + radius,
            fill=self._dot_color, outline="",
        )
        self._ring = self.status_dot.create_oval(
            center - radius, center - radius, center + radius, center + radius,
            outline=WHITE, width=2, state="hidden",
        )
        self.status_label = tk.Label(
            row, textvariable=self.status_var, font=self.f_ui, bg=WHITE,
            fg=self._status_color, anchor="w", justify="left",
        )
        self.status_label.pack(side="left", fill="both", expand=True, padx=(self.px(6), 0))
        self.status_label.bind(
            "<Configure>", lambda event: self.status_label.configure(wraplength=max(event.width, 1))
        )

    def _on_configure(self, event: tk.Event) -> None:
        """Wait for the user to stop resizing, then re-fit the zoom."""
        if event.widget is not self.root:
            return
        if self._resize_job is not None:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(160, self._fit_zoom)

    def _fit_zoom(self) -> None:
        self._resize_job = None
        width, height = self.root.winfo_width(), self.root.winfo_height()
        if width < 2 or height < 2:
            return
        zoom = min(width / BASE_W, height / BASE_H)
        zoom = round(max(self.min_k, min(zoom, self.max_k)), 2)
        if abs(zoom - self.k) / self.k < 0.02:
            return
        self.k = zoom
        self._rebuild()

    def _rebuild(self) -> None:
        """Recreate the interface at the new zoom, keeping everything the user entered."""
        allocation = [[entry.get() for entry in row] for row in self.allocation_entries]
        maximum = [[entry.get() for entry in row] for row in self.max_entries]
        total = self.total_input.values() if self.total_input else None
        request = self.request_input.values() if self.request_input else None

        self.anim.clear()
        self._stream_queue = []
        if self.stage is not None:
            self.stage.destroy()
        self.allocation_entries = []
        self.max_entries = []
        self.row_labels = []
        self.chips = []
        self.total_input = None
        self.request_input = None
        self.chip_selector = None

        self._compose()

        if allocation:
            self._create_grid(len(allocation), len(allocation[0]), allocation, maximum, total, request)
        self._render_transcript()
        self._restore_sequence()
