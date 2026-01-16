# Quickstart: Documentation Logo Integration

## Overview

This feature adds DoIt branding logos to the README and documentation. Three files need to be modified/created.

## Implementation Steps

### Step 1: Update README.md

Add at **line 1** (before the title):

```html
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="media/doit-logo-white.svg">
    <img src="media/doit-logo-full-color.svg" alt="DoIt Framework Logo" width="200">
  </picture>
</div>

```

### Step 2: Update docs/index.md

Add at **line 1** (before the title):

```html
<div align="center">
  <img src="../media/doit-logo-full-color.svg" alt="DoIt Framework Logo" width="200">
</div>

```

### Step 3: Create media/README.md

Create new file with logo usage guidelines:

```markdown
# DoIt Brand Assets

This folder contains the official DoIt framework logo files.

## Logo Variants

| Preview | File | Use Case |
|---------|------|----------|
| ![Full Color](doit-logo-full-color.svg) | `doit-logo-full-color.svg` | Primary logo for light backgrounds |
| ![Standard](doit-logo.svg) | `doit-logo.svg` | General purpose |
| ![Outlined](doit-logo-outlined.svg) | `doit-logo-outlined.svg` | When filled logos don't fit the design |
| ![White](doit-logo-white.svg) | `doit-logo-white.svg` | Dark backgrounds |
| ![Master](doit-logo-master.svg) | `doit-logo-master.svg` | Source file for designers |

## Usage Guidelines

### When to use each variant

- **Full Color**: Default choice for README files, documentation, and presentations on light backgrounds
- **White**: Use on dark backgrounds, dark mode interfaces, or colored backgrounds where the full-color version lacks contrast
- **Outlined**: Use when a simpler, line-based logo fits better (icons, favicons, small sizes)
- **Standard**: General purpose, when you need a single versatile option
- **Master**: Reference file containing all design elements; use for creating new variants

### Technical Details

- **Format**: SVG (Scalable Vector Graphics)
- **Dimensions**: 200x200 viewBox
- **Colors**: Teal palette (#0d9488, #14b8a6, #2dd4c0)

### Embedding in Markdown

For GitHub README with dark mode support:
\`\`\`html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/doit-logo-white.svg">
  <img src="media/doit-logo-full-color.svg" alt="DoIt Logo" width="200">
</picture>
\`\`\`

For simple embedding:
\`\`\`markdown
![DoIt Logo](media/doit-logo-full-color.svg)
\`\`\`
```

## Verification

After implementation, verify:

1. [ ] README.md shows logo on GitHub (light mode)
2. [ ] README.md shows white logo on GitHub (dark mode)
3. [ ] docs/index.md shows logo when rendered
4. [ ] media/README.md displays with all logo previews
5. [ ] All images have alt text

## Files Changed

| File | Action | Lines Changed |
|------|--------|---------------|
| `README.md` | MODIFY | +7 lines at top |
| `docs/index.md` | MODIFY | +5 lines at top |
| `media/README.md` | CREATE | ~60 lines |
