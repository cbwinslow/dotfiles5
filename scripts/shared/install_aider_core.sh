#!/bin/bash
# ==============================================================================
# FILENAME: install_aider_core.sh
#
# AUTHOR: Gemini (Modified by foomanchu8008)
# DATE: 2025-11-04
#
# TYPE: Shared Shell Function
#
# PURPOSE:
#   Contains the core logic for installing or updating the Aider CLI.
#
# SUMMARY:
#   This script defines a shell-agnostic function that handles the global
#   installation of the Aider CLI using pip. It is designed to be
#   sourced by shell-specific wrapper functions (e.g., in Zsh or Bash).
#
# ==============================================================================

# ==============================================================================
# FUNCTION: _install_aider_core
#
# DESCRIPTION:
#   This internal function performs the actual installation of the Aider
#   CLI. It checks for python3 and pip and then executes the pip install
#   command. It does NOT handle shell-specific sourcing or alias creation.
#
# USAGE:
#   _install_aider_core
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
#   Requires Python 3.8-3.13. Also requires the OPENAI_API_KEY environment
#   variable to be set for Aider to function correctly.
#   Example: `export OPENAI_API_KEY="your-api-key-here"`
#
# ==============================================================================
_install_aider_core() {
    # Check if python3 is installed
    if ! command -v python3 &> /dev/null; then
        echo "Error: python3 is not installed. Please install Python 3 to continue."
        return 1
    fi

    # Check if pip is installed for python3
    if ! python3 -m pip --version &> /dev/null; then
        echo "Error: pip is not installed for python3. Please install pip for Python 3 to continue."
        return 1
    fi

    echo "Installing Aider CLI..."
    # Install Aider using pip
    if python3 -m pip install aider-install aider-install; then
        echo "Aider CLI installed successfully."
    else
        echo "Error: Failed to install Aider CLI."
        return 1
    fi
}
