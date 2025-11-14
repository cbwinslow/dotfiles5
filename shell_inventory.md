# Shell Inventory

This file provides an inventory of the shell configuration files and directories.

## Shared Functions

*   `~/shared_functions.d/`: Directory for storing functions that are shared between bash and zsh.

## Shared Secrets

*   `~/shell_secrets.d/`: Directory for storing shared secrets, organized by software company.

## Bash

*   `~/bash_secrets.d/`: Directory for storing bash secrets. Files in this directory are sourced by `.bashrc`. This directory contains symlinks to the shared secrets in `~/shell_secrets.d/`.
*   `~/bash_functions.d/`: Directory for storing bash functions. Files in this directory are sourced by `.bashrc`.
*   `~/bash_aliases.d/`: Directory for storing bash aliases. Files in this directory are sourced by `.bashrc`.

## Zsh

*   `~/zsh_secrets.d/`: Directory for storing zsh secrets. Files in this directory are sourced by `.zshrc`. This directory contains symlinks to the shared secrets in `~/shell_secrets.d/`.
*   `~/zsh_functions.d/`: Directory for storing zsh functions. Files in this directory are sourced by `.zshrc`.
*   `~/zsh_aliases.d/`: Directory for storing zsh aliases. Files in this directory are sourced by `.zshrc`.

## Fish

*   `~/fish_secrets.d/`: Directory for storing fish secrets. Files in this directory are sourced by `~/.config/fish/config.fish`.
*   `~/fish_functions.d/`: Directory for storing fish functions. Files in this directory are sourced by `~/.config/fish/config.fish`.
*   `~/fish_aliases.d/`: Directory for storing fish aliases. Files in this directory are sourced by `~/.config/fish/config.fish`.
