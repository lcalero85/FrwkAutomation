# Fase 13 - Visor avanzado de ejecución y trazabilidad

Esta fase agrega una vista técnica y ejecutiva para analizar cada ejecución con mayor profundidad.

## Nuevas capacidades

- Visor avanzado de una ejecución individual.
- Línea de tiempo de pasos ejecutados.
- Resumen técnico de estado, duración, navegador, ambiente y evidencia.
- Tabla detallada de pasos con selector, mensaje, error y tiempo.
- Vista de evidencias por paso cuando exista screenshot.
- Descarga de evidencias.
- Acceso directo a reportes HTML, Excel y PDF asociados.
- Reconstrucción de logs técnicos desde pasos guardados.
- Comparación entre dos ejecuciones desde la vista de ejecuciones.

## Nueva URL

```text
http://127.0.0.1:8000/ui/executions/{execution_id}
```

Ejemplo:

```text
http://127.0.0.1:8000/ui/executions/1
```

## Endpoints nuevos

```text
GET /api/executions/{execution_id}/trace
GET /api/executions/{execution_id}/logs
GET /api/executions/compare?left_id=1&right_id=2
GET /api/executions/{execution_id}/steps/{step_id}/evidence/view
GET /api/executions/{execution_id}/steps/{step_id}/evidence/download
```

## Cómo probar

1. Inicia sesión.
2. Ejecuta una prueba demo desde el dashboard o desde ejecuciones.
3. Entra a `Ejecuciones`.
4. Haz clic en `Visor avanzado`.
5. Revisa línea de tiempo, pasos, fallos, reportes y evidencias.
6. Si tienes dos ejecuciones o más, usa el comparador de ejecuciones.

## Recomendación

Para tener evidencia visual, fuerza un fallo o activa captura por paso en futuras fases. En esta versión, las evidencias dependen de los screenshots registrados por el framework durante la ejecución.
