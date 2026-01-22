"""Roadmapit command wrapper for GitHub-integrated roadmap management.

This module imports and exposes the roadmapit command from the CLI implementation.
"""

from .roadmapit_impl import app as roadmapit_app

# Export the app for registration in main.py
app = roadmapit_app
