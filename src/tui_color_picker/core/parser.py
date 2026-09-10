"""Robust color parser supporting Hex, RGBA, OKLCH, and named colors."""

from __future__ import annotations

import re
from typing import Optional
from coloraide import Color

from .models import ColorValue


def detect_color_format(text: str) -> str:
    """Detect the probable color format of the input string."""
    s = text.strip().lower()
    if s.startswith("#") or (re.fullmatch(r"[0-9a-fA-F]{3,8}", s) and len(s) in (3, 4, 6, 8)) or s.startswith("0x"):
        return "hex"
    if s.startswith("rgb"):
        return "rgba"
    if s.startswith("oklch") or s.startswith("okclh"):
        return "oklch"
    if s.startswith("hsl"):
        return "hsl"
    return "named"


def normalize_color_string(raw: str) -> str:
    """Normalize raw user input string for ColorAide parsing."""
    text = raw.strip()
    if not text:
        raise ValueError("Color string cannot be empty")

    # 0x prefix -> #
    if text.startswith("0x") or text.startswith("0X"):
        text = "#" + text[2:]

    # Bare hex without #
    if re.fullmatch(r"[0-9a-fA-F]{3,8}", text) and len(text) in (3, 4, 6, 8):
        text = "#" + text

    # Typo: okclh -> oklch
    if text.lower().startswith("okclh("):
        text = "oklch(" + text[6:]

    # Fix comma-separated OKLCH syntax: oklch(L, C, H[, A]) -> oklch(L C H [/ A])
    m_oklch = re.match(r"^oklch\s*\((.*)\)$", text, re.IGNORECASE)
    if m_oklch:
        inner = m_oklch.group(1).strip()
        if "," in inner:
            parts = [p.strip() for p in inner.split(",") if p.strip()]
            if len(parts) == 3:
                text = f"oklch({parts[0]} {parts[1]} {parts[2]})"
            elif len(parts) == 4:
                text = f"oklch({parts[0]} {parts[1]} {parts[2]} / {parts[3]})"

    return text


def parse_color_string(raw: str, fallback_h: Optional[float] = None) -> ColorValue:
    """Parse a color string into a ColorValue.

    Supports:
      - Hex (#fff, #ffffff, #ffffff80, or bare hex)
      - RGBA (rgb(255, 0, 128), rgba(255, 0, 128, 0.5), rgb(255 0 128 / 0.5))
      - OKLCH / OKCLH (oklch(0.7 0.15 180), oklch(70% 0.15 180 / 0.5), comma syntax)
      - HSL / HSLA (hsl(200, 100%, 50%), hsla(200, 100%, 50%, 0.5))
      - CSS Named colors (coral, tomato, rebeccapurple, etc.)

    Raises:
        ValueError: if the color string cannot be parsed.
    """
    normalized = normalize_color_string(raw)
    try:
        color = Color(normalized)
    except Exception as exc:
        raise ValueError(f"Invalid color format '{raw}': {exc}") from exc

    return ColorValue.from_coloraide(color)
