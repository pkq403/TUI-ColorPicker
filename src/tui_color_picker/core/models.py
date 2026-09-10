"""Unified color model representing a color across RGB, HSV, OKLCH, and Hex spaces."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional
from coloraide import Color


@dataclass(frozen=True)
class ColorValue:
    """Immutable representation of a color across sRGB, HSV, OKLCH, and Hex spaces.

    Attributes:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        alpha: Alpha channel (0.0 to 1.0).
        h: HSV Hue (0.0 to 360.0).
        s: HSV Saturation (0.0 to 1.0).
        v: HSV Value/Brightness (0.0 to 1.0).
        oklch_l: OKLCH Lightness (0.0 to 1.0).
        oklch_c: OKLCH Chroma (0.0 to ~0.4).
        oklch_h: OKLCH Hue (0.0 to 360.0).
    """

    r: int
    g: int
    b: int
    alpha: float
    h: float
    s: float
    v: float
    oklch_l: float
    oklch_c: float
    oklch_h: float

    @classmethod
    def from_hsv(cls, h: float, s: float, v: float, alpha: float = 1.0) -> ColorValue:
        """Create ColorValue from HSV values, maintaining the user-selected hue even if achromatic."""
        h_clamped = max(0.0, min(360.0, float(h))) % 360.0 if h != 360.0 else 360.0
        s_clamped = max(0.0, min(1.0, float(s)))
        v_clamped = max(0.0, min(1.0, float(v)))
        a_clamped = max(0.0, min(1.0, float(alpha)))

        color = Color("hsv", [h_clamped, s_clamped, v_clamped])
        color["alpha"] = a_clamped

        # Convert to sRGB and fit
        srgb = color.fit("srgb").convert("srgb")
        r = max(0, min(255, int(round(srgb[0] * 255))))
        g = max(0, min(255, int(round(srgb[1] * 255))))
        b = max(0, min(255, int(round(srgb[2] * 255))))

        # Convert to OKLCH
        oklch = color.convert("oklch")
        ok_l = max(0.0, min(1.0, float(oklch[0])))
        ok_c = max(0.0, float(oklch[1]))
        ok_h_val = float(oklch[2])
        ok_h = h_clamped if math.isnan(ok_h_val) else (ok_h_val % 360.0)

        return cls(
            r=r,
            g=g,
            b=b,
            alpha=a_clamped,
            h=h_clamped,
            s=s_clamped,
            v=v_clamped,
            oklch_l=ok_l,
            oklch_c=ok_c,
            oklch_h=ok_h,
        )

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int, alpha: float = 1.0, fallback_h: Optional[float] = None) -> ColorValue:
        """Create ColorValue from sRGB values (0-255)."""
        r_clamped = max(0, min(255, int(round(r))))
        g_clamped = max(0, min(255, int(round(g))))
        b_clamped = max(0, min(255, int(round(b))))
        a_clamped = max(0.0, min(1.0, float(alpha)))

        color = Color("srgb", [r_clamped / 255.0, g_clamped / 255.0, b_clamped / 255.0])
        color["alpha"] = a_clamped

        hsv = color.convert("hsv")
        h_val = float(hsv[0])
        if math.isnan(h_val):
            h = fallback_h if fallback_h is not None else 0.0
        else:
            h = h_val % 360.0 if h_val != 360.0 else 360.0

        s = 0.0 if math.isnan(hsv[1]) else max(0.0, min(1.0, float(hsv[1])))
        v = 0.0 if math.isnan(hsv[2]) else max(0.0, min(1.0, float(hsv[2])))

        oklch = color.convert("oklch")
        ok_l = max(0.0, min(1.0, float(oklch[0])))
        ok_c = max(0.0, float(oklch[1]))
        ok_h_val = float(oklch[2])
        ok_h = h if math.isnan(ok_h_val) else (ok_h_val % 360.0)

        return cls(
            r=r_clamped,
            g=g_clamped,
            b=b_clamped,
            alpha=a_clamped,
            h=h,
            s=s,
            v=v,
            oklch_l=ok_l,
            oklch_c=ok_c,
            oklch_h=ok_h,
        )

    @classmethod
    def from_oklch(cls, l: float, c: float, h: float, alpha: float = 1.0) -> ColorValue:
        """Create ColorValue from OKLCH coordinates (L: 0-1, C: 0-0.4+, H: 0-360)."""
        l_clamped = max(0.0, min(1.0, float(l)))
        c_clamped = max(0.0, float(c))
        h_norm = float(h) % 360.0
        a_clamped = max(0.0, min(1.0, float(alpha)))

        color = Color("oklch", [l_clamped, c_clamped, h_norm])
        color["alpha"] = a_clamped

        # Gamut fit to sRGB
        fit_color = color.clone().fit("srgb")
        srgb = fit_color.convert("srgb")
        r = max(0, min(255, int(round(srgb[0] * 255))))
        g = max(0, min(255, int(round(srgb[1] * 255))))
        b = max(0, min(255, int(round(srgb[2] * 255))))

        hsv = fit_color.convert("hsv")
        h_hsv_val = float(hsv[0])
        h_hsv = h_norm if math.isnan(h_hsv_val) else (h_hsv_val % 360.0)
        s_hsv = 0.0 if math.isnan(hsv[1]) else max(0.0, min(1.0, float(hsv[1])))
        v_hsv = 0.0 if math.isnan(hsv[2]) else max(0.0, min(1.0, float(hsv[2])))

        return cls(
            r=r,
            g=g,
            b=b,
            alpha=a_clamped,
            h=h_hsv,
            s=s_hsv,
            v=v_hsv,
            oklch_l=l_clamped,
            oklch_c=c_clamped,
            oklch_h=h_norm,
        )

    @classmethod
    def from_coloraide(cls, color: Color) -> ColorValue:
        """Create ColorValue from an arbitrary ColorAide Color object."""
        fit_color = color.clone().fit("srgb")
        srgb = fit_color.convert("srgb")
        r = max(0, min(255, int(round(srgb[0] * 255))))
        g = max(0, min(255, int(round(srgb[1] * 255))))
        b = max(0, min(255, int(round(srgb[2] * 255))))
        alpha = float(color["alpha"])

        hsv = fit_color.convert("hsv")
        h_val = float(hsv[0])
        h = 0.0 if math.isnan(h_val) else (h_val % 360.0)
        s = 0.0 if math.isnan(hsv[1]) else max(0.0, min(1.0, float(hsv[1])))
        v = 0.0 if math.isnan(hsv[2]) else max(0.0, min(1.0, float(hsv[2])))

        oklch = color.convert("oklch")
        ok_l = max(0.0, min(1.0, float(oklch[0])))
        ok_c = max(0.0, float(oklch[1]))
        ok_h_val = float(oklch[2])
        ok_h = h if math.isnan(ok_h_val) else (ok_h_val % 360.0)

        return cls(
            r=r,
            g=g,
            b=b,
            alpha=alpha,
            h=h,
            s=s,
            v=v,
            oklch_l=ok_l,
            oklch_c=ok_c,
            oklch_h=ok_h,
        )

    # String formatters
    @property
    def hex(self) -> str:
        """Return hex representation (#rrggbb or #rrggbbaa if alpha < 1.0)."""
        if self.alpha < 0.999:
            a_byte = int(round(self.alpha * 255))
            return f"#{self.r:02x}{self.g:02x}{self.b:02x}{a_byte:02x}"
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    @property
    def hex_no_alpha(self) -> str:
        """Return 6-digit hex representation (#rrggbb)."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    @property
    def rgba_str(self) -> str:
        """Return formatted rgba(...) or rgb(...) string."""
        if self.alpha < 0.999:
            a_formatted = f"{self.alpha:.2f}".rstrip("0").rstrip(".")
            return f"rgba({self.r}, {self.g}, {self.b}, {a_formatted})"
        return f"rgb({self.r}, {self.g}, {self.b})"

    @property
    def oklch_str(self) -> str:
        """Return formatted oklch(...) string."""
        l_str = f"{self.oklch_l:.3f}".rstrip("0").rstrip(".")
        c_str = f"{self.oklch_c:.3f}".rstrip("0").rstrip(".")
        h_str = f"{self.oklch_h:.1f}".rstrip("0").rstrip(".")
        if self.alpha < 0.999:
            a_str = f"{self.alpha:.2f}".rstrip("0").rstrip(".")
            return f"oklch({l_str} {c_str} {h_str} / {a_str})"
        return f"oklch({l_str} {c_str} {h_str})"

    @property
    def hsl_str(self) -> str:
        """Return formatted hsl(...) string."""
        # Convert to HSL
        c = Color("srgb", [self.r / 255.0, self.g / 255.0, self.b / 255.0])
        hsl = c.convert("hsl")
        h = 0.0 if math.isnan(hsl[0]) else (hsl[0] % 360.0)
        s = 0.0 if math.isnan(hsl[1]) else hsl[1]
        l = 0.0 if math.isnan(hsl[2]) else hsl[2]
        if self.alpha < 0.999:
            a_str = f"{self.alpha:.2f}".rstrip("0").rstrip(".")
            return f"hsla({int(round(h))}, {int(round(s))}%, {int(round(l))}%, {a_str})"
        return f"hsl({int(round(h))}, {int(round(s))}%, {int(round(l))}%)"

    def with_alpha(self, alpha: float) -> ColorValue:
        """Return a copy with updated alpha."""
        return ColorValue.from_hsv(self.h, self.s, self.v, alpha=alpha)

    def with_hsv(
        self,
        h: Optional[float] = None,
        s: Optional[float] = None,
        v: Optional[float] = None,
    ) -> ColorValue:
        """Return a copy with updated HSV values."""
        new_h = self.h if h is None else h
        new_s = self.s if s is None else s
        new_v = self.v if v is None else v
        return ColorValue.from_hsv(new_h, new_s, new_v, alpha=self.alpha)
