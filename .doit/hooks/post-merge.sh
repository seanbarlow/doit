#!/usr/bin/env bash
# Post-merge hook installed by doit
# This hook auto-completes fixit workflows when fix branches are merged

# Exit on error
set -e

# Check if doit is available
if ! command -v doit &> /dev/null; then
    exit 0
fi

# Get the name of the branch that was merged
# SQUASH_MSG contains the branch name for squash merges
# Otherwise we need to check reflog

# Check if we have a squash commit message file
if [ -f ".git/SQUASH_MSG" ]; then
    # Try to extract branch name from squash message
    MERGED_BRANCH=$(head -1 .git/SQUASH_MSG | grep -oE "fix/[0-9]+-[a-z0-9-]+" || true)
fi

# Fallback: check git reflog for recent merge
if [ -z "$MERGED_BRANCH" ]; then
    # Get the most recent merge line from reflog
    REFLOG_MERGE=$(git reflog --grep-reflog="merge" -1 2>/dev/null || true)
    if [ -n "$REFLOG_MERGE" ]; then
        MERGED_BRANCH=$(echo "$REFLOG_MERGE" | grep -oE "fix/[0-9]+-[a-z0-9-]+" || true)
    fi
fi

# Fallback: Check ORIG_HEAD which points to the tip before the merge
if [ -z "$MERGED_BRANCH" ]; then
    # Get the branch that was merged using the second parent of HEAD
    PARENT2=$(git rev-parse HEAD^2 2>/dev/null || true)
    if [ -n "$PARENT2" ]; then
        # Find branch containing this commit
        MERGED_BRANCH=$(git branch -a --contains "$PARENT2" 2>/dev/null | grep -oE "fix/[0-9]+-[a-z0-9-]+" | head -1 || true)
    fi
fi

# If we found a fix branch, complete the workflow
if [ -n "$MERGED_BRANCH" ]; then
    # Extract issue ID from branch name (fix/{issue_id}-{slug})
    ISSUE_ID=$(echo "$MERGED_BRANCH" | grep -oE "fix/([0-9]+)" | sed 's/fix\///')

    if [ -n "$ISSUE_ID" ]; then
        echo "🔧 Detected merge of fix branch: $MERGED_BRANCH"
        echo "📋 Auto-completing workflow for issue #$ISSUE_ID..."

        # Call doit to complete the workflow
        # This will close the GitHub issue and mark the workflow as completed
        python -c "
from doit_cli.services.fixit_service import FixitService
from doit_cli.services.github_service import GitHubService
from doit_cli.services.state_manager import StateManager

try:
    service = FixitService()
    workflow = service.get_workflow($ISSUE_ID)
    if workflow:
        success = service.complete_workflow($ISSUE_ID, close_issue=True)
        if success:
            print('✅ Workflow completed and issue #$ISSUE_ID closed!')
        else:
            print('⚠️  Could not complete workflow (may already be completed)')
    else:
        print('ℹ️  No active workflow found for issue #$ISSUE_ID')
except Exception as e:
    print(f'⚠️  Could not auto-complete workflow: {e}')
" 2>/dev/null || echo "⚠️  Fixit workflow completion skipped (doit-cli not in environment)"
    fi
fi

exit 0
