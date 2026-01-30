#!/usr/bin/env bash
# Post-commit hook installed by doit
# This hook logs bypass events when --no-verify was used

# Exit on error
set -e

# Check if doit is available
if ! command -v doit &> /dev/null; then
    exit 0
fi

# Get the current commit hash
COMMIT_HASH=$(git rev-parse HEAD 2>/dev/null || echo "")

# Check if the pre-commit hook would have run validation
# We detect bypass by checking if the commit was made without our validation
# This is a best-effort detection since we can't know for certain if --no-verify was used

# For now, we only log when explicitly called via doit hooks log-bypass
# The actual bypass detection requires more complex logic that would need
# to track state between pre-commit and post-commit hooks.

# This hook is available for future enhancement to detect and log bypasses
exit 0
