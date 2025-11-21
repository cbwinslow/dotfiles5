#!/bin/bash
# Sync GitLab to GitHub Script
# Pushes changes from GitLab to GitHub repository

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== GitLab to GitHub Sync ===${NC}"
echo -e "${YELLOW}Syncing changes from GitLab to GitHub...${NC}"

# Repository URLs
GITHUB_REPO="git@github.com:cbwinslow/dotfiles5.git"
GITLAB_REPO="git@gitlab.com:cbwinslow/dotfiles5.git"

# Check if we're in YADM repository
if [ ! -d "$HOME/.local/share/yadm/repo.git" ]; then
    echo -e "${RED}✗ YADM repository not found${NC}"
    echo "Please ensure YADM is properly set up"
    exit 1
fi

cd "$HOME"

# Check current remote
if ! yadm remote | grep -q "origin"; then
    echo -e "${RED}✗ No origin remote found${NC}"
    exit 1
fi

# Add GitHub remote if not exists
if ! yadm remote | grep -q "github"; then
    echo -e "${YELLOW}Adding GitHub remote...${NC}"
    yadm remote add github "$GITHUB_REPO"
fi

# Fetch latest changes from both remotes
echo -e "${YELLOW}Fetching changes...${NC}"
yadm fetch origin
yadm fetch github

# Check if there are changes to push
if [ -n "$(yadm log origin/main..HEAD --oneline)" ]; then
    echo -e "${YELLOW}Pushing changes to GitHub...${NC}"
    yadm push github main
    echo -e "${GREEN}✓ Changes pushed to GitHub${NC}"
else
    echo -e "${BLUE}No changes to push${NC}"
fi

echo -e "${GREEN}✓ Sync completed!${NC}"
