"""
MultiTask - Tkinter graphical interface for the Banker's Algorithm simulator.

PT 101 Final Project - Topic 5: Deadlock Avoidance (Banker's Algorithm)

Run:
    python gui_v3.py

The window uses banker.py for every computation and display.py for the trace
text, so its results are identical to the console version in main.py.

Design notes
------------
* The interface fills the whole window and keeps its proportions: when the
  window is resized, text, spacing and controls are zoomed together, so it
  looks the same when maximised, restored or resized. Spare space goes to the
  grid and the output pane.
* After a resize the layout is rebuilt; grid values, vectors, output, status
  and the safe sequence are kept.
* Vectors are entered in one labelled box per resource. Boxes accept digits
  only and can be navigated with the arrow keys and Enter.
* Fonts: the best installed family from a preferred list is used. To use your
  own, put .ttf or .otf files in a folder named "fonts" next to gui_v3.py
  (loaded automatically on Windows) and add the family name to UI_FAMILIES,
  TITLE_FAMILIES or MONO_FAMILIES.
* Animation runs on Tk's after() timer, so the interface never freezes. The
  "Animation" switch in the header sets the speed (Off / Fast / Normal / Slow).

Package layout
--------------
theme.py     colours, font preferences, layout constants
helpers.py   colour blending, geometry and font loading helpers
animator.py  tween engine
widgets.py   RoundButton, Stepper, ChipSelector, VectorInput
styling.py   fonts, ttk styles, widget factories      (StyleMixin)
layout.py    header, cards, panels, footer, resizing  (LayoutMixin)
grid.py      allocation/max grid                      (GridMixin)
actions.py   button actions and their animations      (ActionsMixin)
output.py    safe-sequence strip, transcript, status  (OutputMixin)
app.py       BankerApp (combines the mixins) and main()
"""
