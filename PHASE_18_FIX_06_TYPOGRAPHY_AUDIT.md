# Phase 18 Fix 06 - Typography and font configuration audit

## Objective
This fix normalizes the application typography so the font family and base font size configured in Settings are applied consistently across the interface.

## Changes
- Added font size options from 9 px to 28 px.
- Normalized font variables through CSS custom properties.
- Added scalable tokens: xs, sm, base, md, lg, xl and xxl.
- Applied font family and font size to body, buttons, inputs, tables, cards, menus, badges, code blocks and responsive areas.
- Added client-side validation to clamp font sizes between 9 and 28 px.
- Kept technical labels such as API, Selenium, SQLite, HTML, Excel, PDF, Page Object and Pytest unchanged.

## Modified files
- app/web/templates/settings.html
- app/web/static/css/app.css
- app/web/static/js/app.js
- app/services/settings_service.py
- app/schemas/settings_schema.py
