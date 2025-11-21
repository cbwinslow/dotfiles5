#!/bin/bash
# ==============================================================================
# FILENAME: install_qwen_code_core.sh
#
# AUTHOR: Gemini (Modified by foomanchu8008)
# DATE: 2025-11-04
#
# TYPE: Shared Shell Function
#
# PURPOSE:
#   Contains the core logic for installing or updating the Qwen Code CLI.
#
# SUMMARY:
#   This script defines a shell-agnostic function that handles the global
#   installation of the Qwen Code CLI using npm. It is designed to be
#   sourced by shell-specific wrapper functions (e.g., in Zsh or Bash).
#
# ==============================================================================

# ==============================================================================
# FUNCTION: _install_qwen_code_core
#
# DESCRIPTION:
#   This internal function performs the actual installation of the Qwen Code
#   CLI. It checks for npm and then executes the global npm install command.
#   It does NOT handle shell-specific sourcing or alias creation.
#
# USAGE:
#   _install_qwen_code_core
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
_install_qwen_code_core() {
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        echo "Error: npm is not installed. Please install Node.js and npm to continue."
        return 1
    fi

    echo "Installing Qwen Code CLI..."
    # Install the Qwen Code CLI globally using npm
    if npm install -g qwen-code; then
        echo "Qwen Code CLI installed successfully."
    else
        echo "Error: Failed to install Qwen Code CLI."
        return 1
    fi
}
