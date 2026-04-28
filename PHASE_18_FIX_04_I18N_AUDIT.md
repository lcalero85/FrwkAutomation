# Phase 18 Fix 04 - Internationalization audit

This fix focuses on the language switcher across the current UI.

## Changes

- Expanded the bilingual dictionary in `app/web/static/js/app.js`.
- Added translations for the Recorder, Executions, Reports, Templates, Users, Settings, FAQ, and About screens.
- Added dynamic translation support for content rendered after API calls.
- Added fallback phrase replacement for mixed paragraphs, while skipping short technical labels.
- Technical names remain unchanged intentionally: Selenium, FastAPI, SQLite, API, HTML, PDF, Excel, Page Object, Pytest, Chrome, Firefox, and Edge.

## Validation recommended

1. Start the app.
2. Open each UI module.
3. Switch to English and refresh.
4. Switch to Spanish and refresh.
5. Validate that no non-technical Spanish/English mixture remains.

