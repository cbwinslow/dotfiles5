# GitLab Auto-sync Setup

This document explains how to set up automatic synchronization between your GitHub repository and GitLab repository.

## Overview

The auto-sync workflow runs every 6 hours (at 00:00, 06:00, 12:00, 18:00 UTC) and automatically pushes any changes from GitHub to your GitLab repository. This acts like an "autosave" feature for your dotfiles.

## Setup Instructions

### 1. Create GitLab Personal Access Token

1. Go to your GitLab account settings
2. Navigate to **Access Tokens**
3. Create a new token with the following scopes:
   - `api` (for API access)
   - `write_repository` (for pushing to repositories)
4. Copy the token (you won't be able to see it again)

### 2. Add GitHub Secrets

In your GitHub repository, go to **Settings > Secrets and variables > Actions** and add these secrets:

#### Required Secrets:

- **`GITLAB_TOKEN`**: Your GitLab personal access token
- **`GITLAB_REPO_URL`**: The HTTPS URL of your GitLab repository
  - Format: `https://gitlab.com/yourusername/yourrepo.git`
  - Or for self-hosted: `https://your-gitlab-instance.com/yourusername/yourrepo.git`

### 3. Enable the Workflow

The workflow is automatically enabled once the secrets are configured. It will:
- Run every 6 hours on schedule
- Can also be triggered manually via GitHub Actions
- Only sync when there are actual changes
- Skip sync if repositories are already in sync

## Automated Setup with Bitwarden

A setup script is provided to automatically retrieve secrets from Bitwarden and configure GitHub secrets:

### Prerequisites

1. **GitHub CLI installed and authenticated:**
   ```bash
   gh auth login
   ```

2. **Bitwarden CLI installed**

3. **jq installed** (for JSON parsing)

### Quick Setup

1. Run the setup script:
   ```bash
   cd ~/.local/share/chezmoi
   ./setup-github-secrets.sh
   ```

2. The script will:
   - Unlock your Bitwarden vault (prompt for password if needed)
   - Retrieve the GitLab token and repository URL
   - Set up the GitHub secrets automatically

### Expected Bitwarden Items

The script looks for these Bitwarden items (in order of preference):

- **GitLab Token**: `gitlab`, `gitlab-token`, or `gitlab token`
- **GitLab Repository URL**: `gitlab-repo`, `gitlab-repo-url`, or `gitlab repository`

Make sure your Bitwarden items have the token in the "password" field and the repository URL in a custom field named "url" or in the login URI field.

### Manual Setup (Alternative)

If you prefer to set up the secrets manually or the automated script doesn't work:

## Workflow Behavior

### When Changes Are Detected:
- ✅ Checks out the repository
- ✅ Configures Git with automated user details
- ✅ Adds GitLab as a remote (if not already added)
- ✅ Pushes changes to GitLab
- ✅ Logs success message

### When No Changes:
- ℹ️ Skips the sync process
- Logs that no changes were detected

## Manual Trigger

You can manually trigger the sync by:
1. Going to the **Actions** tab in GitHub
2. Selecting "Auto-sync to GitLab" workflow
3. Clicking "Run workflow"

## Security Notes

- The GitLab token is stored securely as a GitHub secret
- The token only has the minimum required permissions
- No sensitive data is logged in the workflow output
- The workflow only pushes to the specified GitLab repository

## Troubleshooting

### Common Issues:

1. **"Permission denied" error**:
   - Check that your GitLab token has `write_repository` scope
   - Verify the token hasn't expired

2. **"Repository not found" error**:
   - Double-check the `GITLAB_REPO_URL` secret
   - Ensure the repository exists and you have access

3. **Workflow doesn't run**:
   - Check that secrets are properly configured
   - Verify the workflow file is in the correct location: `.github/workflows/autosync-gitlab.yml`

### Testing the Setup:

You can test the setup by making a small change to any file and waiting for the next scheduled run, or trigger it manually.

## Customization

### Change Sync Frequency

To modify how often the sync runs, edit the cron schedule in `autosync-gitlab.yml`:

```yaml
schedule:
  - cron: '0 0,6,12,18 * * *'  # Every 6 hours
```

Common cron examples:
- `'0 */2 * * *'` - Every 2 hours
- `'0 */4 * * *'` - Every 4 hours
- `'0 0 * * *'` - Daily at midnight UTC
- `'0 */12 * * *'` - Twice daily

### Change Target Branch

Currently syncs to `main` branch. To change this, modify the push command:

```yaml
run: |
  git push gitlab main  # Change 'main' to your desired branch
```

## Monitoring

- Check the **Actions** tab in GitHub to see workflow runs
- Each run will show whether changes were synced or skipped
- Failed runs will be marked with a red X and show error details