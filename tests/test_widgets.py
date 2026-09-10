import pytest
from textual.app import App, ComposeResult
from tui_color_picker.tui.widgets import ColorCanvas, HueBar, AlphaBar


class WidgetTestApp(App):
    def compose(self) -> ComposeResult:
        yield ColorCanvas(hue=120.0, saturation=0.5, value=0.8, id="canvas")
        yield HueBar(hue=180.0, id="hue_bar")
        yield AlphaBar(alpha=0.75, id="alpha_bar")


@pytest.mark.asyncio
async def test_color_canvas_interactions():
    app = WidgetTestApp()
    async with app.run_test() as pilot:
        canvas = app.query_one("#canvas", ColorCanvas)
        assert canvas.hue == 120.0
        assert canvas.saturation == 0.5
        assert canvas.value == 0.8

        # Test keyboard navigation
        canvas.focus()
        await pilot.press("left")
        assert canvas.saturation < 0.5

        await pilot.press("up")
        assert canvas.value > 0.8

        # Test mouse click
        await pilot.click(ColorCanvas, offset=(10, 5))
        assert 0.0 <= canvas.saturation <= 1.0
        assert 0.0 <= canvas.value <= 1.0


@pytest.mark.asyncio
async def test_hue_bar_interactions():
    app = WidgetTestApp()
    async with app.run_test() as pilot:
        hue_bar = app.query_one("#hue_bar", HueBar)
        assert hue_bar.hue == 180.0

        hue_bar.focus()
        await pilot.press("down")
        assert hue_bar.hue > 180.0

        await pilot.click(HueBar, offset=(1, 2))
        assert 0.0 <= hue_bar.hue <= 360.0


@pytest.mark.asyncio
async def test_alpha_bar_interactions():
    app = WidgetTestApp()
    async with app.run_test() as pilot:
        alpha_bar = app.query_one("#alpha_bar", AlphaBar)
        assert alpha_bar.alpha == 0.75

        alpha_bar.focus()
        await pilot.press("left")
        assert alpha_bar.alpha < 0.75

        await pilot.click(AlphaBar, offset=(5, 0))
        assert 0.0 <= alpha_bar.alpha <= 1.0


@pytest.mark.asyncio
async def test_slider_focus_stability():
    """Ensure clicking/focusing HueBar and AlphaBar preserves content size without bugging or crushing."""
    app = WidgetTestApp()
    async with app.run_test() as pilot:
        canvas = app.query_one("#canvas", ColorCanvas)
        hue_bar = app.query_one("#hue_bar", HueBar)
        alpha_bar = app.query_one("#alpha_bar", AlphaBar)

        # 1. Focus HueBar (simulating mouse press on HueBar)
        hue_bar.focus()
        await pilot.pause()
        assert hue_bar.content_size.width >= 3
        assert hue_bar.content_size.height >= 10
        # Check that render produces valid non-empty lines
        rendered_hue = hue_bar.render()
        assert len(rendered_hue.plain.splitlines()) >= 10

        # 2. Focus AlphaBar (simulating mouse press on AlphaBar)
        alpha_bar.focus()
        await pilot.pause()
        assert alpha_bar.content_size.width >= 20
        assert alpha_bar.content_size.height >= 2
        # Check that render produces 2 distinct lines (gradient and pointer)
        rendered_alpha = alpha_bar.render()
        lines = rendered_alpha.plain.splitlines()
        assert len(lines) == 2
        assert "▲" in lines[1]

        # 3. Focus back on ColorCanvas
        canvas.focus()
        await pilot.pause()
        assert hue_bar.content_size.width >= 3
        assert alpha_bar.content_size.height >= 2
