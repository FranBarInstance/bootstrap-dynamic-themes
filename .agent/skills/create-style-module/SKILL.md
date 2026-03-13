# Skill: Create Style Module

This skill allows the AI to create structural modifiers (borders, shadows, rounding, spacing) for the BTDT system.

## Project Context
Style modules change the "feel" of components without changing their colors. They target Bootstrap variables for spacing and border radius.

## Directory Structure
Style modules are stored in: `btdt/themes/styles/[category]-[value].css`
Categories include: `borders`, `rounding`, `shadows`, `spacing`, `gradients`, `accent`.

## Implementation Guidelines

### 1. Border Modifiers
Target `--bs-border-width` and component-specific border variables.

### 2. Rounding (Border Radius) Modifiers
Target `--bs-border-radius`, `--bs-border-radius-lg`, etc.

### 3. Shadow Modifiers
Target `.card` shadows or generic utility shadows. Use subtle `rgba` colors for a premium effect.

### 4. Gradient/Glassmorphism
Apply translucent backgrounds and backdrop filters for modern "Glass" effects.

## Example Reference
```css
/* btdt/themes/styles/rounding-extra.css */
:root {
  --bs-border-radius: 1rem;
  --bs-border-radius-sm: 0.5rem;
  --bs-border-radius-lg: 2rem;
  --bs-border-radius-xl: 3rem;
}
```

## Aesthetic Standards
- **Subtlety**: When creating shadows, avoid heavy dark blooms. Use multiple layered shadows for depth.
- **Consistency**: Ensure that a "Large Spacing" module applies the increased margins consistently across different components.
