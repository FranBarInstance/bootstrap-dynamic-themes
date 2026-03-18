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
At minimum, define:
- `--bs-body-font-family`
- `--bs-body-font-weight`
- `--bs-body-line-height`

Then style the main typographic selectors actually used in this codebase:
- headings (`h1`-`h6`, `.h1`-`.h6`)
- display headings (`.display-1`-`.display-6`)
- `.btn`

Optional but recommended when appropriate:
- `.navbar-brand`
- `.form-label`
- `code, pre, kbd`

### 3. Fallbacks
Always include standard system fallbacks (e.g., `sans-serif`, `serif`, `monospace`) to ensure a graceful degradation.

### 4. Metadata Update (CRITICAL)
After creating the CSS file, you MUST add the new font metadata to `btdt/js/config-fonts.js`.
- Add a new entry with the font ID and its human-readable label.
- This ensures the font appears in the editor's custom select dropdown with its correct preview.

## Example Reference
```css
/* btdt/themes/fonts/inter.css */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

:root {
  --bs-body-font-family: 'Inter', system-ui, -apple-system, sans-serif;
  --bs-body-font-weight: 400;
  --bs-body-line-height: 1.6;
}

h1, h2, h3, h4, h5, h6,
.h1, .h2, .h3, .h4, .h5, .h6 {
  font-family: 'Inter', sans-serif;
  font-weight: 700;
}
```

## Selection Criteria
- **Professionalism**: Pick fonts that look premium and are highly legible.
- **Variety**: Offer a mix of High-quality Sans-serifs (Modern), Serifs (Classic), and Mono fonts (Technical).
- **Performance**: Only import necessary weights to keep load times fast.
