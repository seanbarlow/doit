# Do-It Brand Assets

This folder contains the official Do-It framework logo files.

## Logo Variants

| Preview | File | Use Case |
|---------|------|----------|
| <img src="doit-logo-full-color.svg" width="50"> | `doit-logo-full-color.svg` | Primary logo for light backgrounds |
| <img src="doit-logo.svg" width="50"> | `doit-logo.svg` | General purpose |
| <img src="doit-logo-outlined.svg" width="50"> | `doit-logo-outlined.svg` | When filled logos don't fit the design |
| <img src="doit-logo-white.svg" width="50"> | `doit-logo-white.svg` | Dark backgrounds |
| <img src="doit-logo-master.svg" width="50"> | `doit-logo-master.svg` | Source file for designers |

## Usage Guidelines

### When to Use Each Variant

- **Full Color** (`doit-logo-full-color.svg`): Default choice for README files, documentation, and presentations on light backgrounds
- **White** (`doit-logo-white.svg`): Use on dark backgrounds, dark mode interfaces, or colored backgrounds where the full-color version lacks contrast
- **Outlined** (`doit-logo-outlined.svg`): Use when a simpler, line-based logo fits better (icons, favicons, small sizes)
- **Standard** (`doit-logo.svg`): General purpose, when you need a single versatile option
- **Master** (`doit-logo-master.svg`): Reference file containing all design elements; use for creating new variants

### Technical Details

- **Format**: SVG (Scalable Vector Graphics)
- **Dimensions**: 200x200 viewBox
- **Colors**: Teal palette (#0d9488, #14b8a6, #2dd4c0)

## Embedding Examples

### GitHub README with Dark Mode Support

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/doit-logo-white.svg">
  <img src="media/doit-logo-full-color.svg" alt="Do-It Logo" width="200">
</picture>
```

### Simple Markdown Image

```markdown
![Do-It Logo](media/doit-logo-full-color.svg)
```

### HTML with Size Control

```html
<img src="media/doit-logo-full-color.svg" alt="Do-It Logo" width="200">
```

## License

The Do-It logo is part of the Do-It project and is licensed under the MIT License.
