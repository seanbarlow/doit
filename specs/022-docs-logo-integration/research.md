# Research: Documentation Logo Integration

**Feature**: 022-docs-logo-integration
**Date**: 2026-01-14

## Research Questions

### RQ-001: How to display SVG logos in GitHub README

**Decision**: Use HTML `<img>` tag with `<picture>` element for theme support

**Rationale**:
- GitHub's markdown renderer strips inline SVG for security reasons
- Standard markdown image syntax works but lacks sizing control
- HTML `<img>` tag provides width/height attributes
- `<picture>` element with `prefers-color-scheme` media query supports dark/light mode switching

**Alternatives Considered**:
- Inline SVG: Rejected - GitHub strips for security
- Base64 data URIs: Rejected - results in broken images on GitHub
- Standard markdown `![](path)`: Rejected - insufficient control over sizing

### RQ-002: How to center images in GitHub markdown

**Decision**: Use `<div align="center">` wrapper

**Rationale**:
- GitHub Flavored Markdown has no native centering support
- CSS `style="text-align: center"` is stripped by GitHub
- The `align="center"` HTML attribute is the only reliable method

**Alternatives Considered**:
- CSS inline styles: Rejected - stripped by GitHub's sanitizer
- Table-based centering: Rejected - overly complex for simple centering

### RQ-003: Dark mode support for GitHub README

**Decision**: Use `<picture>` element with full-color logo for light mode and white logo for dark mode

**Rationale**:
- GitHub supports native theme switching via `<picture>` with `prefers-color-scheme`
- The full-color logo (doit-logo-full-color.svg) works well on light backgrounds
- The white variant (doit-logo-white.svg) is designed for dark backgrounds
- This approach works across all browsers that support GitHub

**Alternatives Considered**:
- CSS media queries inside SVG: Rejected - partial browser support (Chrome/Firefox only, not Safari)
- Single logo with transparency: Rejected - teal colors may not contrast well on all dark themes
- GitHub hash fragments (`#gh-dark-mode-only`): Considered - requires showing both images in markup

### RQ-004: Logo sizing approach

**Decision**: Set width="200" for README, let height auto-calculate

**Rationale**:
- 200px provides good visibility without dominating the page
- SVGs maintain aspect ratio automatically when only width is set
- GitHub applies max-width: 100% to all images for responsiveness
- The spec requires 200-400px; 200px is appropriate for a header logo

**Alternatives Considered**:
- Percentage width (50%): Rejected - inconsistent across viewport sizes
- Fixed width and height: Rejected - unnecessary; SVG handles aspect ratio

### RQ-005: MkDocs documentation logo integration

**Decision**: Use standard markdown image syntax with relative path from docs folder

**Rationale**:
- MkDocs supports standard markdown image syntax
- Relative path `../media/doit-logo-full-color.svg` works from docs/index.md
- MkDocs Material theme handles SVG rendering well

**Alternatives Considered**:
- MkDocs theme logo configuration: Could be added later but doesn't address the index.md requirement
- Copying logo to docs folder: Rejected - violates DRY principle, requires maintaining duplicates

## Implementation Patterns

### Pattern 1: README Logo with Theme Support

```html
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="media/doit-logo-white.svg">
    <img src="media/doit-logo-full-color.svg" alt="DoIt Framework Logo" width="200">
  </picture>
</div>
```

### Pattern 2: Documentation Logo (Simple)

```markdown
<div align="center">
  <img src="../media/doit-logo-full-color.svg" alt="DoIt Framework Logo" width="200">
</div>
```

### Pattern 3: Media README Structure

```markdown
# DoIt Brand Assets

## Logo Variants

| Variant | File | Use Case |
|---------|------|----------|
| Full Color | doit-logo-full-color.svg | Primary logo for light backgrounds |
| Standard | doit-logo.svg | General purpose |
| Outlined | doit-logo-outlined.svg | When filled logos don't fit |
| White | doit-logo-white.svg | Dark backgrounds |
| Master | doit-logo-master.svg | Source file for designers |
```

## Technical Constraints

1. **GitHub Security**: No inline SVG, no base64 data URIs
2. **MkDocs Paths**: Must use relative paths from the markdown file location
3. **Browser Support**: `<picture>` element has excellent support (97%+ globally)
4. **Accessibility**: All images must have descriptive alt text

## Conclusion

The implementation is straightforward:
1. Edit README.md to add themed logo at top
2. Edit docs/index.md to add logo at top
3. Create media/README.md with usage guidelines

No code changes, data models, or API contracts required. This is a documentation-only feature.
