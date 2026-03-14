# Bootstrap 5 Dynamic Themes (BTDT)

A professional, real-time theme customizer and modular engine for Bootstrap 5. An alternative to Bootswatch.

**This is a production-ready theme system.** Use the included visual designer to create your look, and drop the self-contained module into your project.

## Project Structure

This project is organized as a standalone module (`btdt/`) that can be easily dropped into any project.

```text
├── btdt/                 # Root of the theme module
│   ├── editor/           # THE CUSTOMIZER (visual designer)
│   ├── css/              # Bootstrap foundation
│   ├── js/               # theme-manager.js engine
│   └── themes/           # CSS modules (colors, fonts, etc.)
├── .gitignore.example    # Suggested rules for production
└── README.md
```

## Workflow: Design to Production

1.  **Open the Editor**: Launch `btdt/editor/index.html` in your browser.
2.  **Design**: Use the panel to experiment with 30+ palettes, 20+ fonts, and multiple structural styles.
3.  **Export**: Click **"Copy CSS Preset"** to get your `@import` code.
4.  **Save & Link**: Save your design in `btdt/themes/preset/my-theme.css` and link it in your HTML.

## ⚖️ BTDT vs. Bootswatch

While **Bootswatch** is an industry standard for static themes, **BTDT** takes it to the next level by being a dynamic engine:

- **100% Editable**: Don't just pick a theme; design it. Tweak every variable (colors, fonts, borders, rounding) in real-time.
- **Dynamic Runtime**: Change the entire look and feel or toggle dark mode on-the-fly via the Javascript API without a page reload.
- **Modular Design**: Mix and match components. Use the palette from one theme and the typography from another.
- **Custom Presets**: Create and save your own theme combinations using the preset system, making your designs reusable and easy to share.
- **AI-Ready**: Extend the library easily using an AI assistant (see below).

## How it Works

The application uses a **Modular CSS Injection** strategy managed by the `ThemeManager` class.

1.  **Namespaced Engine**: Everything lives inside the `btdt/` folder to avoid filename collisions (like `js/` or `css/`) in your project.
2.  **Base Path Awareness**: The `ThemeManager` supports a `basePath` configuration, allowing it to find its theme modules regardless of where your HTML file is located.
3.  **Zero-CORS Metadata**: Presets include invisible CSS variables that the engine reads via computed styles, enabling full editor sync even in local environments (`file://`).

## AI-Assisted Development

This project includes a set of **AI Skills** located in `.agent/skills/`. These allow an AI assistant to extend the project while maintaining professional standards.

You can ask your AI assistant to:
- **Create a new color theme**: "Create a premium dark theme inspired by Cyberpunk visuals."
- **Add new fonts**: "Integrate the 'Montserrat' font from Google Fonts."
- **Design structural styles**: "Create a style module with extra large shadows and glassmorphism."
- **Compose presets**: "Create a 'Minimalist' preset using the Inter font and White palette."

The AI will follow the established architecture, ensuring link legibility and Zero-CORS metadata compatibility.

## Implementation in Production

### 1. Integration
Copy the `btdt/` folder to your project root.

> [!IMPORTANT]
> **Production Safety**: Add `btdt/editor/` to your `.gitignore` to keep the customizer out of your public environment.

### 2. Implementation in HTML
Link the base Bootstrap CSS and your chosen preset in the `<head>`.

```html
<head>
    <!-- 1. Foundation -->
    <link rel="stylesheet" href="btdt/css/bootstrap.min.css">

    <!-- 2. Your Design -->
    <link rel="stylesheet" href="btdt/themes/preset/my-theme.css">
</head>
```

### 3. Programmatic Usage
Initialize the manager specifying the `basePath` to unlock dynamic features (dark mode, live preset switching):

```javascript
/* Initialize from project root */
const themeManager = new ThemeManager({ basePath: 'btdt/' });

/* Use the API */
themeManager.toggleMode(); // Toggles between dark/light
themeManager.applyPreset('aurora'); // Loads a different preset
```

---
Built with ❤️ and Bootstrap 5.
