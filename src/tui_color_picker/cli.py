"""Typer CLI entrypoint for tui-color-picker."""

from __future__ import annotations

import sys
from typing import Optional
from enum import Enum
import typer

from tui_color_picker.core import parse_color_string
from tui_color_picker.tui.app import ColorPickerApp

app = typer.Typer(
    name="tui-color-picker",
    help="🎨 Interactive TrueColor TUI Color Picker with Hex, RGBA, and OKLCH support.",
    no_args_is_help=False,
    invoke_without_command=True,
)


class OutputFormat(str, Enum):
    hex = "hex"
    rgba = "rgba"
    oklch = "oklch"
    hsl = "hsl"


def _launch_tui(initial: str, format_str: str, auto_copy: bool) -> None:
    """Launch the interactive TUI application."""
    tui_app = ColorPickerApp(
        initial_color_str=initial,
        default_format=format_str,
        auto_copy=auto_copy,
    )
    result = tui_app.run()
    if result is not None:
        # Output color to stdout for shell pipeline integration
        sys.stdout.write(f"{result}\n")
        sys.stdout.flush()
    else:
        sys.exit(0)


@app.callback()
def main_callback(
    ctx: typer.Context,
    initial: str = typer.Option(
        "#6366f1",
        "--initial",
        "-i",
        help="Initial color (Hex, RGBA, OKLCH, or CSS name).",
    ),
    format: OutputFormat = typer.Option(
        OutputFormat.hex,
        "--format",
        "-f",
        help="Default output format on exit (hex, rgba, oklch, hsl).",
    ),
    copy: bool = typer.Option(
        True,
        "--copy/--no-copy",
        help="Whether to automatically copy the confirmed color to clipboard.",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show application version and exit.",
        is_eager=True,
    ),
) -> None:
    """Launch the TUI color picker directly or run a subcommand."""
    if version:
        typer.echo("tui-color-picker version 0.1.0")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        _launch_tui(initial, format.value, copy)


@app.command(name="pick")
def pick_cmd(
    color: str = typer.Argument(
        "#6366f1",
        help="Initial color (e.g. #ff0055, rgb(255, 0, 128), oklch(0.7 0.15 180)).",
    ),
    format: OutputFormat = typer.Option(
        OutputFormat.hex,
        "--format",
        "-f",
        help="Output format on exit.",
    ),
    copy: bool = typer.Option(
        True,
        "--copy/--no-copy",
        help="Whether to automatically copy confirmed color to clipboard.",
    ),
) -> None:
    """Launch the interactive TUI color picker with an optional initial color."""
    _launch_tui(color, format.value, copy)


@app.command(name="convert")
def convert_cmd(
    color: str = typer.Argument(..., help="Color string to convert (Hex, RGBA, OKLCH, etc.)."),
    to: OutputFormat = typer.Option(
        OutputFormat.hex,
        "--to",
        "-t",
        help="Target format to convert into (hex, rgba, oklch, hsl).",
    ),
) -> None:
    """Convert a color string to another format without launching the TUI."""
    try:
        c = parse_color_string(color)
    except ValueError as err:
        typer.secho(f"Error: {err}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    target = to.value
    if target == "hex":
        typer.echo(c.hex)
    elif target == "rgba":
        typer.echo(c.rgba_str)
    elif target == "oklch":
        typer.echo(c.oklch_str)
    elif target == "hsl":
        typer.echo(c.hsl_str)


if __name__ == "__main__":
    app()
