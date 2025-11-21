#!/bin/bash
# ==============================================================================
# FILENAME: install_ollama_core.sh
#
# AUTHOR: Gemini (Modified by foomanchu8008)
# DATE: 2025-11-05
#
# TYPE: Shared Shell Function
#
# PURPOSE:
#   Installs Ollama, a lightweight, extensible framework for running LLMs locally.
#
# SUMMARY:
#   This script defines a shell-agnostic function to download and run the
#   official Ollama installation script. It includes checks for existing
#   installations and error handling. It is designed to be sourced by
#   shell-specific wrapper functions.
#
# ==============================================================================

# ==============================================================================
# FUNCTION: _install_ollama_core
#
# DESCRIPTION:
#   Performs the core logic for installing Ollama.
#   Checks for existing installation, downloads and executes the official
#   Ollama install script.
#
# USAGE:
#   _install_ollama_core
#
# PARAMETERS:
#   None
#
# INPUTS:
#   None
#
# OUTPUTS:
#   - Installation status messages.
#
# ==============================================================================
_install_ollama_core() {
    echo "Checking for existing Ollama installation..."
    if command -v ollama &> /dev/null; then
        echo "Ollama is already installed: $(ollama --version)"
        echo "If you wish to reinstall or upgrade, please manually remove the existing Ollama installation first."
        return 0
    fi

    echo "Installing Ollama..."

    # Download and run the official Ollama installation script
    # The official script handles systemd service setup and PATH configuration.
    if ! curl -fsSL https://ollama.com/install.sh | sh; then
        echo "Error: Failed to install Ollama." >&2
        return 1
    fi

    echo "Ollama installed successfully."
    echo "You may need to restart your terminal or source your shell configuration file for 'ollama' command to be available."
    echo "Run 'ollama run llama2' to download and run your first model."

    return 0
}
