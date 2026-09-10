"""tui-color-picker package."""

from .cli import app

def main() -> None:
    """CLI entrypoint."""
    app()

__all__ = ["app", "main"]
