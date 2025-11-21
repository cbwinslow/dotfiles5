# YADM USAGE RULES

## GOLDEN RULE: ALWAYS USE COPIES, NEVER ORIGINALS

When working with yadm, ALWAYS make copies of files/folders before adding them to yadm:

### CORRECT WAY:
```bash
# Copy files to dotfiles directory first
cp -r /path/to/original /home/cbwinslow/dotfiles/
yadm add dotfiles/copied_file
```

### WRONG WAY:
```bash
# NEVER add original files directly
yadm add /path/to/original  # ❌ THIS BREAKS THINGS
```

### SAFE WORKFLOW:
1. Copy files/folders to dotfiles directory
2. Add the copies to yadm
3. Commit and push
4. Original files remain untouched

### EXAMPLE:
```bash
# Copy zsh directories
cp -r ~/zsh_aliases.d ~/dotfiles/
cp -r ~/zsh_functions.d ~/dotfiles/

# Add copies to yadm
yadm add dotfiles/zsh_aliases.d dotfiles/zsh_functions.d
yadm commit -m "Add zsh directories"
```

## REMEMBER: YADM MANAGES COPIES, NOT ORIGINALS!