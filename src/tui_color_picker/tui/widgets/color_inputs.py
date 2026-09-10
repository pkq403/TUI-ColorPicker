"""Multi-format smart color input and format cards widget."""

from __future__ import annotations

from rich.text import Text
from rich.style import Style
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input, Static, Label, Button

from tui_color_picker.core import (
    ColorValue,
    parse_color_string,
    detect_color_format,
)


class FormatCard(Static):
    """Readout card for a specific color format with quick copy trigger."""

    DEFAULT_CSS = """
    FormatCard {
        height: 3;
        margin-bottom: 1;
        padding: 0 1;
        background: $surface;
        border: round $primary-muted;
    }
    FormatCard:hover {
        border: round $accent;
        background: $surface-lighten-1;
    }
    """

    class CopyRequested(Message):
        """Emitted when user clicks to copy this format."""

        def __init__(self, format_name: str, value: str) -> None:
            super().__init__()
            self.format_name = format_name
            self.value = value

    def __init__(self, format_name: str, value: str = "", *, id: str | None = None) -> None:
        super().__init__(id=id)
        self.format_name = format_name
        self.value = value

    def update_value(self, value: str) -> None:
        self.value = value
        self.refresh()

    def render(self) -> Text:
        t = Text()
        t.append(f"{self.format_name:<6} ", style="bold cyan")
        t.append(f"{self.value:<26}", style="bold white")
        t.append(" (click/copy)", style="dim italic")
        return t

    def on_click(self) -> None:
        self.post_message(self.CopyRequested(self.format_name, self.value))


class ColorInputPanel(Vertical):
    """Right-side panel with multi-format smart input and live breakdown cards."""

    DEFAULT_CSS = """
    ColorInputPanel {
        width: 44;
        height: auto;
        padding: 0 1;
    }
    #input_title {
        text-style: bold;
        color: $accent;
        margin-bottom: 0;
    }
    #color_input {
        margin-top: 0;
        margin-bottom: 0;
        border: tall $accent;
    }
    #color_input:focus {
        border: tall $primary;
    }
    #format_badge {
        margin-bottom: 1;
        color: $text-muted;
    }
    """

    class ColorSubmitted(Message):
        """Emitted when user presses enter on input or a valid color is parsed."""

        def __init__(self, color: ColorValue, format_type: str) -> None:
            super().__init__()
            self.color = color
            self.format_type = format_type

    class ColorChanged(Message):
        """Emitted in real-time as user types a valid color string."""

        def __init__(self, color: ColorValue, format_type: str) -> None:
            super().__init__()
            self.color = color
            self.format_type = format_type

    def compose(self) -> ComposeResult:
        yield Label("Color Input (HEX / RGBA / OKLCH):", id="input_title")
        yield Input(
            placeholder="#ff5500, rgba(255,0,128,0.5), oklch(0.7 0.15 180)",
            id="color_input",
        )
        yield Label("[Format: HEX] (Valid)", id="format_badge")

        yield FormatCard("HEX", id="card_hex")
        yield FormatCard("RGBA", id="card_rgba")
        yield FormatCard("OKLCH", id="card_oklch")
        yield FormatCard("HSL", id="card_hsl")

    def update_from_color(self, color: ColorValue, update_input: bool = True) -> None:
        """Update readouts and input text to reflect the given color."""
        card_hex = self.query_one("#card_hex", FormatCard)
        card_rgba = self.query_one("#card_rgba", FormatCard)
        card_oklch = self.query_one("#card_oklch", FormatCard)
        card_hsl = self.query_one("#card_hsl", FormatCard)

        card_hex.update_value(color.hex)
        card_rgba.update_value(color.rgba_str)
        card_oklch.update_value(color.oklch_str)
        card_hsl.update_value(color.hsl_str)

        if update_input:
            input_widget = self.query_one("#color_input", Input)
            # Only update if value actually changed to prevent cursor jump
            if input_widget.value != color.hex:
                input_widget.value = color.hex
                badge = self.query_one("#format_badge", Label)
                badge.update("[Format: HEX] (Valid)")
                badge.styles.color = "green"

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle live typing in the smart input."""
        text = event.value.strip()
        badge = self.query_one("#format_badge", Label)
        if not text:
            badge.update("[Empty input]")
            badge.styles.color = "gray"
            return

        fmt = detect_color_format(text).upper()
        try:
            color = parse_color_string(text)
            badge.update(f"[Format: {fmt}] (Valid)")
            badge.styles.color = "green"

            # Update format cards in real-time
            self.query_one("#card_hex", FormatCard).update_value(color.hex)
            self.query_one("#card_rgba", FormatCard).update_value(color.rgba_str)
            self.query_one("#card_oklch", FormatCard).update_value(color.oklch_str)
            self.query_one("#card_hsl", FormatCard).update_value(color.hsl_str)

            self.post_message(self.ColorChanged(color, fmt))
        except ValueError:
            badge.update(f"[Format: {fmt}] (Incomplete / Invalid)")
            badge.styles.color = "yellow"

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in the smart input."""
        text = event.value.strip()
        try:
            color = parse_color_string(text)
            fmt = detect_color_format(text).upper()
            self.post_message(self.ColorSubmitted(color, fmt))
        except ValueError:
            pass
