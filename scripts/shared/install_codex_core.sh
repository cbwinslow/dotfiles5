#!/bin/bash
# ==============================================================================
# FILENAME: install_codex_core.sh
#
# AUTHOR: Gemini (Modified by foomanchu8008)
# DATE: 2025-11-04
#
# TYPE: Shared Shell Function
#
# PURPOSE:
#   Contains the core logic for installing or updating the OpenAI Codex CLI.
#
# SUMMARY:
#   This script defines a shell-agnostic function that handles the global
#   installation of the OpenAI Codex CLI using npm. It is designed to be
#   sourced by shell-specific wrapper functions (e.g., in Zsh or Bash).
#
# ==============================================================================

# ==============================================================================
# FUNCTION: _install_codex_core
#
# DESCRIPTION:
#   This internal function performs the actual installation of the OpenAI
#   Codex CLI. It checks for npm and then executes the global npm install
#   command. It does NOT handle shell-specific sourcing or alias creation.
#
# USAGE:
#   _install_codex_core
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
#   Requires the OPENAI_API_KEY environment variable to be set.
#   Example: `export OPENAI_API_KEY="your-api-key-here"`
#
# ==============================================================================
_install_codex_core() {
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        echo "Error: npm is not installed. Please install Node.js and npm to continue."
        return 1
    fi

    echo "Installing OpenAI Codex CLI..."
    # Install the Codex CLI globally using npm
    if npm install -g @openai/codex; then
        echo "OpenAI Codex CLI installed successfully."
    else
        echo "Error: Failed to install OpenAI Codex CLI."
        return 1
    fi
}
