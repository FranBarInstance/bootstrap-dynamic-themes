# Skill: Create Style Module

This skill allows the AI to create structural modifiers (borders, shadows, rounding, spacing) for the BTDT system.

## Project Context
Style modules change the "feel" of components without changing their palette. In this project, many style modules work through direct component selectors rather than only global Bootstrap variables.

## Directory Structure
Style modules are stored in: `btdt/themes/styles/[category]-[value].css`
Current categories include:
- `background`
- `borders`
- `rounding`
- `shadows`
- `spacing`
- `gradients`
- `accent`
- `accentSize`
- `accentColor`

## Implementation Guidelines

### 1. Border Modifiers
Use either Bootstrap variables or direct component selectors, depending on the existing pattern in the category. Match the style already used by neighboring files.

### 2. Rounding (Border Radius) Modifiers
Apply radius consistently to the actual components used in the project (`.card`, `.btn`, `.form-control`, `.dropdown-menu`, `.navbar`, etc.). Preserve dropdown usability: do not clip navbar dropdowns with `overflow: hidden`.

### 3. Shadow Modifiers
Target component shadows directly. Use subtle `rgba` colors for a premium effect.

### 4. Gradient/Glassmorphism
Use gradients sparingly. Presets should remain elegant; avoid turning style modules into heavy visual gimmicks.

### 5. Background Modules
Background modules should primarily adjust `--bs-body-bg`, `--bs-secondary-bg`, `--bs-tertiary-bg`, and `--bs-border-color`.
Default philosophy: backgrounds should usually stay white or near-white, with only subtle tints unless the requested aesthetic clearly justifies more.

### 6. Accent Modules
- `accent-[position]` controls where the accent line appears.
- `accent-[1-5]` controls thickness via `--accent-size`.
- `accent-primary|secondary|gray` controls accent color choice.

### 7. Metadata Update (CRITICAL)
If you add a NEW value to an existing category (or a new category), you MUST update `btdt/js/config-ui.js`.
- Add the new value and its human-readable label to the appropriate object.
- This ensures the UI buttons or selectors reflect the new option.

## Example Reference
```css
/* btdt/themes/styles/rounding-extra.css */
.card {
  border-radius: 1.25rem;
  overflow: hidden;
}

.btn {
  border-radius: 1rem;
}
```

## Aesthetic Standards
- **Subtlety**: When creating shadows, avoid heavy dark blooms. Use multiple layered shadows for depth.
- **Consistency**: Ensure that a "Large Spacing" module applies the increased margins consistently across different components.
- **Compatibility**: Review how the module interacts with navbars, dropdowns, cards, and form controls. A style module is not correct if it breaks component behavior.
