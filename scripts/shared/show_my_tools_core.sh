#!/bin/bash
# ==============================================================================
# FILENAME: show_my_tools_core.sh
#
# AUTHOR: Gemini (Modified by foomanchu8008)
# DATE: 2025-11-04
#
# TYPE: Shared Shell Function
#
# PURPOSE:
#   Contains the core logic for displaying aliases, their functions/descriptions,
#   and providing interactive documentation browsing.
#
# SUMMARY:
#   This script defines a shell-agnostic function that parses alias definitions,
#   attempts to link them to relevant documentation, and offers an interactive
#   interface to browse documentation files. It is designed to be sourced by
#   shell-specific wrapper functions (e.g., in Zsh or Bash).
#
# ==============================================================================

# ==============================================================================
# FUNCTION: _show_my_tools_core
#
# DESCRIPTION:
#   This internal function collects aliases and their commands from shell-specific
#   alias directories. It then attempts to find relevant descriptions from
#   `~/.gemini/agents.md` and `~/.gemini/gemini.md`. Finally, it provides an
#   interactive menu (using fzf if available) to browse documentation files.
#
# USAGE:
#   _show_my_tools_core
#
# PARAMETERS:
#   None
#
# INPUTS:
#   - Alias files from ~/.zsh_aliases.d/ and ~/.bash_aliases.d/
#   - Documentation files from ~/.gemini/
#
# OUTPUTS:
#   - Formatted list of aliases and their descriptions.
#   - Interactive menu for documentation browsing.
#
# ==============================================================================
_show_my_tools_core() {
    echo "=== Your AI Coding Terminal Tools & Aliases ==="
    echo ""

    local alias_files=($HOME/.zsh_aliases.d/*.sh $HOME/.bash_aliases.d/*.sh)
    local all_aliases=()

    # Collect aliases and their commands
    for file in "${alias_files[@]}"; do
        if [[ -f "$file" ]]; then
            while IFS= read -r line; do
                if [[ "$line" =~ ^alias[[:space:]]+([^=]+)=\\'(.*)\\'$ ]]; then
                    local alias_name="${BASH_REMATCH[1]}"
                    local alias_cmd="${BASH_REMATCH[2]}"
                    all_aliases+=("$alias_name|$alias_cmd")
                fi
            done < "$file"
        fi
    done

    # Sort aliases alphabetically
    IFS=$'\n' all_aliases=($(sort <<<"${all_aliases[*]}"))
    unset IFS

    # Display aliases with descriptions
    for entry in "${all_aliases[@]}"; do
        local alias_name="${entry%|*}"
        local alias_cmd="${entry#*|}"
        local description="No description found."

        # Try to find description in agents.md or gemini.md
        if [[ -f "$HOME/.gemini/agents.md" ]]; then
            # Look for tool aliases (e.g., 'qwen', 'codex', 'forge')
            description=$(grep -m 1 -A 2 "^## ${alias_name^}" "$HOME/.gemini/agents.md" | tail -n 1 | sed -e 's/^[[:space:]]*//' -e 's/\* Usage: //')
            # Look for installation aliases (e.g., 'iqwen', 'icodex')
            if [[ -z "$description" && "$alias_name" =~ ^i(gcli|qwen|codex|aider|opencode|forge)$ ]]; then
                description="Installs the ${alias_name#i} CLI."
            fi
        fi
        if [[ -z "$description" && -f "$HOME/.gemini/gemini.md" ]]; then
            # Look for gemini alias
            if [[ "$alias_name" == "gcli" ]]; then
                description="Alias for the Google Gemini CLI."
            fi
        fi

        printf "  %-15s -> %-30s : %s\n" "$alias_name" "$alias_cmd" "$description"
    done

    echo "\n=== Browse Documentation ==="
    echo "Select a documentation file to view (use Ctrl+C to exit):"

    local doc_files=(
        "$HOME/.gemini/gemini.md"
        "$HOME/.gemini/agents.md"
        "$HOME/.zsh_functions.d"/*.zsh
        "$HOME/.bash_functions.d"/*.sh
        # Add other relevant documentation paths here
    )

    # Filter out non-existent files
    local existing_doc_files=()
    for file in "${doc_files[@]}"; do
        if [[ -f "$file" ]]; then
            existing_doc_files+=("$file")
        fi
    done

    if command -v fzf &> /dev/null; then
        local selected_file
        selected_file=$(printf "%s\n" "${existing_doc_files[@]}" | fzf --prompt="Select doc > ")
        if [[ -n "$selected_file" ]]; then
            if command -v less &> /dev/null; then
                less "$selected_file"
            else
                cat "$selected_file"
            fi
        fi
    else
        echo "fzf not found. Listing documentation files:"
        printf "%s\n" "${existing_doc_files[@]}"
        echo "To view a file, use 'cat <file_path>' or 'less <file_path>'."
    fi
}
