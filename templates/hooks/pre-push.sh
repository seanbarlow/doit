#!/usr/bin/env bash
# Pre-push hook installed by doit
# This hook validates workflow artifacts before allowing pushes

# Exit on error
set -e

# Check if doit is available
if ! command -v doit &> /dev/null; then
    echo "Warning: doit command not found in PATH"
    echo "Skipping pre-push validation"
    exit 0
fi

# Run pre-push validation
exec doit hooks validate pre-push "$@"
