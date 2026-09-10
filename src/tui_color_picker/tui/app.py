"""Main Textual application for interactive TUI color picker."""

from __future__ import annotations

from typing import Optional
import pyperclip

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Button, Static, Label
from textual.reactive import reactive

from tui_color_picker.core import (
    ColorValue,
    parse_color_string,
    detect_color_format,
)
from tui_color_picker.tui.widgets import (
    ColorCanvas,
    HueBar,
    AlphaBar,
    ColorInputPanel,
    FormatCard,
    PreviewPanel,
)


class ColorPickerApp(App[Optional[str]]):
    """Interactive TrueColor TUI Color Picker."""

    TITLE = "🎨 TUI Color Picker"
    SUB_TITLE = "HEX • RGBA • OKLCH"

    CSS = """
    Screen {
        background: $background;
        overflow: hidden;
        align: center middle;
    }

    #size_warning {
        display: none;
        width: 100%;
        height: 100%;
        content-align: center middle;
        text-align: center;
        background: $background;
        color: $warning;
        text-style: bold;
    }

    Screen.too-small #size_warning {
        display: block;
    }

    Screen.too-small #scroll_wrapper {
        display: none;
    }

    #scroll_wrapper {
        width: 100%;
        height: 100%;
        overflow-y: auto;
        overflow-x: auto;
        align: center middle;
    }

    Screen.compact #scroll_wrapper {
        align: center top;
    }

    #main_layout {
        width: auto;
        height: auto;
        padding: 1 2;
        border: round $primary;
        background: $surface;
    }

    Screen.compact #main_layout {
        layout: vertical;
        padding: 1 1;
        border: none;
        background: transparent;
        align: center top;
    }

    #left_column {
        width: auto;
        height: auto;
        margin-right: 2;
    }

    Screen.compact #left_column {
        margin-right: 0;
        margin-bottom: 1;
        align: center top;
    }

    #canvas_row {
        width: auto;
        height: auto;
    }

    #instructions {
        margin-top: 1;
        color: $text-muted;
        text-align: center;
        width: 38;
    }

    #right_column {
        width: auto;
        height: auto;
    }

    Screen.compact #right_column {
        align: center top;
    }

    #button_row {
        margin-top: 1;
        width: auto;
        align: center middle;
        height: 3;
    }

    #button_row Button {
        margin: 0 1;
    }

    Screen.compact #button_row {
        width: 44;
        height: auto;
        align: center middle;
    }

    Screen.compact #button_row Button {
        margin: 0 0 1 0;
        width: 100%;
    }
    """

    BINDINGS = [
        Binding("enter", "confirm_selection", "Confirm & Copy", priority=True),
        Binding("escape", "cancel_selection", "Cancel", priority=True),
        Binding("q", "cancel_selection", "Quit", show=False),
        Binding("c", "copy_hex", "Copy Hex", show=True),
        Binding("r", "copy_rgba", "Copy RGBA", show=True),
        Binding("o", "copy_oklch", "Copy OKLCH", show=True),
    ]

    current_color: reactive[ColorValue]

    def __init__(
        self,
        initial_color_str: str = "#6366f1",
        default_format: str = "hex",
        auto_copy: bool = True,
    ) -> None:
        super().__init__()
        try:
            self.initial_color = parse_color_string(initial_color_str)
        except ValueError:
            self.initial_color = ColorValue.from_hsv(239.0, 0.58, 0.95)

        self.current_color = self.initial_color
        self.default_format = default_format.lower()
        self.auto_copy = auto_copy
        self._is_updating_ui = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            "⚠️ Terminal too small for color picker.\nPlease enlarge window (min 40x14).",
            id="size_warning",
        )
        with VerticalScroll(id="scroll_wrapper"):
            with Horizontal(id="main_layout"):
                # Left column: 2D Canvas + Hue Bar + Alpha Bar
                with Vertical(id="left_column"):
                    with Horizontal(id="canvas_row"):
                        yield ColorCanvas(
                            hue=self.current_color.h,
                            saturation=self.current_color.s,
                            value=self.current_color.v,
                            id="canvas",
                        )
                        yield HueBar(
                            hue=self.current_color.h,
                            id="hue_bar",
                        )
                    yield AlphaBar(
                        alpha=self.current_color.alpha,
                        rgb=(self.current_color.r, self.current_color.g, self.current_color.b),
                        id="alpha_bar",
                    )
                    yield Static(
                        "Mouse: Click/Drag | Arrows: Move | Tab: Next Widget",
                        id="instructions",
                    )

                # Right column: Multi-Format Input + Breakdown + Preview
                with Vertical(id="right_column"):
                    yield ColorInputPanel(id="input_panel")
                    yield PreviewPanel(self.initial_color, id="preview_panel")

            with Horizontal(id="button_row"):
                yield Button("Confirm & Exit (Enter)", variant="success", id="btn_confirm")
                yield Button("Copy Hex (c)", variant="primary", id="btn_copy_hex")
                yield Button("Copy RGBA (r)", variant="default", id="btn_copy_rgba")
                yield Button("Copy OKLCH (o)", variant="default", id="btn_copy_oklch")
                yield Button("Cancel (Esc)", variant="error", id="btn_cancel")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize widgets with the starting color and responsive layout mode."""
        size = self.size
        is_too_small = size.width < 40 or size.height < 14
        is_compact = size.width < 88
        self.screen.set_class(is_too_small, "too-small")
        self.screen.set_class(is_compact and not is_too_small, "compact")

        input_panel = self.query_one("#input_panel", ColorInputPanel)
        input_panel.update_from_color(self.current_color, update_input=True)

        preview_panel = self.query_one("#preview_panel", PreviewPanel)
        preview_panel.update_current_color(self.current_color)
        preview_panel.record_history(self.current_color)

    def on_resize(self, event: events.Resize) -> None:
        """Handle terminal resize dynamically with responsive layout classes."""
        is_too_small = event.size.width < 40 or event.size.height < 14
        is_compact = event.size.width < 88
        self.screen.set_class(is_too_small, "too-small")
        self.screen.set_class(is_compact and not is_too_small, "compact")

    def _sync_to_widgets(self, source: str) -> None:
        """Synchronize current_color across all other widgets."""
        if self._is_updating_ui:
            return
        self._is_updating_ui = True
        try:
            canvas = self.query_one("#canvas", ColorCanvas)
            hue_bar = self.query_one("#hue_bar", HueBar)
            alpha_bar = self.query_one("#alpha_bar", AlphaBar)
            input_panel = self.query_one("#input_panel", ColorInputPanel)
            preview_panel = self.query_one("#preview_panel", PreviewPanel)

            # Sync Canvas
            if source != "canvas":
                canvas.hue = self.current_color.h
                canvas.saturation = self.current_color.s
                canvas.value = self.current_color.v

            # Sync Hue Bar
            if source != "hue_bar":
                hue_bar.hue = self.current_color.h

            # Sync Alpha Bar
            if source != "alpha_bar":
                alpha_bar.alpha = self.current_color.alpha
            alpha_bar.rgb = (self.current_color.r, self.current_color.g, self.current_color.b)

            # Sync Input Panel
            if source != "input":
                input_panel.update_from_color(self.current_color, update_input=True)

            # Sync Preview Panel
            preview_panel.update_current_color(self.current_color)
        finally:
            self._is_updating_ui = False

    def on_color_canvas_changed(self, event: ColorCanvas.Changed) -> None:
        """Handled when user moves canvas reticle."""
        self.current_color = self.current_color.with_hsv(
            s=event.saturation,
            v=event.value,
        )
        self._sync_to_widgets(source="canvas")

    def on_hue_bar_changed(self, event: HueBar.Changed) -> None:
        """Handled when user changes Hue."""
        self.current_color = self.current_color.with_hsv(h=event.hue)
        self._sync_to_widgets(source="hue_bar")

    def on_alpha_bar_changed(self, event: AlphaBar.Changed) -> None:
        """Handled when user changes Alpha."""
        self.current_color = self.current_color.with_alpha(event.alpha)
        self._sync_to_widgets(source="alpha_bar")

    def on_color_input_panel_color_changed(self, event: ColorInputPanel.ColorChanged) -> None:
        """Handled in real-time as user types into the input field."""
        self.current_color = event.color
        self._sync_to_widgets(source="input")

    def on_color_input_panel_color_submitted(self, event: ColorInputPanel.ColorSubmitted) -> None:
        """Handled when user presses Enter inside the input field."""
        self.current_color = event.color
        self.action_confirm_selection()

    def on_format_card_copy_requested(self, event: FormatCard.CopyRequested) -> None:
        """Handled when user clicks a format card."""
        self._copy_and_notify(event.value, event.format_name)

    def on_history_strip_color_selected(self, event) -> None:
        """Handled when user clicks a history swatch."""
        self.current_color = event.color
        self._sync_to_widgets(source="history")
        self.notify(f"Loaded {event.color.hex} from history", timeout=2)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn_confirm":
            self.action_confirm_selection()
        elif btn_id == "btn_copy_hex":
            self.action_copy_hex()
        elif btn_id == "btn_copy_rgba":
            self.action_copy_rgba()
        elif btn_id == "btn_copy_oklch":
            self.action_copy_oklch()
        elif btn_id == "btn_cancel":
            self.action_cancel_selection()

    def _copy_and_notify(self, text: str, label: str) -> None:
        """Copy text to clipboard and display notification."""
        try:
            pyperclip.copy(text)
        except Exception:
            pass
        try:
            self.copy_to_clipboard(text)
        except Exception:
            pass
        self.notify(f"Copied {label}: {text}", timeout=2)

    def action_copy_hex(self) -> None:
        self._copy_and_notify(self.current_color.hex, "HEX")

    def action_copy_rgba(self) -> None:
        self._copy_and_notify(self.current_color.rgba_str, "RGBA")

    def action_copy_oklch(self) -> None:
        self._copy_and_notify(self.current_color.oklch_str, "OKLCH")

    def _get_output_formatted(self) -> str:
        """Return the formatted color string based on default_format setting."""
        fmt = self.default_format
        if fmt == "rgba" or fmt == "rgb":
            return self.current_color.rgba_str
        elif fmt == "oklch" or fmt == "okclh":
            return self.current_color.oklch_str
        elif fmt == "hsl":
            return self.current_color.hsl_str
        return self.current_color.hex

    def action_confirm_selection(self) -> None:
        """Confirm selection, copy to clipboard, record in history, and exit."""
        out = self._get_output_formatted()
        if self.auto_copy:
            try:
                pyperclip.copy(out)
            except Exception:
                pass
            try:
                self.copy_to_clipboard(out)
            except Exception:
                pass
        self.exit(out)

    def action_cancel_selection(self) -> None:
        """Cancel selection and exit without returning a color."""
        self.exit(None)
