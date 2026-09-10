import pytest
from textual.widgets import Input
from tui_color_picker.tui.app import ColorPickerApp
from tui_color_picker.tui.widgets import ColorCanvas, ColorInputPanel, FormatCard


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
