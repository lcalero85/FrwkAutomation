# Fase 12 - Descarga directa de reportes y visor de evidencias

Esta fase agrega la capacidad de consultar, visualizar y descargar reportes desde la interfaz web de AutoTest Pro Framework.

## Nuevas capacidades

- Descarga directa de reportes HTML, Excel y PDF.
- Vista previa del reporte HTML desde la interfaz.
- Visor de evidencias por ejecución.
- Descarga individual de screenshots/evidencias.
- Validación de existencia de archivos antes de mostrar acciones.
- Endpoints protegidos por permisos.

## Pantalla principal

Abrir:

```text
http://127.0.0.1:8000/ui/reports
```

Desde esa pantalla se puede:

- Abrir el reporte HTML en una pestaña nueva.
- Previsualizar el HTML en un modal.
- Descargar HTML, Excel y PDF.
- Abrir el visor de evidencias.
- Enviar reportes por correo, funcionalidad agregada en Fase 11.

## Nuevos endpoints

```text
GET /api/reports/{report_id}
GET /api/reports/{report_id}/download/{file_type}
GET /api/reports/{report_id}/view/html
GET /api/reports/{report_id}/evidences
GET /api/reports/{report_id}/evidences/{step_id}/view
GET /api/reports/{report_id}/evidences/{step_id}/download
```

Valores aceptados para `file_type`:

```text
html
excel
pdf
```

## Permiso nuevo

```text
reports.download
```

Este permiso permite descargar reportes y evidencias.

## Recomendación de prueba

1. Iniciar sesión.
2. Ejecutar una prueba demo desde el dashboard.
3. Ir a Reportes.
4. Descargar HTML, Excel y PDF.
5. Abrir el visor de evidencias.

Si una ejecución no tiene screenshots, el visor mostrará una lista vacía o indicará que no hay evidencias disponibles.
