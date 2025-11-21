#!/bin/bash
# ==============================================================================
# FILENAME: install_gemini_cli_core.sh
#
# AUTHOR: Gemini (Modified by foomanchu8008)
# DATE: 2025-11-04
#
# TYPE: Shared Shell Function
#
# PURPOSE:
#   Contains the core logic for installing or updating the Google Gemini CLI.
#
# SUMMARY:
#   This script defines a shell-agnostic function that handles the global
#   installation of the Google Gemini CLI using npm. It is designed to be
#   sourced by shell-specific wrapper functions (e.g., in Zsh or Bash).
#
# ==============================================================================

# ==============================================================================
# FUNCTION: _install_gemini_cli_core
#
# DESCRIPTION:
#   This internal function performs the actual installation of the Google
#   Gemini CLI. It checks for npm and then executes the global npm install
#   command. It does NOT handle shell-specific sourcing or alias creation.
#
# USAGE:
#   _install_gemini_cli_core
#
# PARAMETERS:
#   None
#
# INPUTS:
#   None
#
# OUTPUTS:
#   - Messages indicating installation progress and success/failure.
#
# ==============================================================================
_install_gemini_cli_core() {
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        echo "Error: npm is not installed. Please install Node.js and npm to continue."
        return 1
    fi

    echo "Installing Google Gemini CLI..."
    # Install the Gemini CLI globally using npm
    if npm install -g @google/gemini-cli; then
        echo "Google Gemini CLI installed successfully."
    else
        echo "Error: Failed to install Google Gemini CLI."
        return 1
    fi
}
