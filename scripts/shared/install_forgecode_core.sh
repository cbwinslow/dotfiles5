#!/bin/bash
# ==============================================================================
# FILENAME: install_forgecode_core.sh
#
# AUTHOR: Gemini (Modified by foomanchu8008)
# DATE: 2025-11-04
#
# TYPE: Shared Shell Function
#
# PURPOSE:
#   Contains the core logic for installing or updating the ForgeCode CLI.
#
# SUMMARY:
#   This script defines a shell-agnostic function that handles the global
#   installation of the ForgeCode CLI using npm. It is designed to be
#   sourced by shell-specific wrapper functions (e.g., in Zsh or Bash).
#
# ==============================================================================

# ==============================================================================
# FUNCTION: _install_forgecode_core
#
# DESCRIPTION:
#   This internal function performs the actual installation of the ForgeCode
#   CLI. It checks for npm and then executes the global npm install command.
#   It does NOT handle shell-specific sourcing or alias creation.
#
# USAGE:
#   _install_forgecode_core
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
# NOTE:
#   ForgeCode requires authentication after installation. Refer to the official
#   ForgeCode documentation for details on how to authenticate (e.g., OAuth,
#   API keys for other providers).
#
# ==============================================================================
_install_forgecode_core() {
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        echo "Error: npm is not installed. Please install Node.js and npm to continue."
        return 1
    fi

    echo "Installing ForgeCode CLI..."
    # Install the ForgeCode CLI globally using npm
    if npm install -g forgecode@latest; then
        echo "ForgeCode CLI installed successfully."
    else
        echo "Error: Failed to install ForgeCode CLI."
        return 1
    fi
}
