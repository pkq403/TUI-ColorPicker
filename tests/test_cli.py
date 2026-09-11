import pytest
from typer.testing import CliRunner
from tui_color_picker.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "tui-color-picker" in result.output
    assert "pick" in result.output
    assert "convert" in result.output


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_convert_to_hex():
    result = runner.invoke(app, ["convert", "rgb(255, 0, 0)", "--to", "hex"])
    assert result.exit_code == 0
    assert result.output.strip() == "#ff0000"


def test_cli_convert_to_oklch():
    result = runner.invoke(app, ["convert", "#ff0000", "--to", "oklch"])
    assert result.exit_code == 0
    assert result.output.strip().startswith("oklch(")


def test_cli_convert_to_rgba():
    result = runner.invoke(app, ["convert", "oklch(0.7 0.15 180)", "--to", "rgba"])
    assert result.exit_code == 0
    assert "rgb" in result.output


def test_cli_convert_invalid():
    result = runner.invoke(app, ["convert", "not-a-color"])
    assert result.exit_code != 0
    assert "Error:" in result.output


def test_entrypoint_main(monkeypatch):
    from tui_color_picker import main

    monkeypatch.setattr("sys.argv", ["color-picker", "--version"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0

