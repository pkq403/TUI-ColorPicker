import pytest
from tui_color_picker.core import (
    ColorValue,
    parse_color_string,
    detect_color_format,
    calculate_contrast,
)


def test_color_value_from_hsv():
    # Pure Red (H=0, S=1, V=1)
    red = ColorValue.from_hsv(0, 1.0, 1.0)
    assert red.r == 255
    assert red.g == 0
    assert red.b == 0
    assert red.alpha == 1.0
    assert red.hex == "#ff0000"
    assert red.rgba_str == "rgb(255, 0, 0)"

    # With alpha
    red_half = red.with_alpha(0.5)
    assert red_half.alpha == 0.5
    assert red_half.hex.startswith("#ff0000")
    assert len(red_half.hex) == 9
    assert "0.5" in red_half.rgba_str


def test_color_value_from_rgb():
    blue = ColorValue.from_rgb(0, 0, 255)
    assert blue.hex == "#0000ff"
    assert round(blue.h) == 240
    assert blue.s == 1.0
    assert blue.v == 1.0


def test_color_value_from_oklch():
    # Test OKLCH creation and gamut fitting
    color = ColorValue.from_oklch(0.65, 0.15, 240)
    assert 0 <= color.r <= 255
    assert 0 <= color.g <= 255
    assert 0 <= color.b <= 255
    assert 0 <= color.h <= 360
    assert color.hex.startswith("#")


def test_parse_hex_variants():
    # 3-digit with and without #
    c1 = parse_color_string("#fff")
    c2 = parse_color_string("fff")
    assert c1.hex == "#ffffff"
    assert c2.hex == "#ffffff"

    # 6-digit with and without #
    c3 = parse_color_string("#ff5500")
    c4 = parse_color_string("ff5500")
    assert c3.hex == "#ff5500"
    assert c4.hex == "#ff5500"

    # 8-digit hex with alpha
    c5 = parse_color_string("#ff550080")
    assert c5.alpha == pytest.approx(0.5, abs=0.01)

    # 0x prefix
    c6 = parse_color_string("0x00ff00")
    assert c6.hex == "#00ff00"


def test_parse_rgba():
    c1 = parse_color_string("rgb(255, 128, 0)")
    assert c1.r == 255
    assert c1.g == 128
    assert c1.b == 0
    assert c1.alpha == 1.0

    c2 = parse_color_string("rgba(255, 128, 0, 0.5)")
    assert c2.r == 255
    assert c2.g == 128
    assert c2.b == 0
    assert c2.alpha == pytest.approx(0.5, abs=0.01)

    # Space separated CSS Color 4
    c3 = parse_color_string("rgb(0 255 128 / 0.8)")
    assert c3.r == 0
    assert c3.g == 255
    assert c3.b == 128
    assert c3.alpha == pytest.approx(0.8, abs=0.01)


def test_parse_oklch_and_typo():
    # Standard CSS oklch
    c1 = parse_color_string("oklch(0.7 0.15 180)")
    assert c1.oklch_l == pytest.approx(0.7, abs=0.01)
    assert c1.oklch_c == pytest.approx(0.15, abs=0.01)
    assert c1.oklch_h == pytest.approx(180, abs=0.5)

    # User typo: okclh
    c2 = parse_color_string("okclh(0.7 0.15 180)")
    assert c2.oklch_l == pytest.approx(0.7, abs=0.01)

    # Comma-separated oklch
    c3 = parse_color_string("oklch(0.65, 0.12, 240, 0.75)")
    assert c3.alpha == pytest.approx(0.75, abs=0.01)


def test_parse_named_and_hsl():
    c_red = parse_color_string("red")
    assert c_red.hex == "#ff0000"

    c_hsl = parse_color_string("hsl(120, 100%, 50%)")
    assert c_hsl.hex == "#00ff00"


def test_parse_invalid():
    with pytest.raises(ValueError):
        parse_color_string("not-a-color-xyz")

    with pytest.raises(ValueError):
        parse_color_string("")


def test_detect_color_format():
    assert detect_color_format("#ff0000") == "hex"
    assert detect_color_format("aabbcc") == "hex"
    assert detect_color_format("0x123456") == "hex"
    assert detect_color_format("rgb(1, 2, 3)") == "rgba"
    assert detect_color_format("rgba(1, 2, 3, 0.4)") == "rgba"
    assert detect_color_format("oklch(0.5 0.1 180)") == "oklch"
    assert detect_color_format("okclh(0.5 0.1 180)") == "oklch"
    assert detect_color_format("hsl(180, 50%, 50%)") == "hsl"
    assert detect_color_format("papayawhip") == "named"


def test_calculate_contrast():
    white_color = ColorValue.from_rgb(255, 255, 255)
    report_w = calculate_contrast(white_color)
    assert report_w.contrast_white == 1.0
    assert report_w.contrast_black == 21.0
    assert report_w.best_text_color == "#000000"
    assert report_w.aaa_normal_black is True

    black_color = ColorValue.from_rgb(0, 0, 0)
    report_b = calculate_contrast(black_color)
    assert report_b.contrast_black == 1.0
    assert report_b.contrast_white == 21.0
    assert report_b.best_text_color == "#ffffff"
    assert report_b.aaa_normal_white is True
