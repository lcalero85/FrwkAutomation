# Phase 18 Fix 05 - i18n and font settings

## Objective
Fix the language switcher to avoid mixed Spanish/English text and add UI configuration for base font family and font size.

## Changes

- Reworked the frontend i18n phrase registry to prevent inverse duplicate translations from overwriting canonical pairs.
- Added additional canonical Spanish/English phrases for Recorder, Projects, Scheduler, Executions, Reports, Templates, Profile, Users, Audit, Settings, FAQ and About.
- Improved dynamic text translation for content inserted by JavaScript after page load.
- Added font family and base font size settings.
- Added CSS variables for font family and font size.
- Applied font changes immediately from Settings and persisted them through the settings API.

## Files changed

- app/web/static/js/app.js
- app/web/static/js/settings.js
- app/web/static/css/app.css
- app/web/templates/layout.html
- app/web/templates/settings.html
- app/services/settings_service.py
- app/schemas/settings_schema.py

## Notes
Technical product names and formats such as Selenium, FastAPI, SQLite, API, HTML, PDF, Excel, Page Object, Pytest, Chrome, Firefox and Edge remain untranslated intentionally.
