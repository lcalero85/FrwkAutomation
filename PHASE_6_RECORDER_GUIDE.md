# Fase 6 - Grabador de pasos

Esta fase agrega un módulo inicial de grabación de pasos para AutoTest Pro Framework.

## Objetivo

Permitir crear casos grabados y registrar pasos de automatización de forma manual/asistida desde la interfaz web.

## Interfaz

Levanta el servidor:

```bash
python api_server.py
```

Abre:

```text
http://127.0.0.1:8000/ui/recorder
```

## API agregada

```text
GET    /api/recorder/cases
POST   /api/recorder/cases
GET    /api/recorder/cases/{case_id}
PUT    /api/recorder/cases/{case_id}
DELETE /api/recorder/cases/{case_id}
POST   /api/recorder/cases/{case_id}/steps
PUT    /api/recorder/steps/{step_id}
DELETE /api/recorder/steps/{step_id}
POST   /api/recorder/selector-suggestions
GET    /api/recorder/cases/{case_id}/code
```

## Alcance actual

- Crear casos grabados.
- Agregar pasos manualmente.
- Guardar pasos en SQLite.
- Sugerir selectores básicos.
- Generar una clase Python base desde los pasos.
- Preparar el módulo para futura integración con extensión de navegador, Selenium Listener o Chrome DevTools Protocol.

## Limitación actual

Esta fase todavía no captura eventos automáticamente desde cualquier sitio web externo. Esa parte requiere una extensión de navegador o integración CDP, que debe implementarse en una fase posterior.
