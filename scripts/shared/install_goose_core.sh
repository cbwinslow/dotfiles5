#!/bin/bash
# ==============================================================================
# FILENAME: install_goose_core.sh
#
# AUTHOR: Gemini (Modified by foomanchu8008)
# DATE: 2025-11-05
#
# TYPE: Shared Shell Function
#
# PURPOSE:
#   Installs Goose, a terminal coding agent.
#
# SUMMARY:
#   This script defines a shell-agnostic function to install Goose using its
#   official CLI install script. It includes checks for existing installations,
#   ensures necessary dependencies (like bzip2) are present, and provides
#   error handling. It is designed to be sourced by shell-specific wrapper functions.
#
# ==============================================================================

# ==============================================================================
# FUNCTION: _install_goose_core
#
# DESCRIPTION:
#   Performs the core logic for installing Goose.
#   Checks for existing installation, installs bzip2 if missing, and executes
#   the official Goose install script.
#
# USAGE:
#   _install_goose_core
#
# PARAMETERS:
#   None
#
# INPUTS:
#   None
#
# OUTPUTS:
#   - Installation status messages.
#   - Instructions for user to configure Goose.
#
# ==============================================================================
_install_goose_core() {
    echo "Checking for existing Goose installation..."
    if command -v goose &> /dev/null; then
        echo "Goose is already installed: $(goose --version 2>/dev/null || echo 'version unknown')"
        echo "If you wish to reinstall or upgrade, please manually remove the existing Goose installation first."
        return 0
    fi

    echo "Installing Goose..."

    # Check and install bzip2 if not present
    if ! command -v bzip2 &> /dev/null; then
        echo "bzip2 is required for Goose installation. Attempting to install bzip2..."
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y bzip2
        elif command -v yum &> /dev/null; then
            sudo yum install -y bzip2
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y bzip2
        else
            echo "Warning: bzip2 not found and cannot be automatically installed with apt, yum, or dnf."
            echo "Please install bzip2 manually using your distribution's package manager before proceeding."
            return 1
        fi
        if [[ $? -ne 0 ]]; then
            echo "Error: Failed to install bzip2." >&2
            return 1
        fi
    fi

    # Download and run the official Goose installation script
    echo "Downloading and running the official Goose install script..."
    if ! curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash; then
        echo "Error: Failed to install Goose." >&2
        return 1
    fi

    echo "Goose installed successfully."
    echo "You may need to restart your terminal or source your shell configuration file for 'goose' command to be available."
    echo "\n======================================================================"
    echo "IMPORTANT: Next, configure Goose with your LLM provider:"
    echo "           Run 'goose configure' in your terminal."
    echo "======================================================================"

    return 0
}
