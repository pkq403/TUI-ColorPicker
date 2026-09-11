#!/usr/bin/env bash
set -euo pipefail

# 🎨 color-picker Linux Installer & Uninstaller
# Supports: uv tool install, pipx install, and python3 venv standalone fallback.

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
DATA_DIR="${HOME}/.local/share/tui-color-picker"

print_banner() {
    echo -e "${BLUE}${BOLD}"
    echo "  🎨 TUI Color Picker Installer"
    echo -e "${NC}"
}

check_path() {
    local target_dir="$1"
    case ":${PATH}:" in
        *":${target_dir}:"*)
            # Directory is already in PATH
            return 0
            ;;
        *)
            echo -e "${YELLOW}⚠️  Note: ${target_dir} is not currently in your PATH.${NC}"
            echo -e "   To run 'color-picker' directly from anywhere, add this to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
            echo -e "   ${BOLD}export PATH=\"${target_dir}:\$PATH\"${NC}"
            echo -e "   Then reload your terminal or run: ${BOLD}source ~/.bashrc${NC}\n"
            return 1
            ;;
    esac
}

do_uninstall() {
    echo -e "${BLUE}Uninstalling color-picker / tui-color-picker...${NC}"
    local uninstalled=0

    # Check uv tool
    if command -v uv &>/dev/null; then
        if uv tool list 2>/dev/null | grep -q "tui-color-picker"; then
            echo -e "Removing uv tool: tui-color-picker"
            uv tool uninstall tui-color-picker || true
            uninstalled=1
        fi
    fi

    # Check pipx
    if command -v pipx &>/dev/null; then
        if pipx list 2>/dev/null | grep -q "tui-color-picker"; then
            echo -e "Removing pipx package: tui-color-picker"
            pipx uninstall tui-color-picker || true
            uninstalled=1
        fi
    fi

    # Remove standalone symlinks and data directory if present
    if [ -L "${BIN_DIR}/color-picker" ] || [ -f "${BIN_DIR}/color-picker" ]; then
        rm -f "${BIN_DIR}/color-picker"
        echo -e "Removed ${BIN_DIR}/color-picker"
        uninstalled=1
    fi
    if [ -L "${BIN_DIR}/tui-color-picker" ] || [ -f "${BIN_DIR}/tui-color-picker" ]; then
        rm -f "${BIN_DIR}/tui-color-picker"
        echo -e "Removed ${BIN_DIR}/tui-color-picker"
        uninstalled=1
    fi

    if [ -d "${DATA_DIR}" ]; then
        rm -rf "${DATA_DIR}"
        echo -e "Removed ${DATA_DIR}"
        uninstalled=1
    fi

    if [ "$uninstalled" -eq 1 ]; then
        echo -e "${GREEN}✓ color-picker has been uninstalled successfully.${NC}"
    else
        echo -e "${YELLOW}No existing color-picker installation found.${NC}"
    fi
}

do_install() {
    print_banner
    mkdir -p "${BIN_DIR}"

    # Method 1: uv (preferred)
    if command -v uv &>/dev/null; then
        echo -e "${BLUE}Found 'uv'. Installing with uv tool...${NC}"
        if uv tool list 2>/dev/null | grep -q "tui-color-picker"; then
            echo -e "Updating existing installation..."
            uv tool install --reinstall "${SCRIPT_DIR}"
        else
            uv tool install "${SCRIPT_DIR}"
        fi
        
        # Ensure shell path for uv tool bin
        local uv_bin_dir
        uv_bin_dir="$(uv tool dir --bin 2>/dev/null || echo "${BIN_DIR}")"
        check_path "${uv_bin_dir}"

    # Method 2: pipx
    elif command -v pipx &>/dev/null; then
        echo -e "${BLUE}Found 'pipx'. Installing with pipx...${NC}"
        if pipx list 2>/dev/null | grep -q "tui-color-picker"; then
            pipx install --force "${SCRIPT_DIR}"
        else
            pipx install "${SCRIPT_DIR}"
        fi
        check_path "${BIN_DIR}"

    # Method 3: python3 standalone virtualenv in ~/.local/share
    elif command -v python3 &>/dev/null; then
        echo -e "${BLUE}'uv' or 'pipx' not found. Installing into dedicated virtual environment...${NC}"
        
        # Verify Python version >= 3.13
        local py_ver
        py_ver="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
        local py_major py_minor
        py_major="$(echo "$py_ver" | cut -d. -f1)"
        py_minor="$(echo "$py_ver" | cut -d. -f2)"
        
        if [ "$py_major" -lt 3 ] || { [ "$py_major" -eq 3 ] && [ "$py_minor" -lt 13 ]; }; then
            echo -e "${RED}Error: Python 3.13 or newer is required (found Python ${py_ver}).${NC}"
            echo -e "Please install Python 3.13+ or install uv: https://docs.astral.sh/uv/"
            exit 1
        fi

        echo -e "Setting up isolated virtual environment in ${DATA_DIR}..."
        mkdir -p "${DATA_DIR}"
        python3 -m venv "${DATA_DIR}/venv"
        "${DATA_DIR}/venv/bin/pip" install --upgrade pip --quiet
        "${DATA_DIR}/venv/bin/pip" install "${SCRIPT_DIR}" --quiet

        ln -sf "${DATA_DIR}/venv/bin/color-picker" "${BIN_DIR}/color-picker"
        ln -sf "${DATA_DIR}/venv/bin/tui-color-picker" "${BIN_DIR}/tui-color-picker"

        check_path "${BIN_DIR}"

    else
        echo -e "${RED}Error: Neither 'uv', 'pipx', nor 'python3' was found.${NC}"
        echo -e "Please install 'uv' (https://docs.astral.sh/uv/) or Python 3.13+."
        exit 1
    fi

    echo -e "${GREEN}${BOLD}✓ Installation complete!${NC}"
    echo -e "You can now run:"
    echo -e "  ${BOLD}color-picker${NC}         # Launch the interactive color picker"
    echo -e "  ${BOLD}color-picker --help${NC}  # View CLI options and commands"
    echo -e "  ${BOLD}tui-color-picker${NC}    # Alias command also available\n"
}

case "${1:-install}" in
    install)
        do_install
        ;;
    --uninstall|uninstall)
        do_uninstall
        ;;
    -h|--help|help)
        echo "Usage: $0 [install | --uninstall | --help]"
        echo ""
        echo "Commands:"
        echo "  install      Install color-picker to your system (default)"
        echo "  --uninstall  Uninstall color-picker from your system"
        echo "  --help       Show this help message"
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo "Usage: $0 [install | --uninstall | --help]"
        exit 1
        ;;
esac
