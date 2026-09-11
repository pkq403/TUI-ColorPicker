# 🎨 TUI Color Picker (`color-picker`)

A terminal-based color picker built with Python. Features an interactive 2D color palette square rendered with TrueColor half-blocks, Hue and Alpha sliders, live bidirectional synchronization with a smart multi-format input (Hex, RGBA, OKLCH, HSL), WCAG contrast checks, and a fast CLI interface.

Once installed, simply type **`color-picker`** in your Linux terminal to launch!

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
  - Direct execution via `color-picker` (alias `tui-color-picker` also provided).
  - Clean flags, help menus, and exit codes.
  - Pressing `Enter` confirms selection, copies the color to clipboard, and prints it to `stdout`.
  - Non-interactive `convert` command for fast headless conversions.

---

## 🚀 Installation on Linux

Requires **Python 3.13+**.

### Option 1: One-Command Installer Script (Recommended)

From the project root, run the installer:

```bash
./install.sh
# or using Make:
make install
```

The script automatically detects whether you have [`uv`](https://docs.astral.sh/uv/), [`pipx`](https://pypa.github.io/pipx/), or standard `python3`, and installs `color-picker` into `~/.local/bin`.

### Option 2: Using `uv`

If you use `uv`:

```bash
uv tool install .
```

### Option 3: Using `pipx`

If you use `pipx`:

```bash
pipx install .
```

### 📌 Ensure `~/.local/bin` is in your `PATH`

On most Linux distributions, `~/.local/bin` is already in your `$PATH`. If running `color-picker` says "command not found", add it to your shell configuration:

```bash
# For Bash (~/.bashrc):
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# For Zsh (~/.zshrc):
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 🗑️ Uninstalling

To uninstall at any time:

```bash
./install.sh --uninstall
# or
make uninstall
# or (if installed with uv)
uv tool uninstall tui-color-picker
```

---

## 💻 Quick Start & Usage

Once installed, run `color-picker` directly in your terminal:

```bash
# Launch interactive color picker with default color
color-picker

# Launch with a specific starting color
color-picker pick "#e11d48"

# Launch with OKLCH format
color-picker pick "oklch(0.7 0.15 180)"

# Launch specifying output format
color-picker --format oklch
```

*(Note: `tui-color-picker` can also be typed as an alternate command name.)*

### Run Without Installing

You can also run it directly without installing via `uv`:

```bash
uv run color-picker
```

### Shell Pipeline Usage

Capture the picked color directly into shell variables or pipelines:

```bash
# Capture selected hex into a shell variable
COLOR=$(color-picker)
echo "You selected: $COLOR"

# Pick directly in OKLCH format
OKLCH_COLOR=$(color-picker --format oklch)
echo "OKLCH: $OKLCH_COLOR"
```

### Headless Conversion

Convert color formats directly from the command line without opening the TUI:

```bash
# Convert OKLCH to Hex
color-picker convert "oklch(0.7 0.15 180)" --to hex
# Output: #00b8a1

# Convert Hex to OKLCH
color-picker convert "#ff0080" --to oklch
# Output: oklch(0.645 0.26 2.5)

# Convert RGBA to HSL
color-picker convert "rgba(255, 0, 128, 0.5)" --to hsl
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
# or
make test
```
