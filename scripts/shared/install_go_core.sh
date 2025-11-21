#!/bin/bash
# ==============================================================================
# FILENAME: install_go_core.sh
#
# AUTHOR: Gemini (Modified by foomanchu8008)
# DATE: 2025-11-05
#
# TYPE: Shared Shell Function
#
# PURPOSE:
#   Installs the latest stable version of Go (Go-lang) on a Linux x64 system.
#
# SUMMARY:
#   This script defines a shell-agnostic function to download, extract, and
#   configure the Go programming language. It includes checks for existing
#   installations, error handling, and instructions for setting up environment
#   variables. It is designed to be sourced by shell-specific wrapper functions.
#
# ==============================================================================

# ==============================================================================
# FUNCTION: _install_go_core
#
# DESCRIPTION:
#   Performs the core logic for installing Go-lang.
#   Checks for existing installation, downloads the tarball, extracts it to
#   /usr/local, and provides instructions for environment variable setup.
#
# USAGE:
#   _install_go_core
#
# PARAMETERS:
#   None
#
# INPUTS:
#   None
#
# OUTPUTS:
#   - Installation status messages.
#   - Instructions for user to update their shell configuration.
#
# ==============================================================================
_install_go_core() {
    local GO_VERSION="1.25.3"
    local GO_TARBALL="go${GO_VERSION}.linux-amd64.tar.gz"
    local GO_DOWNLOAD_URL="https://golang.org/dl/${GO_TARBALL}"
    local INSTALL_DIR="/usr/local"
    local GO_INSTALL_PATH="${INSTALL_DIR}/go"

    echo "Checking for existing Go installation..."
    if command -v go &> /dev/null; then
        echo "Go is already installed: $(go version)"
        echo "If you wish to reinstall or upgrade, please manually remove the existing Go installation first (e.g., sudo rm -rf ${GO_INSTALL_PATH})."
        return 0
    fi

    echo "Installing Go ${GO_VERSION}..."

    # Create a temporary directory for download
    local TEMP_DIR=$(mktemp -d)
    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to create temporary directory." >&2
        return 1
    fi
    echo "Using temporary directory: ${TEMP_DIR}"

    # Download Go tarball
    echo "Downloading Go from ${GO_DOWNLOAD_URL}..."
    if ! curl -sSL "${GO_DOWNLOAD_URL}" -o "${TEMP_DIR}/${GO_TARBALL}"; then
        echo "Error: Failed to download Go tarball." >&2
        rm -rf "${TEMP_DIR}"
        return 1
    fi

    # Verify checksum (placeholder - actual checksum not available from search)
    # echo "Verifying checksum..."
    # local EXPECTED_CHECKSUM="<INSERT_CHECKSUM_HERE>"
    # local ACTUAL_CHECKSUM=$(sha256sum "${TEMP_DIR}/${GO_TARBALL}" | awk 
'{print $1}')
    # if [[ "${ACTUAL_CHECKSUM}" != "${EXPECTED_CHECKSUM}" ]]; then
    #     echo "Error: Checksum mismatch. Downloaded file may be corrupted." >&2
    #     rm -rf "${TEMP_DIR}"
    #     return 1
    # fi
    # echo "Checksum verified."

    # Extract Go tarball
    echo "Extracting Go to ${INSTALL_DIR}..."
    # Ensure /usr/local exists and is writable, or use sudo
    if [[ ! -d "${INSTALL_DIR}" ]]; then
        echo "Warning: ${INSTALL_DIR} does not exist. Attempting to create with sudo."
        if ! sudo mkdir -p "${INSTALL_DIR}"; then
            echo "Error: Failed to create ${INSTALL_DIR}. Please ensure you have permissions." >&2
            rm -rf "${TEMP_DIR}"
            return 1
        fi
    fi

    if ! sudo tar -C "${INSTALL_DIR}" -xzf "${TEMP_DIR}/${GO_TARBALL}"; then
        echo "Error: Failed to extract Go tarball." >&2
        rm -rf "${TEMP_DIR}"
        return 1
    fi

    # Clean up temporary directory
    echo "Cleaning up temporary files..."
    rm -rf "${TEMP_DIR}"

    echo "Go ${GO_VERSION} installed successfully to ${GO_INSTALL_PATH}."
    echo ""
    echo "======================================================================"
    echo "IMPORTANT: Please add the following to your shell configuration file"
    echo "           (e.g., ~/.zshrc or ~/.bashrc) to complete the setup:"
    echo ""
    echo "export PATH=\"${GO_INSTALL_PATH}/bin:\$PATH\""
    echo "export GOPATH=\"
$HOME/go\"" # Or your preferred Go workspace directory
    echo "export PATH=\"
$GOPATH/bin:\$PATH\""
    echo ""
    echo "After adding these lines, run 'source ~/.zshrc' or 'source ~/.bashrc'."
    echo "======================================================================"

    # Attempt to set for current session (user still needs to add to rc file)
    export PATH="${GO_INSTALL_PATH}/bin:${PATH}"
    export GOPATH="$HOME/go"
    export PATH="${GOPATH}/bin:${PATH}"

    if command -v go &> /dev/null; then
        echo "Go version in current session: $(go version)"
    else
        echo "Go command not found in current session. Please reload your shell."
    fi

    return 0
}
