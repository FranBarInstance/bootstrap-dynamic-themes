# Skill: Create Theme Personality

## When to use this skill
Use this skill when the user asks to:
- "create a personality", "add a new personality", "make a sketch/brutalist/sticker personality"
- "add a `personality-*` style", "create a finish layer", "give the theme more character"
- refine or fix an existing `personality-*.css` file in `btdt/themes/styles/`

This skill is for final visual layers that modify how a theme feels without turning it into a different theme.

## Project Context
A personality is applied on top of an existing BTDT theme. It should work with any color palette and preserve the underlying theme identity.

The key test is:
> Does it still feel like the same theme, only with a different finish?

If the answer is yes, it is probably a personality.

Another useful way to think about it:
> A theme defines what the interface is.
> A personality defines how that same interface behaves visually at the final layer.

Use `btdt/themes/styles/personality-sketch.css` as the local project reference when needed.

## Directory Structure
Personality files live in:
- `btdt/themes/styles/personality-[value].css`
- `btdt/themes/styles/personality-[value].min.css`

## Implementation Guidelines

### 1. Treat personality as a final layer
Do not redesign the theme from scratch.

Good personality moves:
- distort borders or radii
- alter shadow character
- add texture, glow, noise, filter, relief, or finish
- sharpen or soften surfaces

Bad personality moves:
- replacing the palette with unrelated colors
- changing typography
- changing layout scale, spacing system, or component sizing
- creating a new theme identity instead of transforming the current one

It is acceptable to touch colors indirectly through finish effects, such as glow, opacity, texture, or filtering, as long as the base palette still reads as the same theme.

### 1.1 Personality must not duplicate an existing style category
A personality cannot be just "another border", "another shadow", or "another rounding option".

BTDT already has dedicated categories for things like:
- borders
- rounding
- shadows
- spacing
- gradients
- accent

So if the requested effect can be described as a simple new option in one of those families, it probably belongs there instead of in `personality-*`.

A personality is justified only when the result feels singular and distinctive as a final finish layer.

For example:
- a slightly different border thickness is not a personality
- a slightly different shadow preset is not a personality
- a new corner radius alone is not a personality
- but a contour treatment that gives the whole interface a recognizable hand-drawn or cut-paper character can be a personality

### 2. Match the BTDT component surface
When a personality affects shape or finish, target the components actually used by BTDT, not only global variables.

Common selectors:
- `.card`
- `.btn`
- `.form-control`
- `.form-select`
- `.alert`
- `.badge`
- `.dropdown-menu`
- `.navbar`
- `.modal-content`
- `.toast`
- `.accordion-item`
- `.accordion-button`
- `.list-group-item`
- `.input-group-text`
- `.pagination .page-link`
- `.nav-pills .nav-link`
- `.nav-tabs .nav-link`

### 3. Keep content usability intact
Personalities must not make content harder to read or interact with.

Critical rule learned from `personality-sketch.css`:
- cards need more restraint than buttons
- exaggerated border distortion that looks good on buttons can crowd card titles and body content
- if using irregular radii, cards usually need a milder version of the same idea, not the most extreme shape

Also:
- do not clip dropdowns or overlays accidentally
- watch header and footer corners on cards and modals
- inherit border radius carefully on `card-header`, `card-footer`, `modal-header`, and `modal-footer`

### 4. Prefer a small shape vocabulary
Define a few CSS custom properties in `:root` and reuse them.

Example pattern:
```css
:root {
  --personality-example-line: 1.5px;
  --personality-example-radius-a: 24px 120px 32px 140px / 140px 28px 120px 24px;
  --personality-example-radius-b: 16px 96px 20px 110px / 110px 18px 96px 16px;
}
```

Then apply them intentionally:
- stronger variants for buttons, badges, pills
- milder variants for cards, forms, navbars, modal surfaces

### 5. Keep the file focused
A personality should be legible as a single idea.

Examples:
- `sketch`: irregular contours, rough draft energy
- `sharp`: zero radius, hard edges, hard shadows
- `sticker`: pasted-on look, border plus lift
- `embossed`: inset relief, material depth

Avoid mixing several competing aesthetics in one file.

### 6. Catalog Sync
When adding or removing a personality value, do NOT edit `btdt/js/config-ui.js` manually.

Instead, run:
- `btdt/scripts/sync-configs.py`

This regenerates `btdt/js/config-ui.js` from the styles catalog so the personality appears correctly in the editor.

If the task also requires minified assets to be updated, run after that:
- `btdt/scripts/minify-all.py`

`btdt/scripts/minify-all.py` runs through the shared
`btdt/scripts/.venv` environment and depends on the packages listed in
`btdt/scripts/requirements.txt`.

Order matters:
1. `btdt/scripts/sync-configs.py`
2. `btdt/scripts/minify-all.py`

## Workflow
1. Inspect existing `personality-*.css`.
2. Decide the single visual idea of the new personality.
3. Create `personality-[value].css`.
4. Run `btdt/scripts/sync-configs.py` to refresh the editor catalog.
5. If the task requires minified assets too, run `btdt/scripts/minify-all.py`.
6. Sanity-check that the result still feels like the same theme with a new finish.

## Example Reference
Use `btdt/themes/styles/personality-sketch.css` as the main reference for:
- applying personality through component selectors
- using reusable irregular-radius tokens
- keeping the effect visible but not destructive to card content

## Aesthetic Standards
- **Compatibility**: It should work across many palettes, not only one.
- **Restraint**: The effect should be recognizable without overwhelming the UI.
- **Hierarchy awareness**: Cards and form controls usually need a calmer treatment than buttons or badges.
- **Single idea**: Each personality should communicate one finish clearly.
