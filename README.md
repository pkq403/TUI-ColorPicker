# 🎨 TUI Color Picker (`tui-color-picker`)

A terminal-based color picker built with Python, driven by the **`uv`** package manager. Features an interactive 2D color palette square rendered with TrueColor half-blocks, Hue and Alpha sliders, live bidirectional synchronization with a smart multi-format input (Hex, RGBA, OKLCH), WCAG contrast checks, and a Typer CLI interface.

---

## ✨ Features

- **2D Color Palette Square**:
  - Rendered with 24-bit TrueColor ANSI escape codes and half-block characters (`▀`) to double the vertical resolution and produce a smooth, square gradient.
  - Interactive reticle (`⊙`) with automatic high-contrast visibility against bright and dark colors.
  - Full mouse click-and-drag support alongside keyboard arrow key navigation (with `Shift` for fast steps).
- **Hue & Alpha Sliders**:
  - Vertical Hue bar ($0^\circ - 360^\circ$) with live indicator (`◀`).
  - Horizontal Alpha / Opacity slider ($0\% - 100\%$) with checkerboard background blending.
- **Multi-Format Smart Input Field**:
  - Positioned to the right of the color palette square.
  - Auto-detects and parses input in real time:
    - **Hex**: `#ffffff`, `#ff550080`, bare hex `ff5500`, `0xff5500`.
    - **RGBA**: `rgb(255, 0, 128)`, `rgba(255, 0, 128, 0.5)`, CSS Color 4 `rgb(255 0 128 / 0.5)`.
    - **OKLCH**: `oklch(0.7 0.15 180)`, comma syntax `oklch(0.7, 0.15, 180, 0.5)`, and common typos like `okclh(...)`.
    - **HSL** & **CSS Named Colors**: `hsl(200, 100%, 50%)`, `coral`, `rebeccapurple`.
  - Bidirectional reactive sync: typing updates the canvas reticle and sliders; moving the canvas/sliders updates the input and format cards.
- **Live Preview & Inspection Panel**:
  - Side-by-side color swatches: **Current** vs. **Initial** for comparison.
  - Live breakdown cards for HEX, RGBA, OKLCH, and HSL. Click any card to copy its value to the clipboard.
  - **WCAG 2.1 Contrast Analysis**: Live contrast ratios against `#000000` and `#ffffff` with `[AA Pass]`, `[AAA Pass]`, or `[Fail]` badges.
  - **Recent Color History**: Click any recent swatch to restore that color.
- **CLI & Shell Pipeline Integration**:
  - Built with **Typer**: clean flags, help menus, and exit codes.
  - Pressing `Enter` confirms selection, copies the color to clipboard, and prints it to `stdout`.
  - Non-interactive `convert` command for fast headless conversions.

---

## 🚀 Installation & Quick Start

Requires Python 3.13+ and [`uv`](https://docs.astral.sh/uv/).

### Run directly with `uvx` or `uv run`:
```bash
# Launch interactive color picker
uv run tui-color-picker

# Launch with a specific starting color
uv run tui-color-picker pick "#e11d48"

# Or with OKLCH:
uv run tui-color-picker pick "oklch(0.7 0.15 180)"
```

### Shell Pipeline Usage
Capture the picked color directly into shell variables or pipelines:
```bash
# Capture selected hex into a shell variable
COLOR=$(uv run tui-color-picker)
echo "You selected: $COLOR"

# Pick directly in OKLCH format
OKLCH_COLOR=$(uv run tui-color-picker --format oklch)
echo "OKLCH: $OKLCH_COLOR"
```

### Headless Conversion
```bash
# Convert OKLCH to Hex
uv run tui-color-picker convert "oklch(0.7 0.15 180)" --to hex
# Output: #00b8a1

# Convert Hex to OKLCH
uv run tui-color-picker convert "#ff0080" --to oklch
# Output: oklch(0.645 0.26 2.5)

# Convert RGBA to HSL
uv run tui-color-picker convert "rgba(255, 0, 128, 0.5)" --to hsl
# Output: hsla(330, 100%, 50%, 0.5)
```

---

## ⌨️ Controls & Keybindings

| Key / Action | Description |
|---|---|
| **Mouse Click / Drag** | Move reticle on canvas, slide Hue bar, slide Alpha bar |
| **Arrow Keys** (`←` `→` `↑` `↓`) | Fine-tune canvas color, Hue, or Alpha |
| **Shift + Arrow Keys** | Fast-step navigation |
| **Tab / Shift+Tab** | Move focus between Canvas, Hue, Alpha, Input, and Buttons |
| **c** | Quick-copy **HEX** to clipboard |
| **r** | Quick-copy **RGBA** to clipboard |
| **o** | Quick-copy **OKLCH** to clipboard |
| **Enter** | Confirm selection, copy to clipboard, print to `stdout`, and exit |
| **Esc** / **q** | Cancel and exit without outputting |

---

## 🧪 Testing

Run the test suite with `pytest`:
```bash
uv run pytest
```
