#!/bin/bash
# Sync GitHub to GitLab Script
# Pushes changes from GitHub to GitLab repository

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== GitHub to GitLab Sync ===${NC}"
echo -e "${YELLOW}Syncing changes from GitHub to GitLab...${NC}"

# Repository URLs
GITHUB_REPO="git@github.com:cbwinslow/dotfiles5.git"
GITLAB_REPO="git@gitlab.com:cbwinslow/dotfiles5.git"

# Check if we're in the right directory
if [ ! -d ".git" ]; then
    echo -e "${RED}✗ Not in a git repository${NC}"
    echo "Please run this from the repository root"
    exit 1
fi

# Check current remote
if ! git remote | grep -q "origin"; then
    echo -e "${RED}✗ No origin remote found${NC}"
    exit 1
fi

# Add GitLab remote if not exists
if ! git remote | grep -q "gitlab"; then
    echo -e "${YELLOW}Adding GitLab remote...${NC}"
    git remote add gitlab "$GITLAB_REPO"
fi

# Fetch latest changes from both remotes
echo -e "${YELLOW}Fetching changes...${NC}"
git fetch origin
git fetch gitlab

# Check if there are changes to push
if [ -n "$(git log origin/main..HEAD --oneline)" ]; then
    echo -e "${YELLOW}Pushing changes to GitLab...${NC}"
    git push gitlab main
    echo -e "${GREEN}✓ Changes pushed to GitLab${NC}"
else
    echo -e "${BLUE}No changes to push${NC}"
fi

echo -e "${GREEN}✓ Sync completed!${NC}"
