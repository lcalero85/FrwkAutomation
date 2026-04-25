# Fase 18 - Plantillas profesionales de proyectos, suites y casos

Esta fase agrega una biblioteca de plantillas reutilizables para acelerar la creación de artefactos de automatización.

## Objetivo

Permitir que el usuario cree rápidamente:

- Proyectos completos con suites y casos iniciales.
- Suites de prueba predefinidas.
- Casos grabados listos para ejecutar o ajustar.
- Plantillas personalizadas basadas en JSON.

## Nueva pantalla

```text
/ui/templates
```

## Nuevos endpoints

```text
GET    /api/templates
GET    /api/templates/{template_id}
POST   /api/templates
PUT    /api/templates/{template_id}
DELETE /api/templates/{template_id}
POST   /api/templates/{template_id}/apply
```

## Nuevas tablas

```text
templates
```

## Permisos agregados

```text
templates.view
templates.manage
templates.apply
```

## Plantillas incluidas por defecto

- Proyecto QA Web Smoke + Regression
- Suite de Login y Seguridad
- Caso CRUD básico
- Caso formulario con validaciones obligatorias

## Flujo recomendado

1. Iniciar sesión como administrador.
2. Entrar a Plantillas.
3. Seleccionar una plantilla.
4. Completar nombre de proyecto, URL base y navegador.
5. Presionar Aplicar plantilla.
6. Ir al Grabador para revisar el caso creado.
7. Ejecutar el caso o exportarlo como Page Object.

## Crear plantilla personalizada

El campo Payload JSON permite definir la estructura de una plantilla. Para un caso básico:

```json
{
  "name": "flujo_basico_desde_plantilla",
  "description": "Caso base creado desde una plantilla personalizada.",
  "suite_name": "Suite personalizada",
  "steps": [
    {
      "action_type": "open",
      "url": "{{BASE_URL}}",
      "expected_result": "Abrir el sistema"
    },
    {
      "action_type": "click",
      "selector_type": "css",
      "selector_value": "{{BUTTON_SELECTOR}}",
      "expected_result": "Click en botón principal"
    },
    {
      "action_type": "assert_visible",
      "selector_type": "css",
      "selector_value": "{{SUCCESS_SELECTOR}}",
      "expected_result": "Validar resultado esperado"
    }
  ]
}
```

## Notas técnicas

- Las plantillas del sistema no pueden eliminarse.
- Las plantillas personalizadas sí pueden crearse y eliminarse.
- Al aplicar una plantilla de caso se crea un caso grabado en SQLite.
- Al aplicar una plantilla de suite se crea una suite y sus casos grabados.
- Al aplicar una plantilla de proyecto se crea un proyecto con suites y casos iniciales.
