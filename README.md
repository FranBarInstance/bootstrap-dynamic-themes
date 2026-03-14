# Bootstrap 5 Dynamic Themes (BTDT)

A professional, real-time theme customizer and modular engine for Bootstrap 5. An alternative to **Bootswatch**.

[**🚀 Live Demo & Visual Designer**](https://franbarinstance.github.io/bootstrap-dynamic-themes/btdt/editor/)

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

1.  **Open the Editor**: Launch `btdt/editor/index.html` in your browser (or use the [Live Demo](https://franbarinstance.github.io/bootstrap-dynamic-themes/btdt/editor/)).
2.  **Design**: Use the panel to experiment with 50+ palettes, 50+ fonts, 50+ presets and multiple structural styles.
3.  **Export**: Click **"Copy CSS Preset"** to get your `@import` code.
4.  **Save & Link**: Save your design in `btdt/themes/preset/my-theme.css` and link it in your HTML.

## BTDT vs. Bootswatch

While **Bootswatch** is an industry standard for static themes, **BTDT** takes it to the next level by being a dynamic engine:

- **100% Editable**: Don't just pick a theme; design it. Tweak every variable (colors, fonts, borders, rounding) in real-time.
- **Dynamic Runtime**: Change the entire look and feel or toggle dark mode on-the-fly via the Javascript API without a page reload.
- **Modular Design**: Mix and match components. Use the palette from one theme and the typography from another.
- **Custom Presets**: Create and save your own theme combinations using the preset system, making your designs reusable and easy to share.
- **No Compilation Required**: Unlike standard Bootstrap customization, you don't need SCSS, Ruby, or Node modules to tweak your look. Just standard CSS.
- **AI-Ready**: Extend the library easily using an AI assistant (see below).

## How it Works

The application uses a **Modular CSS Injection** strategy managed by the `ThemeManager` class.

1.  **Namespaced Engine**: Everything lives inside the `btdt/` folder to avoid filename collisions (like `js/` or `css/`) in your project.
2.  **Base Path Awareness**: The `ThemeManager` supports a `basePath` configuration, allowing it to find its theme modules regardless of where your HTML file is located.
3.  **Zero-CORS Metadata**: Presets include invisible CSS variables that the engine reads via computed styles, enabling full editor sync even in local environments (`file://`).

## Pure CSS - No Compilation

Unlike many Bootstrap customization workflows that require complex SCSS/SASS setups, BTDT is built on **Pure CSS** using modern CSS custom properties (variables).

### Advantages:
- **Zero Build Steps**: No `npm install`, no Webpack, no Vite, and no precompilation required. Edit a CSS file and see the result instantly.
- **Runtime Hot-Swapping**: Change the entire look and feel of your app at runtime without reloading or rebuilding.
- **Portability**: The entire module works perfectly even when opened directly from the file system (`file:///`), making it ideal for prototyping.
- **Zero Learning Curve**: You don't need to know CSS or SASS. Use the visual customizer to design your theme and simply copy-paste the code.
- **Lightweight**: Zero toolchain overhead. You only ship the CSS you actually use.

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

### 2. Choose Implementation Method

#### Option A: Native CSS (Maximum Performance)
Best for static sites where speed is the only priority. Zero JS dependency for initial load.

```html
<head>
    <link rel="stylesheet" href="btdt/css/bootstrap.min.css">
    <link rel="stylesheet" href="btdt/themes/preset/studio.css">
</head>

<body>
    ...
    <!-- API access -->
    <script src="btdt/js/btdt.min.js"></script>
</body>
```

#### Option B: All-in-One Loader (Saves a step)
The simplest way. One single line in the `<head>` handles both CSS injection and API initialization.

```html
<head>
    <link rel="stylesheet" href="btdt/css/bootstrap.min.css">
    <script data-preset="studio" src="btdt/js/btdt.min.js"></script>
</head>
```

> [!NOTE]
> Using the JS loader (**Option B**) may cause a slight flash of unstyled content (FOUC) during page load as the CSS is injected via JavaScript. For a perfectly smooth experience, use **Option A**.

### 3. API Usage

Regardless of the option chosen (unless you skipped JS), you can use the global `btdt` object:

```javascript
btdt.load('aurora'); // Switch preset dynamically
btdt.toggleMode();   // Toggle Dark/Light mode
```

## Dynamic Contrast & Theming

A common challenge in Bootstrap 5+ is handling accessibility and contrast dynamically.

### The Standard (Static) Approach
In standard Bootstrap, developers must explicitly define the contrast mode for each container. If you have a dark background, you add `data-bs-theme="dark"` to make the child elements (text, links, buttons) visible.

```html
<!-- You must know IN ADVANCE that bg-primary is dark -->
<footer class="bg-primary" data-bs-theme="dark">
    <a class="nav-link" href="#">Static Link</a>
</footer>
```
**The limitation**: This approach is hardcoded. If you change your theme to a light version at runtime, the `data-bs-theme="dark"` attribute will remain, making the text unreadable (white text on a light background).

### The BTDT (Dynamic) Approach
BTDT uses a specialized approach to ensure your UI remains readable regardless of the active theme without modifying the HTML:

1.  **Agnostic HTML**: We use the native `.text-reset` class, which tells the element to inherit the color from its parent instead of using the default Bootstrap link color.
2.  **Smart Theme Logic**: Each BTDT CSS theme module automatically calculates the optimal contrast color based on the primary color's current brightness.

```html
<!-- Agnostic structure: works for both dark and light primary colors -->
<footer class="bg-primary">
    <a class="nav-link text-reset" href="#">Dynamic Link</a>
</footer>
```

This ensures that when you switch from a dark professional theme to a light pastel style, your menus and links **automatically adapt** their colors instantly.

---
Built with ❤️ and Bootstrap 5.
