# Fase 14 - Ejecución real de casos grabados

Esta fase convierte los casos creados en el módulo Grabador en pruebas reales ejecutables con Selenium.

## Funcionalidades agregadas

- Ejecutar un caso grabado desde la interfaz.
- Ejecutar los pasos guardados en SQLite usando Selenium real.
- Soporte para acciones: `open`, `click`, `double_click`, `right_click`, `type`, `assert_visible`, `assert_text`, `assert_url`, `scroll`, `hover`, `select`, `upload` y `wait`.
- Generación automática de reportes HTML, Excel y PDF.
- Persistencia de la ejecución en SQLite.
- Visualización posterior desde el Visor avanzado de ejecución.
- Caso demo grabado `login_recorded_demo` creado por seed.

## URL principal

```text
http://127.0.0.1:8000/ui/recorder
```

## Endpoint nuevo

```text
POST /api/recorder/cases/{case_id}/run
```

Body sugerido:

```json
{
  "browser": "chrome",
  "headless": false,
  "environment": "recorded",
  "base_url": null,
  "report": "html,excel,pdf",
  "timeout": 15,
  "stop_on_failure": true
}
```

## Flujo de prueba recomendado

1. Iniciar sesión.
2. Abrir el módulo Grabador.
3. Seleccionar el caso demo `login_recorded_demo`.
4. Presionar `Ejecutar` o `Ejecutar caso`.
5. Validar que se abre el navegador y se ejecutan los pasos.
6. Revisar el Visor avanzado de ejecución.
7. Revisar los reportes generados.

## Nota técnica

Esta fase ejecuta pasos manuales/asistidos guardados en SQLite. La captura automática de eventos en sitios externos sigue preparada para una fase posterior mediante extensión de navegador, Selenium listener o Chrome DevTools Protocol.
