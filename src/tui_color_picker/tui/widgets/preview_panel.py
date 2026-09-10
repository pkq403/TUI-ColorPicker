"""Color preview swatch, contrast indicators, and session history widget."""

from __future__ import annotations

from typing import List
from rich.text import Text
from rich.style import Style
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.message import Message
from textual.widgets import Static, Label

from tui_color_picker.core import ColorValue, calculate_contrast, ContrastReport


class ColorSwatch(Static):
    """Visual preview block for a color."""

    DEFAULT_CSS = """
    ColorSwatch {
        height: 4;
        width: 16;
        border: solid $accent;
        padding: 0;
        content-align: center middle;
    }
    """

    def __init__(self, color: ColorValue, label: str = "", *, id: str | None = None) -> None:
        super().__init__(id=id)
        self.color = color
        self.label = label

    def set_color(self, color: ColorValue) -> None:
        self.color = color
        self.refresh()

    def render(self) -> Text:
        # Determine background color blended with terminal or check
        r, g, b = self.color.r, self.color.g, self.color.b
        a = self.color.alpha

        # Blend over neutral grey checkerboard if transparent
        bg_r = int(r * a + 50 * (1.0 - a) + 0.5)
        bg_g = int(g * a + 50 * (1.0 - a) + 0.5)
        bg_b = int(b * a + 50 * (1.0 - a) + 0.5)

        contrast = calculate_contrast(self.color)
        text_color = contrast.best_text_color

        lines = []
        cell_style = Style(color=text_color, bgcolor=f"rgb({bg_r},{bg_g},{bg_b})", bold=True)

        t = Text()
        t.append(f" {self.label}\n", style=cell_style)
        t.append(f" {self.color.hex}\n", style=cell_style)
        if a < 0.999:
            t.append(f" α: {int(a * 100)}% ", style=cell_style)
        else:
            t.append(f"         ", style=cell_style)
        return t


class ContrastCard(Static):
    """WCAG Contrast breakdown."""

    DEFAULT_CSS = """
    ContrastCard {
        height: 4;
        margin-top: 1;
        padding: 0 1;
        background: $surface;
        border: round $primary-muted;
    }
    """

    def __init__(self, color: ColorValue, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self.color = color

    def update_color(self, color: ColorValue) -> None:
        self.color = color
        self.refresh()

    def render(self) -> Text:
        report = calculate_contrast(self.color)
        t = Text()
        t.append("WCAG Contrast:\n", style="bold yellow")

        # White contrast
        t.append(f"on White: {report.contrast_white:.1f}:1 ", style="white")
        if report.aaa_normal_white:
            t.append("[AAA Pass] ", style="bold green")
        elif report.aa_normal_white:
            t.append("[AA Pass] ", style="green")
        else:
            t.append("[Fail] ", style="bold red")

        t.append("\n")

        # Black contrast
        t.append(f"on Black: {report.contrast_black:.1f}:1 ", style="white")
        if report.aaa_normal_black:
            t.append("[AAA Pass]", style="bold green")
        elif report.aa_normal_black:
            t.append("[AA Pass]", style="green")
        else:
            t.append("[Fail]", style="bold red")

        return t


class HistoryStrip(Static):
    """Recent color swatches strip."""

    DEFAULT_CSS = """
    HistoryStrip {
        height: 2;
        margin-top: 1;
    }
    """

    class ColorSelected(Message):
        """Emitted when user clicks a recent color swatch."""

        def __init__(self, color: ColorValue) -> None:
            super().__init__()
            self.color = color

    def __init__(self, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self.history: List[ColorValue] = []

    def add_color(self, color: ColorValue) -> None:
        # Avoid consecutive duplicates
        if self.history and self.history[-1].hex == color.hex:
            return
        self.history.append(color)
        if len(self.history) > 10:
            self.history.pop(0)
        self.refresh()

    def render(self) -> Text:
        t = Text()
        t.append("History: ", style="bold dim")
        if not self.history:
            t.append("(empty)", style="dim italic")
            return t

        for idx, col in enumerate(self.history):
            t.append("██", style=Style(color=f"rgb({col.r},{col.g},{col.b})"))
            t.append(" ")
        return t

    def on_click(self, event) -> None:
        # Map click to history index
        # "History: " is 9 chars, each swatch is 3 chars ("██ ")
        offset_x = event.x - 9
        if offset_x >= 0 and self.history:
            idx = offset_x // 3
            if 0 <= idx < len(self.history):
                self.post_message(self.ColorSelected(self.history[idx]))


class PreviewPanel(Vertical):
    """Panel combining current/initial swatches, contrast report, and history."""

    DEFAULT_CSS = """
    PreviewPanel {
        width: 36;
        height: auto;
        padding: 0 1;
    }
    .swatch-row {
        height: 5;
    }
    """

    def __init__(self, initial_color: ColorValue, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self.initial_color = initial_color
        self.current_color = initial_color

    def compose(self) -> ComposeResult:
        with Horizontal(classes="swatch-row"):
            yield ColorSwatch(self.current_color, label="Current", id="swatch_current")
            yield ColorSwatch(self.initial_color, label="Initial", id="swatch_initial")
        yield ContrastCard(self.current_color, id="contrast_card")
        yield HistoryStrip(id="history_strip")

    def update_current_color(self, color: ColorValue) -> None:
        self.current_color = color
        self.query_one("#swatch_current", ColorSwatch).set_color(color)
        self.query_one("#contrast_card", ContrastCard).update_color(color)

    def record_history(self, color: ColorValue) -> None:
        self.query_one("#history_strip", HistoryStrip).add_color(color)
