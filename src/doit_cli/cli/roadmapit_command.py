"""Roadmapit command wrapper for GitHub-integrated roadmap management.

This module imports and exposes the roadmapit command from doit_toolkit_cli
for use in the main doit CLI.
"""

from doit_toolkit_cli.commands.roadmapit import app as roadmapit_app

# Export the app for registration in main.py
app = roadmapit_app
