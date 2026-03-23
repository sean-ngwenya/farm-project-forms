# AGENTS.md - Farm Project Forms

## Project Overview

This repository contains static HTML forms for the Farm Project management system. There are 3 forms:
- `farm-form-1.html` - Who & What (project overview, partners, financial structure)
- `farm-form-2.html` - Farm operations (crops, land, workers, planting)
- `farm-form-3.html` - Financials & Open Notes

## Build/Lint/Test Commands

This is a **static HTML/CSS/JS project** - there is no build system, test framework, or linter configured.

### Running the Forms
Simply open any `farm-form-*.html` file in a browser, or serve locally:
```bash
# Using Python
python3 -m http.server 8000

# Using Node
npx serve .
```

### Single Test
No tests exist in this repository.

### Linting
No linter is configured. For HTML validation, consider:
- W3C HTML Validator: https://validator.w3.org/
- HTML5 Validator tools

## Code Style Guidelines

### General Structure
- Single HTML files with embedded CSS and JavaScript
- CSS goes in `<style>` tags in `<head>`
- JavaScript goes in `<script>` at end of `<body>`

### HTML Conventions
- Use semantic HTML5 elements (`section`, `div`, `label`, `input`)
- Use `kebab-case` for CSS class names (e.g., `field-group`, `btn-submit`)
- Indent with 2 spaces
- Self-closing tags: `<meta>`, `<link>`, `<br>`, `<input>`

### CSS Guidelines
- CSS custom properties (variables) in `:root` for theming
- Use CSS variables for colors, spacing, and values
- Use `rem` for font sizes, `px` for borders and small values
- Flexbox and CSS Grid for layouts
- Mobile-first responsive design with `@media` queries

### Example CSS Variable Setup
```css
:root {
  --soil: #3d2b1f;
  --bark: #6b4226;
  --leaf: #2d6a4f;
  --sprout: #52b788;
  --sun: #f4a261;
  --cream: #fdf6ec;
  --fog: #f0ebe3;
  --ink: #1a1209;
  --muted: #7a6a57;
  --border: #d6c9b5;
  --radius: 10px;
}
```

### JavaScript Guidelines
- Use `const` and `let` - avoid `var`
- Use template literals for string interpolation
- Prefer modern ES6+ syntax
- Add `use strict` if applicable
- Keep scripts minimal - forms are mostly static

### Naming Conventions
- Classes: `kebab-case` (e.g., `.respondent-card`, `.field-group`)
- IDs: `kebab-case` (avoid - use classes instead)
- Variables: `camelCase` (e.g., `handleSubmit`, `filledCount`)
- Functions: `camelCase` (e.g., `initForm`, `validateInput`)

### Accessibility
- All form inputs must have associated `<label>` elements
- Use `type` attributes correctly (`text`, `date`, `radio`, `checkbox`)
- Use `placeholder` for hints, not as replacement for labels
- Ensure sufficient color contrast (minimum 4.5:1 for text)

### Error Handling
- Form validation is client-side only
- Use `alert()` for simple validation messages
- For production, consider adding proper error states with CSS classes

### File Organization
- Each form is self-contained in one file
- External resources: Google Fonts via CDN
- No local assets - forms are standalone

### Best Practices
1. Keep CSS selectors specific to avoid conflicts
2. Use progressive enhancement - forms should work without JS
3. Test in multiple browsers
4. Validate form data before submission
5. Use `console.log` for debugging (remove in production)

## Working with This Codebase

### Adding New Form Fields
1. Copy the existing `field-group` structure
2. Update question numbers (e.g., `1.10`, `2.5.1`)
3. Add appropriate input type (`text`, `date`, `textarea`, `radio`)

### Modifying Styles
1. Edit CSS variables in `:root` for theme changes
2. Add component-specific styles after the base styles
3. Use media queries for responsive adjustments

### Form Submission
Currently forms show a success message via JS. For production:
- Add `action` attribute to `<form>` element
- Implement server-side endpoint
- Add proper error handling and loading states

## Color Scheme

The project uses an earth-toned palette inspired by farming/nature:
- **Primary**: `#2d6a4f` (leaf green) - headers, buttons, accents
- **Secondary**: `#3d2b1f` (soil brown) - headings, labels
- **Accent**: `#f4a261` (sun orange) - progress bars, highlights
- **Background**: `#fdf6ec` (cream) - page background
- **Surface**: `#f0ebe3` (fog) - card backgrounds, dividers
- **Text**: `#1a1209` (ink) - primary text
- **Muted**: `#7a6a57` - secondary text, hints

### Semantic Color Usage
- Green (`--leaf`, `--sprout`) - positive actions, section headers
- Brown (`--soil`, `--bark`) - primary headings, labels
- Orange (`--sun`) - progress indicators, call-to-action
- Cream/Fog - form backgrounds
- Border color (`--border`) - all input and card borders

## Component Patterns

### Section Pattern
```html
<div class="section">
  <div class="section-header">
    <div class="section-number">Section N</div>
    <div class="section-title">Title</div>
    <div class="section-desc">Description</div>
  </div>
  <div class="section-body">
    <!-- field-group elements -->
  </div>
</div>
```

### Field Group Pattern
```html
<div class="field-group">
  <label class="field-label">
    <span class="field-num">1.1</span> Question text
  </label>
  <input type="text" placeholder="Hint text">
</div>
```

### Radio Group Pattern
```html
<div class="field-group">
  <label class="field-label"><span class="field-num">1.2</span> Question?</label>
  <div class="radio-group">
    <label class="radio-option"><input type="radio" name="q1" value="a"> Option A</label>
    <label class="radio-option"><input type="radio" name="q1" value="b"> Option B</label>
  </div>
</div>
```

### Partner Block Pattern
```html
<div class="partner-block">
  <div class="partner-label">👤 Person N</div>
  <div class="field-group">...</div>
</div>
```

## Form Field Question Numbering

Questions follow this pattern:
- `1.x` - Section 1 (Project Overview)
- `2.x.x` - Section 2 (Partners) - sub-numbered per person
- `3.x` - Section 3 (Financial Structure)
- Each form has its own question numbering system

When adding new questions, maintain the existing numbering pattern.

## Browser Testing

Test forms in:
- Chrome/Edge (primary)
- Firefox
- Safari (iOS)
- Mobile viewport (320px - 480px width)

## Notes for Agents

- This is a simple static HTML project - no complex tooling
- Forms are data collection only - no CRUD operations
- Each form is independent and can be opened separately
- The `files/` directory contains all form files
- All three forms together collect comprehensive farm project data
- Forms use vanilla JavaScript only - no frameworks
