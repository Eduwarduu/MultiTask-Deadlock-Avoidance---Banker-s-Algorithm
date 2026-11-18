# MultiTask – Banker's Algorithm Simulator

**PT 101 Final Project · Topic 5: Deadlock Avoidance**

A desktop app (Python + Tkinter) that simulates the **Banker's Algorithm**, the classic deadlock-avoidance method used by operating systems. You enter a system's resource state, and the app tells you whether it is in a safe state and whether a new resource request can be granted without risking deadlock.

## How it works

For each process the program keeps track of:

- **Allocation** – resources the process currently holds
- **Max** – the most the process may ever need
- **Need** = Max − Allocation
- **Available** = Total − sum of all Allocations

**Safety check:** the algorithm looks for an order in which every process can finish using the available resources. If one exists, the state is **safe** and the order is the *safe sequence*. If not, the state is **unsafe**.

**Resource request:** a process asks for extra resources. The request is only granted if it is within the process's Need and the available resources, and the resulting tentative state still passes the safety check. Otherwise the process must wait.

## Features

- Editable allocation and max tables for 1–10 processes and 1–8 resource types
- Total-resources vector with one labelled box per resource
- One-click **Load sample** data
- **Run safety check** with the safe sequence revealed step by step
- **Request resources** with a GRANT / WAIT result and a full step-by-step trace
- Colour-coded output log (safe / unsafe, granted / wait)
- Resizable window that scales to any screen, with keyboard navigation in the grids
- Adjustable animation speed (Off / Fast / Normal / Slow)
- Optional custom fonts (drop `.ttf` / `.otf` files in a `fonts` folder, Windows)

## Requirements

- Python 3.9 or newer (tested on 3.14)
- Tkinter (included with the standard Python installer on Windows and macOS)
- No third-party packages

## Run

```bash
python gui_v3.py
```

Run it from the project folder so the `ui` package and the other modules can be found.

## Project structure

```
├── gui_v3.py        # launcher
├── banker.py        # Banker's Algorithm logic
├── display.py       # trace/output text formatting
├── sample_data.py   # sample system state
└── ui/              # GUI package
    ├── app.py       # main window (BankerApp) and main()
    ├── layout.py    # header, panels, footer, resizing
    ├── grid.py      # allocation / max grid
    ├── actions.py   # button actions and animations
    ├── output.py    # safe-sequence strip, output log, status
    ├── styling.py   # fonts, styles, widget factories
    ├── widgets.py   # rounded button, stepper, chip selector, vector input
    ├── animator.py  # tween engine
    ├── helpers.py   # colour and geometry helpers
    └── theme.py     # colours and constants
```

## Authors

PT 101 – MultiTask group project.
