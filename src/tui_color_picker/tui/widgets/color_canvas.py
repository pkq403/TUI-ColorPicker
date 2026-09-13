"""Interactive 2D Color Palette Square rendered with ANSI TrueColor and half-blocks."""

from __future__ import annotations

import math
from typing import ClassVar
from rich.text import Text
from rich.style import Style
from textual import events
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget


def _hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    """Fast HSV to sRGB conversion."""
    c = v * s
    x = c * (1.0 - abs((h / 60.0) % 2.0 - 1.0))
    m = v - c
    h_mod = h % 360.0

    if 0.0 <= h_mod < 60.0:
        r, g, b = c, x, 0.0
    elif 60.0 <= h_mod < 120.0:
        r, g, b = x, c, 0.0
    elif 120.0 <= h_mod < 180.0:
        r, g, b = 0.0, c, x
    elif 180.0 <= h_mod < 240.0:
        r, g, b = 0.0, x, c
    elif 240.0 <= h_mod < 300.0:
        r, g, b = x, 0.0, c
    else:
        r, g, b = c, 0.0, x

    return (
        int((r + m) * 255.0 + 0.5),
        int((g + m) * 255.0 + 0.5),
        int((b + m) * 255.0 + 0.5),
    )


class ColorCanvas(Widget):
    DEFAULT_CSS = """
    ColorCanvas {
        width: 32;
        height: 16;
        border: solid $accent;
        pointer: default;
    }
    ColorCanvas:focus {
        border: double $primary;
    }
    """

    can_focus = True
    ALLOW_SELECT = False

    class Changed(Message):
        """Emitted when the user changes the saturation or value."""

        def __init__(self, saturation: float, value: float) -> None:
            super().__init__()
            self.saturation = saturation
            self.value = value

    hue: reactive[float] = reactive(0.0)
    saturation: reactive[float] = reactive(1.0)
    value: reactive[float] = reactive(1.0)

    _is_dragging: bool = False

    def __init__(
        self,
        hue: float = 0.0,
        saturation: float = 1.0,
        value: float = 1.0,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.hue = hue
        self.saturation = saturation
        self.value = value

    def render(self) -> Text:
        """Render the 2D gradient square and reticle."""
        # Available content dimensions
        width = max(8, self.content_size.width or 30)
        height = max(4, self.content_size.height or 14)

        # Map current saturation and value to cell coordinates
        cursor_x = int(round(self.saturation * (width - 1)))
        # subpixel y in [0, height * 2 - 1], 0 is top (V=1.0)
        cursor_sub_y = int(round((1.0 - self.value) * (height * 2 - 1)))
        cursor_row = cursor_sub_y // 2
        cursor_is_top = (cursor_sub_y % 2 == 0)

        result = Text()

        for row in range(height):
            for col in range(width):
                s = col / float(width - 1) if width > 1 else 0.0

                # Top subpixel value
                v_top = 1.0 - (row * 2) / float(height * 2 - 1)
                # Bottom subpixel value
                v_bot = 1.0 - (row * 2 + 1) / float(height * 2 - 1)

                r_top, g_top, b_top = _hsv_to_rgb(self.hue, s, v_top)
                r_bot, g_bot, b_bot = _hsv_to_rgb(self.hue, s, v_bot)

                if col == cursor_x and row == cursor_row:
                    # Draw reticle cursor on this cell
                    # Pick high-contrast text color against the active subpixel
                    active_v = v_top if cursor_is_top else v_bot
                    contrast_color = "black" if (active_v > 0.55 and s < 0.6) or (active_v > 0.75) else "white"
                    reticle_char = "⊙"

                    cell_bg = f"rgb({r_top},{g_top},{b_top})" if cursor_is_top else f"rgb({r_bot},{g_bot},{b_bot})"
                    result.append(
                        reticle_char,
                        style=Style(color=contrast_color, bgcolor=cell_bg, bold=True),
                    )
                else:
                    # Normal gradient half-block
                    result.append(
                        "▀",
                        style=Style(
                            color=f"rgb({r_top},{g_top},{b_top})",
                            bgcolor=f"rgb({r_bot},{g_bot},{b_bot})",
                        ),
                    )

            if row < height - 1:
                result.append("\n")

        return result

    def _update_from_mouse(self, x: int, y: int) -> None:
        """Update saturation and value based on mouse coordinates."""
        width = max(8, self.content_size.width or 30)
        height = max(4, self.content_size.height or 14)

        content_x = x - (self.gutter.left if hasattr(self, "gutter") else 0)
        content_y = y - (self.gutter.top if hasattr(self, "gutter") else 0)

        clamped_x = max(1, min(width - 1, content_x))
        clamped_y = max(0, min(height - 1, content_y))

        new_s = clamped_x / float(width - 1) if width > 1 else 0.0
        new_v = 1.0 - (clamped_y / float(height - 1)) if height > 1 else 1.0
        self.saturation = round(new_s, 3)
        self.value = round(new_v, 3)
        self.post_message(self.Changed(self.saturation, self.value))

    def on_mouse_down(self, event: events.MouseDown) -> None:
        self.focus()
        self._is_dragging = True
        self.capture_mouse()
        self._update_from_mouse(event.x, event.y)

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if self._is_dragging:
            self._update_from_mouse(event.x, event.y)

    def on_mouse_up(self, event: events.MouseUp) -> None:
        if self._is_dragging:
            self._update_from_mouse(event.x, event.y)
            self._is_dragging = False
            self.release_mouse()

    def on_key(self, event: events.Key) -> None:
        step = 0.08 if "shift" in event.key else 0.02
        key = event.key.lower()

        if "left" in key:
            self.saturation = max(0.0, round(self.saturation - step, 3))
            self.post_message(self.Changed(self.saturation, self.value))
            event.stop()
        elif "right" in key:
            self.saturation = min(1.0, round(self.saturation + step, 3))
            self.post_message(self.Changed(self.saturation, self.value))
            event.stop()
        elif "up" in key:
            self.value = min(1.0, round(self.value + step, 3))
            self.post_message(self.Changed(self.saturation, self.value))
            event.stop()
        elif "down" in key:
            self.value = max(0.0, round(self.value - step, 3))
            self.post_message(self.Changed(self.saturation, self.value))
            event.stop()
