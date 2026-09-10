"""Hue and Alpha slider widgets for color selection."""

from __future__ import annotations

from rich.text import Text
from rich.style import Style
from textual import events
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget

from .color_canvas import _hsv_to_rgb


class HueBar(Widget):
    """Vertical Hue slider bar (0° to 360°)."""

    DEFAULT_CSS = """
    HueBar {
        width: 5;
        height: 16;
        border: solid $accent;
        margin-left: 1;
        pointer: default;
    }
    HueBar:focus {
        border: double $primary;
    }
    """

    can_focus = True
    ALLOW_SELECT = False

    class Changed(Message):
        """Emitted when the user changes the hue."""

        def __init__(self, hue: float) -> None:
            super().__init__()
            self.hue = hue

    hue: reactive[float] = reactive(0.0)
    _is_dragging: bool = False

    def __init__(
        self,
        hue: float = 0.0,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.hue = hue

    def render(self) -> Text:
        height = max(4, self.content_size.height or 14)
        result = Text()

        # Row corresponding to current hue
        active_row = int(round((self.hue / 360.0) * (height - 1))) if height > 1 else 0

        for row in range(height):
            # Top subpixel hue
            h_top = (row * 2 / float(height * 2 - 1)) * 360.0
            # Bottom subpixel hue
            h_bot = ((row * 2 + 1) / float(height * 2 - 1)) * 360.0

            r_top, g_top, b_top = _hsv_to_rgb(h_top, 1.0, 1.0)
            r_bot, g_bot, b_bot = _hsv_to_rgb(h_bot, 1.0, 1.0)

            style = Style(
                color=f"rgb({r_top},{g_top},{b_bot})",
                bgcolor=f"rgb({r_bot},{g_bot},{b_bot})",
            )
            result.append("▀▀", style=style)

            # Indicator arrow
            if row == active_row:
                result.append("◀", style=Style(color="white", bold=True))
            else:
                result.append(" ")

            if row < height - 1:
                result.append("\n")

        return result

    def _update_from_mouse(self, y: int) -> None:
        height = max(4, self.content_size.height or 14)
        content_y = y - (self.gutter.top if hasattr(self, "gutter") else 0)
        clamped_y = max(0, min(height - 1, content_y))
        new_hue = (clamped_y / float(height - 1)) * 360.0 if height > 1 else 0.0
        self.hue = round(new_hue, 1)
        self.post_message(self.Changed(self.hue))

    def on_mouse_down(self, event: events.MouseDown) -> None:
        self.focus()
        self._is_dragging = True
        self.capture_mouse()
        self._update_from_mouse(event.y)

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if self._is_dragging:
            self._update_from_mouse(event.y)

    def on_mouse_up(self, event: events.MouseUp) -> None:
        if self._is_dragging:
            self._is_dragging = False
            self.release_mouse()
            self._update_from_mouse(event.y)

    def on_key(self, event: events.Key) -> None:
        step = 20.0 if "shift" in event.key else 5.0
        key = event.key.lower()

        if "up" in key:
            self.hue = max(0.0, round(self.hue - step, 1))
            self.post_message(self.Changed(self.hue))
            event.stop()
        elif "down" in key:
            self.hue = min(360.0, round(self.hue + step, 1))
            self.post_message(self.Changed(self.hue))
            event.stop()


class AlphaBar(Widget):
    """Horizontal Alpha / Opacity slider bar (0.0 to 1.0)."""

    DEFAULT_CSS = """
    AlphaBar {
        width: 38;
        height: 4;
        border: solid $accent;
        margin-top: 1;
        pointer: default;
    }
    AlphaBar:focus {
        border: double $primary;
    }
    """

    can_focus = True
    ALLOW_SELECT = False

    class Changed(Message):
        """Emitted when the user changes the alpha value."""

        def __init__(self, alpha: float) -> None:
            super().__init__()
            self.alpha = alpha

    alpha: reactive[float] = reactive(1.0)
    # Color to display on the opacity bar
    rgb: reactive[tuple[int, int, int]] = reactive((255, 0, 0))
    _is_dragging: bool = False

    def __init__(
        self,
        alpha: float = 1.0,
        rgb: tuple[int, int, int] = (255, 0, 0),
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.alpha = alpha
        self.rgb = rgb

    def render(self) -> Text:
        width = max(8, self.content_size.width or 36)
        result = Text()

        # Row 0: Alpha gradient bar with checkered background blend
        r_c, g_c, b_c = self.rgb
        for col in range(width):
            a = col / float(width - 1) if width > 1 else 1.0
            check = 190 if (col % 2 == 0) else 90
            r = int(r_c * a + check * (1.0 - a) + 0.5)
            g = int(g_c * a + check * (1.0 - a) + 0.5)
            b = int(b_c * a + check * (1.0 - a) + 0.5)
            result.append("█", style=Style(color=f"rgb({r},{g},{b})"))

        result.append("\n")

        # Row 1: Indicator pointer
        marker_col = int(round(self.alpha * (width - 1))) if width > 1 else 0
        for col in range(width):
            if col == marker_col:
                result.append("▲", style=Style(color="white", bold=True))
            else:
                result.append(" ")

        return result

    def _update_from_mouse(self, x: int) -> None:
        width = max(8, self.content_size.width or 36)
        content_x = x - (self.gutter.left if hasattr(self, "gutter") else 0)
        clamped_x = max(0, min(width - 1, content_x))
        new_alpha = clamped_x / float(width - 1) if width > 1 else 1.0
        self.alpha = round(new_alpha, 2)
        self.post_message(self.Changed(self.alpha))

    def on_mouse_down(self, event: events.MouseDown) -> None:
        self.focus()
        self._is_dragging = True
        self.capture_mouse()
        self._update_from_mouse(event.x)

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if self._is_dragging:
            self._update_from_mouse(event.x)

    def on_mouse_up(self, event: events.MouseUp) -> None:
        if self._is_dragging:
            self._update_from_mouse(event.x)
            self._is_dragging = False
            self.release_mouse()

    def on_key(self, event: events.Key) -> None:
        step = 0.10 if "shift" in event.key else 0.02
        key = event.key.lower()

        if "left" in key:
            self.alpha = max(0.0, round(self.alpha - step, 2))
            self.post_message(self.Changed(self.alpha))
            event.stop()
        elif "right" in key:
            self.alpha = min(1.0, round(self.alpha + step, 2))
            self.post_message(self.Changed(self.alpha))
            event.stop()
