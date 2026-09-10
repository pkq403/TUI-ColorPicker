import pytest
from textual.widgets import Input
from tui_color_picker.tui.app import ColorPickerApp
from tui_color_picker.tui.widgets import (
    ColorCanvas,
    ColorInputPanel,
    FormatCard,
    HueBar,
    AlphaBar,
)


@pytest.mark.asyncio
async def test_app_initialization():
    app = ColorPickerApp(initial_color_str="#ff0080", default_format="hex")
    async with app.run_test() as pilot:
        canvas = app.query_one("#canvas", ColorCanvas)
        assert canvas is not None
        assert app.current_color.hex == "#ff0080"

        input_field = app.query_one("#color_input", Input)
        assert input_field.value == "#ff0080"


@pytest.mark.asyncio
async def test_app_input_typing_hex():
    app = ColorPickerApp(initial_color_str="#000000")
    async with app.run_test() as pilot:
        input_field = app.query_one("#color_input", Input)
        input_field.value = "#00ff00"
        await pilot.pause()

        # Canvas and current color should update
        assert app.current_color.hex == "#00ff00"
        canvas = app.query_one("#canvas", ColorCanvas)
        assert round(canvas.hue) == 120
        assert canvas.saturation == 1.0


@pytest.mark.asyncio
async def test_app_input_typing_oklch():
    app = ColorPickerApp()
    async with app.run_test() as pilot:
        input_field = app.query_one("#color_input", Input)
        # Type oklch
        input_field.value = "oklch(0.7 0.15 180)"
        await pilot.pause()

        assert app.current_color.oklch_l == pytest.approx(0.7, abs=0.01)

        # Type okclh typo
        input_field.value = "okclh(0.6 0.2 240)"
        await pilot.pause()
        assert app.current_color.oklch_l == pytest.approx(0.6, abs=0.01)


@pytest.mark.asyncio
async def test_app_canvas_movement_syncs_input():
    app = ColorPickerApp(initial_color_str="#ff0000")
    async with app.run_test() as pilot:
        canvas = app.query_one("#canvas", ColorCanvas)
        canvas.focus()
        await pilot.press("left")
        await pilot.pause()

        input_field = app.query_one("#color_input", Input)
        assert input_field.value.startswith("#")
        assert input_field.value != "#ff0000"


@pytest.mark.asyncio
async def test_app_exit_confirm():
    app = ColorPickerApp(initial_color_str="#123456", default_format="hex")
    async with app.run_test() as pilot:
        await pilot.press("enter")
        assert app.return_value == "#123456"


@pytest.mark.asyncio
async def test_app_exit_format_oklch():
    app = ColorPickerApp(initial_color_str="#123456", default_format="oklch")
    async with app.run_test() as pilot:
        await pilot.press("enter")
        assert app.return_value.startswith("oklch(")


@pytest.mark.asyncio
async def test_app_exit_cancel():
    app = ColorPickerApp(initial_color_str="#123456")
    async with app.run_test() as pilot:
        await pilot.press("escape")
        assert app.return_value is None


@pytest.mark.asyncio
async def test_app_terminal_resize_resilience():
    """Verify that resizing the terminal dynamically adapts between wide, compact, and warning modes."""
    app = ColorPickerApp(initial_color_str="#6366f1")
    async with app.run_test(size=(120, 35)) as pilot:
        # 1. Wide terminal mode
        assert "compact" not in app.screen.classes
        assert "too-small" not in app.screen.classes

        # 2. Resize to standard 80x24 terminal
        await pilot.resize_terminal(80, 24)
        assert "compact" in app.screen.classes
        assert "too-small" not in app.screen.classes

        # Verify interaction in compact mode
        canvas = app.query_one("#canvas", ColorCanvas)
        canvas.focus()
        await pilot.press("right")
        assert app.current_color.s > 0.0

        # 3. Resize to micro terminal (too small)
        await pilot.resize_terminal(32, 10)
        assert "too-small" in app.screen.classes

        # 4. Resize back to wide
        await pilot.resize_terminal(110, 35)
        assert "compact" not in app.screen.classes
        assert "too-small" not in app.screen.classes


@pytest.mark.asyncio
async def test_app_pointer_shape_never_changes_to_text():
    """Verify that clicking and dragging in the app keeps the pointer as default and does not enter text insert mode."""
    app = ColorPickerApp()
    async with app.run_test(size=(120, 35)) as pilot:
        assert app.ALLOW_SELECT is False

        # 1. Click and drag on canvas
        await pilot.mouse_down(ColorCanvas, offset=(5, 5))
        await pilot.hover(ColorCanvas, offset=(15, 10))
        assert app.screen._selecting is False
        assert app.screen._pointer_shape != "text"
        await pilot.mouse_up()

        # 2. Click and drag on HueBar
        await pilot.mouse_down(HueBar, offset=(2, 3))
        await pilot.hover(HueBar, offset=(2, 8))
        assert app.screen._selecting is False
        assert app.screen._pointer_shape != "text"
        await pilot.mouse_up()

        # 3. Click and drag on AlphaBar
        await pilot.mouse_down(AlphaBar, offset=(5, 1))
        await pilot.hover(AlphaBar, offset=(20, 1))
        assert app.screen._selecting is False
        assert app.screen._pointer_shape != "text"
        await pilot.mouse_up()


