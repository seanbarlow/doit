# Documentation

This folder contains the documentation source files for Do-It, built using GitHub Pages with MkDocs.

## Building Locally

To build the documentation locally:

1. Install MkDocs:

   ```bash
   pip install mkdocs mkdocs-material
   ```

2. Build and serve the documentation:

   ```bash
   cd docs
   mkdocs serve
   ```

3. Open your browser to `http://localhost:8000` to view the documentation.

## Structure

- `mkdocs.yml` - MkDocs configuration file
- `index.md` - Main documentation homepage
- `installation.md` - Installation guide
- `quickstart.md` - Quick start guide
- `local-development.md` - Local development guide
- `_site/` - Generated documentation output (ignored by git)

## Deployment

Documentation is automatically built and deployed to GitHub Pages when changes are pushed to the `main` branch. The workflow is defined in `.github/workflows/docs.yml`.
