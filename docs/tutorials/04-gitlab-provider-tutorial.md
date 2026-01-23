# Tutorial 4: Configuring GitLab as Your Git Provider

This tutorial walks you through setting up GitLab as your git provider for Do-It, enabling full integration with GitLab issues, merge requests, and milestones.

**Time**: ~30 minutes

**What you'll learn**:
- Configure Do-It to use GitLab (gitlab.com or self-hosted)
- Create a Personal Access Token with the right permissions
- Use the provider wizard for interactive setup
- Work with GitLab issues and merge requests through Do-It

**Prerequisites**:
- Do-It CLI installed (`pip install doit-toolkit-cli`)
- A GitLab account with a project
- Git repository with a GitLab remote

---

## Step 1: Create a GitLab Personal Access Token

Before configuring Do-It, you need a Personal Access Token (PAT) with the `api` scope.

### 1.1 Navigate to Access Tokens

1. Log in to GitLab (gitlab.com or your self-hosted instance)
2. Click your avatar in the top-right corner
3. Select **Preferences**
4. In the left sidebar, click **Access Tokens**

### 1.2 Create a New Token

1. Enter a **Token name**: `doit-cli` (or any descriptive name)
2. Set an **Expiration date** (recommended: 1 year)
3. Select the **api** scope (required for full functionality)
4. Click **Create personal access token**

### 1.3 Save Your Token

Copy the token immediately - you won't be able to see it again.

```text
glpat-xxxxxxxxxxxxxxxxxxxx
```

---

## Step 2: Configure the Provider

You have two options for configuring GitLab: using the interactive wizard or manual configuration.

### Option A: Interactive Wizard (Recommended)

Run the provider configuration wizard:

```bash
doit provider wizard
```

The wizard will:
1. Auto-detect GitLab from your git remote URL
2. Prompt for your Personal Access Token
3. Validate the token against the GitLab API
4. Save the configuration to `.doit/config/provider.yaml`

Example session:

```text
Git Provider Configuration Wizard
==================================

Detected remote: https://gitlab.com/your-org/your-project.git

Select your git provider:
  1. GitHub
  2. GitLab (detected)
  3. Azure DevOps

> 2

Enter your GitLab Personal Access Token:
(Token requires 'api' scope)
> glpat-xxxxxxxxxxxxxxxxxxxx

Validating token...
✓ Token valid for user: your-username

Configuration saved to .doit/config/provider.yaml
```

### Option B: Manual Configuration

Set the environment variable and create the config file manually:

```bash
# Set environment variable
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"

# Or add to your shell profile
echo 'export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"' >> ~/.bashrc
```

Create `.doit/config/provider.yaml`:

```yaml
provider:
  type: gitlab
  host: gitlab.com  # or your self-hosted domain
  project_path: your-org/your-project
```

---

## Step 3: Verify Configuration

Check that the provider is configured correctly:

```bash
doit provider status
```

Expected output:

```text
Git Provider Status
===================

Provider: GitLab
Host: gitlab.com
Project: your-org/your-project
Status: Connected
User: your-username
```

---

## Step 4: Using Do-It with GitLab

Once configured, Do-It commands automatically integrate with GitLab.

### Creating Issues with `/doit.specit`

When you create a specification, Do-It can create a linked GitLab issue:

```markdown
/doit.specit Add user authentication with OAuth2
```

The wizard will:
1. Create the spec files
2. Create a GitLab issue (Epic) for the feature
3. Link the spec to the issue in the frontmatter

### Managing the Roadmap with `doit roadmapit`

View your roadmap with GitLab issue status:

```bash
doit roadmapit show
```

Add a new roadmap item and create a GitLab epic:

```bash
doit roadmapit add "Implement user profiles" --priority P2
```

### Syncing Milestones

Sync priority-based milestones with GitLab:

```bash
doit roadmapit sync-milestones
```

This creates GitLab milestones for each priority level (P1, P2, P3, P4).

### Creating Merge Requests with `/doit.checkin`

When you complete a feature, `/doit.checkin` can create a merge request:

```markdown
/doit.checkin
```

The command will:
1. Close related GitLab issues
2. Create a git commit with proper references
3. Create a merge request to your target branch
4. Display the MR URL for review

---

## Step 5: Self-Hosted GitLab (Optional)

If you're using a self-hosted GitLab instance, the configuration is similar but with your custom host.

### Detect Self-Hosted Instance

The provider wizard auto-detects self-hosted instances from your git remote:

```text
Detected remote: https://gitlab.mycompany.com/team/project.git

Provider: GitLab (self-hosted)
Host: gitlab.mycompany.com
```

### Manual Self-Hosted Configuration

```yaml
# .doit/config/provider.yaml
provider:
  type: gitlab
  host: gitlab.mycompany.com  # Your self-hosted domain
  project_path: team/project
```

### SSL Certificate Issues

If you encounter SSL certificate errors with self-hosted instances:

1. Ensure your certificate is valid and trusted
2. Check that the root CA is in your system trust store
3. For testing only, you may need to configure your Git client to skip verification

---

## GitLab-Specific Features

### Labels

Do-It automatically creates and manages GitLab labels:

| Label | Purpose |
|-------|---------|
| `Epic` | Epic-level features |
| `Feature` | Feature issues |
| `Bug` | Bug reports |
| `Task` | Task items |
| `priority::1` through `priority::4` | Priority levels (scoped labels) |

### Issue Relationships

Do-It uses GitLab's issue links API to connect related issues. When you create a feature under an epic, they're automatically linked.

### Merge Request Terminology

Do-It uses GitLab terminology when working with GitLab:
- "Merge Request" instead of "Pull Request"
- "MR" instead of "PR"

---

## Troubleshooting

### Token Validation Fails

```text
Error: GitLab authentication failed. Check your GITLAB_TOKEN.
```

**Solutions**:
1. Verify the token hasn't expired
2. Ensure the token has `api` scope
3. Check that the token is for the correct GitLab instance

### Project Not Found

```text
Error: Project or resource not found
```

**Solutions**:
1. Verify the project path matches your GitLab project
2. Ensure you have access to the project
3. Check that the project visibility allows API access

### Rate Limiting

```text
Error: GitLab API rate limit exceeded. Retry after 60 seconds.
```

**Solutions**:
1. Wait for the rate limit window to reset
2. Reduce the frequency of API calls
3. For heavy usage, consider GitLab Premium for higher limits

---

## Summary

You've learned how to:
- Create a GitLab Personal Access Token
- Configure Do-It to use GitLab as your provider
- Use Do-It commands that integrate with GitLab
- Handle self-hosted GitLab instances
- Troubleshoot common issues

## Next Steps

- Return to the [Tutorials Index](index.md)
- Try the [Greenfield Tutorial](01-greenfield-tutorial.md) with GitLab
- Explore [Team Collaboration](03-team-collaboration-tutorial.md) with GitLab

---

## Quick Reference

| Task | Command |
|------|---------|
| Configure provider | `doit provider wizard` |
| Check status | `doit provider status` |
| View roadmap | `doit roadmapit show` |
| Sync milestones | `doit roadmapit sync-milestones` |
| Create spec with issue | `/doit.specit [description]` |
| Complete feature | `/doit.checkin` |

| Environment Variable | Purpose |
|---------------------|---------|
| `GITLAB_TOKEN` | Personal Access Token |

| Config File | Purpose |
|-------------|---------|
| `.doit/config/provider.yaml` | Provider configuration |
