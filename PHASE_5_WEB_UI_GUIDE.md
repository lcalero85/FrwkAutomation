# AutoTest Pro Framework - Fase 5

Esta fase agrega una interfaz web profesional sobre la API FastAPI creada en la Fase 4.

## Cómo levantar

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m app.database.init_db
python api_server.py
```

## URLs principales

- API raíz: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Interfaz web: http://127.0.0.1:8000/ui

## Módulos visuales incluidos

- Dashboard con métricas.
- Gráfica de resultados.
- Ejecución demo desde interfaz.
- Gestión básica de proyectos.
- Historial de ejecuciones.
- Detalle de pasos por ejecución.
- Consulta de reportes generados.
- Pantalla de configuración base.
- Tema claro/oscuro persistente con localStorage.

## Nota técnica

La interfaz consume los endpoints REST existentes. La lógica Selenium sigue dentro del framework, la API coordina la ejecución y la interfaz solo controla visualmente el flujo.
