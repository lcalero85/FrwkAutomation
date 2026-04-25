# AutoTest Pro Framework - Fase 4

## Objetivo

Agregar persistencia en SQLite y exponer una API backend con FastAPI para preparar el camino hacia la interfaz web profesional.

## Comandos rápidos

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.database.init_db
python api_server.py
```

## Abrir API

```text
http://127.0.0.1:8000/docs
```

## Probar ejecución desde API

Endpoint:

```text
POST /api/executions/run-demo
```

Body:

```json
{
  "browser": "chrome",
  "headless": false,
  "environment": "demo",
  "test": "login_demo",
  "report": "html,excel,pdf"
}
```

## Consultas útiles

```text
GET /api/dashboard/metrics
GET /api/projects
GET /api/executions
GET /api/reports
```
