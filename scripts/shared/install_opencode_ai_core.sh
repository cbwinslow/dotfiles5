#!/bin/bash
# ==============================================================================
# FILENAME: install_opencode_ai_core.sh
#
# AUTHOR: Gemini (Modified by foomanchu8008)
# DATE: 2025-11-04
#
# TYPE: Shared Shell Function
#
# PURPOSE:
#   Contains the core logic for installing or updating the Opencode-AI CLI.
#
# SUMMARY:
#   This script defines a shell-agnostic function that handles the global
#   installation of the Opencode-AI CLI using npm. It is designed to be
#   sourced by shell-specific wrapper functions (e.g., in Zsh or Bash).
#
# ==============================================================================

# ==============================================================================
# FUNCTION: _install_opencode_ai_core
#
# DESCRIPTION:
#   This internal function performs the actual installation of the Opencode-AI
#   CLI. It checks for npm and then executes the global npm install command.
#   It does NOT handle shell-specific sourcing or alias creation.
#
# USAGE:
#   _install_opencode_ai_core
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
_install_opencode_ai_core() {
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        echo "Error: npm is not installed. Please install Node.js and npm to continue."
        return 1
    fi

    echo "Installing Opencode-AI CLI..."
    # Install the Opencode-AI CLI globally using npm
    if npm install -g opencode-ai; then
        echo "Opencode-AI CLI installed successfully."
    else
        echo "Error: Failed to install Opencode-AI CLI."
        return 1
    fi
}
