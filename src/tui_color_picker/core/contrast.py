"""Accessibility and WCAG contrast calculation."""

from __future__ import annotations

from dataclasses import dataclass
from coloraide import Color

from .models import ColorValue

WHITE = Color("#ffffff")
BLACK = Color("#000000")


@dataclass(frozen=True)
class ContrastReport:
    """WCAG 2.1 contrast analysis for a color."""

    contrast_white: float
    contrast_black: float
    aa_normal_white: bool
    aa_large_white: bool
    aaa_normal_white: bool
    aa_normal_black: bool
    aa_large_black: bool
    aaa_normal_black: bool
    best_text_color: str  # '#000000' or '#ffffff'


def calculate_contrast(color_val: ColorValue) -> ContrastReport:
    """Calculate WCAG contrast ratios against black and white."""
    c = Color("srgb", [color_val.r / 255.0, color_val.g / 255.0, color_val.b / 255.0])
    ratio_white = float(c.contrast(WHITE))
    ratio_black = float(c.contrast(BLACK))

    best_text = "#000000" if ratio_black >= ratio_white else "#ffffff"

    return ContrastReport(
        contrast_white=round(ratio_white, 2),
        contrast_black=round(ratio_black, 2),
        aa_normal_white=ratio_white >= 4.5,
        aa_large_white=ratio_white >= 3.0,
        aaa_normal_white=ratio_white >= 7.0,
        aa_normal_black=ratio_black >= 4.5,
        aa_large_black=ratio_black >= 3.0,
        aaa_normal_black=ratio_black >= 7.0,
        best_text_color=best_text,
    )
