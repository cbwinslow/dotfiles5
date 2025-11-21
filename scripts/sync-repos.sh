#!/bin/bash
# Bidirectional Repository Sync Script
# Synchronizes changes between GitHub and GitLab repositories

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Bidirectional Repository Sync ===${NC}"
echo -e "${YELLOW}Synchronizing GitHub and GitLab repositories...${NC}"

# Repository URLs
GITHUB_REPO="git@github.com:cbwinslow/dotfiles5.git"
GITLAB_REPO="git@gitlab.com:cbwinslow/dotfiles5.git"

# Check if we're in the right directory
if [ ! -d ".git" ] && [ ! -d "$HOME/.local/share/yadm/repo.git" ]; then
    echo -e "${RED}✗ Not in a git repository${NC}"
    echo "Please run this from repository root or ensure YADM is set up"
    exit 1
fi

# Function to sync GitHub to GitLab
sync_github_to_gitlab() {
    echo -e "${YELLOW}Syncing GitHub → GitLab...${NC}"
    
    if [ -d ".git" ]; then
        # GitHub repository
        if ! git remote | grep -q "gitlab"; then
            git remote add gitlab "$GITLAB_REPO"
        fi
        
        git fetch origin
        git fetch gitlab
        
        if [ -n "$(git log origin/main..HEAD --oneline)" ]; then
            git push gitlab main
            echo -e "${GREEN}✓ GitHub → GitLab synced${NC}"
        else
            echo -e "${BLUE}No changes to sync from GitHub${NC}"
        fi
    else
        # YADM repository
        cd "$HOME"
        if ! yadm remote | grep -q "gitlab"; then
            yadm remote add gitlab "$GITLAB_REPO"
        fi
        
        yadm fetch origin
        yadm fetch gitlab
        
        if [ -n "$(yadm log origin/main..HEAD --oneline)" ]; then
            yadm push gitlab main
            echo -e "${GREEN}✓ GitHub → GitLab synced${NC}"
        else
            echo -e "${BLUE}No changes to sync from GitHub${NC}"
        fi
    fi
}

# Function to sync GitLab to GitHub
sync_gitlab_to_github() {
    echo -e "${YELLOW}Syncing GitLab → GitHub...${NC}"
    
    if [ -d ".git" ]; then
        # GitHub repository
        if ! git remote | grep -q "github"; then
            git remote add github "$GITHUB_REPO"
        fi
        
        git fetch origin
        git fetch github
        
        if [ -n "$(git log github/main..HEAD --oneline)" ]; then
            git push github main
            echo -e "${GREEN}✓ GitLab → GitHub synced${NC}"
        else
            echo -e "${BLUE}No changes to sync from GitLab${NC}"
        fi
    else
        # YADM repository
        cd "$HOME"
        if ! yadm remote | grep -q "github"; then
            yadm remote add github "$GITHUB_REPO"
        fi
        
        yadm fetch origin
        yadm fetch github
        
        if [ -n "$(yadm log github/main..HEAD --oneline)" ]; then
            yadm push github main
            echo -e "${GREEN}✓ GitLab → GitHub synced${NC}"
        else
            echo -e "${BLUE}No changes to sync from GitLab${NC}"
        fi
    fi
}

# Menu for sync options
echo -e "${BLUE}Select sync direction:${NC}"
echo "1) GitHub → GitLab"
echo "2) GitLab → GitHub"
echo "3) Bidirectional sync"
echo "n) Exit"
echo -n "Enter choice [1-3, n]: "
read -r choice

case $choice in
    1)
        sync_github_to_gitlab
        ;;
    2)
        sync_gitlab_to_github
        ;;
    3)
        echo -e "${YELLOW}Performing bidirectional sync...${NC}"
        sync_github_to_gitlab
        sync_gitlab_to_github
        ;;
    n|N)
        echo -e "${BLUE}Exiting...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}✓ Sync completed!${NC}"