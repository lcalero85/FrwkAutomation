# Fase 17: Exportación profesional a Page Object

Esta fase agrega la capacidad de convertir un caso capturado en el Grabador en archivos Python listos para versionar.

## Funcionalidades

- Previsualización de Page Object generado.
- Previsualización de test Pytest generado.
- README de exportación por caso.
- ZIP descargable con estructura profesional:
  - `pages/`
  - `tests/`
  - `README_EXPORT.md`
- Endpoint para generar exportación.
- Endpoint para descargar último ZIP generado.

## Flujo recomendado

1. Entra a `/ui/recorder`.
2. Selecciona un caso grabado.
3. Limpia duplicados.
4. Ejecuta el caso para validar que funciona.
5. Presiona `Exportar Page Object`.
6. Revisa el código generado.
7. Presiona `Generar ZIP exportable`.
8. Descarga el ZIP.
9. Copia los archivos a tu repositorio de automatización.

## Endpoints

```text
GET  /api/recorder/cases/{case_id}/export/preview
POST /api/recorder/cases/{case_id}/export
GET  /api/recorder/cases/{case_id}/export/download
```

## Recomendación técnica

Antes de versionar el código exportado, revisa los selectores generados. Prioriza selectores estables como `id`, `name`, `data-testid` y `aria-label`.
