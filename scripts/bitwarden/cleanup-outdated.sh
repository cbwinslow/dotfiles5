#!/bin/bash
# Script to identify outdated dot_ directories in chezmoi that don't have corresponding ~/.config directories

echo "🔍 Checking for outdated dot_ directories in chezmoi..."

cd ~/.local/share/chezmoi

# Get list of dot_ directories
dot_dirs=$(ls -1d dot_* 2>/dev/null | sed 's/dot_//' | sort)

echo "Found $(echo "$dot_dirs" | wc -l) dot_ directories"

echo ""
echo "Directories to check/remove:"

for dir in $dot_dirs; do
    if [[ -d ~/.config/"$dir" ]]; then
        echo "✅ KEEP: $dir (config exists)"
    else
        echo "❌ REMOVE: $dir (no config found)"
    fi
done

echo ""
echo "To remove outdated directories, run:"
echo "cd ~/.local/share/chezmoi"
echo "git rm -r dot_<dirname>"
echo ""
echo "Or to remove all outdated ones at once:"
echo "for dir in \$(ls -1d dot_* | sed 's/dot_//' | while read d; do [ -d ~/.config/\"\$d\" ] || echo \"dot_\$d\"; done); do git rm -r \"\$dir\"; done"