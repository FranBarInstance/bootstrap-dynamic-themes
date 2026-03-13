# Skill: Create Font Module

This skill allows the AI to add new typography options to the BTDT ecosystem using Google Fonts.

## Project Context
The system uses modular CSS files to load fonts dynamically. Each module imports the font and maps it to Bootstrap's CSS variables.

## Directory Structure
Font modules are stored in: `btdt/themes/fonts/[font-name].css`

## Implementation Guidelines

### 1. Font Import
Use `@import` to load the font from Google Fonts. Always include multiple weights (e.g., 400, 700) to support headings and body text.

### 2. CSS Variable Mapping
Map the font family to the following variables:
- `--bs-body-font-family`: The primary font for the entire application.
- `--bs-heading-font-family` (optional): Use if you want headings to have a different personality than the body.

### 3. Fallbacks
Always include standard system fallbacks (e.g., `sans-serif`, `serif`, `monospace`) to ensure a graceful degradation.

## Example Reference
```css
/* btdt/themes/fonts/inter.css */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

:root {
  --bs-body-font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
```

## Selection Criteria
- **Professionalism**: Pick fonts that look premium and are highly legible.
- **Variety**: Offer a mix of High-quality Sans-serifs (Modern), Serifs (Classic), and Mono fonts (Technical).
- **Performance**: Only import necessary weights to keep load times fast.
