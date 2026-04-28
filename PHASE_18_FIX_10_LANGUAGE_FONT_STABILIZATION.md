# Phase 18 Fix 10 - Language and Typography Stabilization

This fix replaces the previous layered language runtime with a single clean language engine.

## Main corrections

- Removed conflicting translation overrides from `app/web/static/js/app.js`.
- Added a single directional ES/EN dictionary.
- Added uppercase table header handling.
- Added placeholder/value translation for form fields where the content is a known UI sample.
- Prevented Settings from overriding the active top-bar language when loading `/api/settings`.
- Strengthened font application through CSS variables and immediate localStorage persistence.
- Font family and base font size are now applied to body, headings, nav, tables, inputs, selects, textareas, buttons, badges, and cards.

## Files changed

- `app/web/static/js/app.js`
- `app/web/static/js/settings.js`
- `app/web/static/css/app.css`
