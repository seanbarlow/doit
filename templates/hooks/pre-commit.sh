#!/usr/bin/env bash
# Pre-commit hook installed by doit
# This hook validates workflow compliance before allowing commits

# Exit on error
set -e

# Check if doit is available
if ! command -v doit &> /dev/null; then
    echo "Warning: doit command not found in PATH"
    echo "Skipping pre-commit validation"
    exit 0
fi

# Run pre-commit validation
# Note: The doit validate command only needs the hook type, not shell arguments.
exec doit hooks validate pre-commit
