# Fase 15 - Grabador automático con extensión de Chrome

Esta fase agrega captura automática de acciones desde el navegador usando una extensión local de Chrome.

## Qué captura

- Navegación / carga de página
- Click
- Doble click
- Click derecho
- Escritura en inputs y textareas
- Cambios en selects
- Scroll opcional
- URL actual
- Título de la página
- Selector recomendado
- Selector alternativo
- Texto visible del elemento

## Ubicación de la extensión

```text
browser_extension/autotest_recorder
```

## Cómo instalar la extensión

1. Levanta AutoTest Pro Framework localmente.
2. Abre Chrome.
3. Ingresa a `chrome://extensions`.
4. Activa `Developer mode`.
5. Presiona `Load unpacked`.
6. Selecciona la carpeta:

```text
browser_extension/autotest_recorder
```

## Cómo grabar acciones automáticamente

1. Entra a la plataforma:

```text
http://127.0.0.1:8000/login
```

2. Ve a:

```text
http://127.0.0.1:8000/ui/recorder
```

3. Crea o abre un caso grabado.
4. Presiona `Grabador automático`.
5. Copia el `Case ID`.
6. Haz clic en el icono de la extensión `AutoTest Recorder`.
7. Configura:

```text
Case ID: el ID del caso abierto
API base: http://127.0.0.1:8000
Captura activa: marcado
```

8. Abre el sitio bajo prueba e interactúa normalmente.
9. Regresa al módulo Grabador y presiona `Refrescar pasos`.

## Endpoint local usado por la extensión

```text
POST /api/recorder/public/cases/{case_id}/browser-events
```

Este endpoint se deja público para uso local porque una extensión ejecutada sobre sitios de terceros no siempre puede enviar cookies HTTPOnly de sesión. En un ambiente productivo debe protegerse con token local, firma temporal o restricción por red.

## Orden de selectores

La extensión intenta generar selectores confiables usando este orden:

1. ID
2. data-testid / data-test / data-qa
3. name
4. aria-label
5. CSS path
6. XPath alternativo

## Protección de datos sensibles

Los campos tipo password se enmascaran automáticamente como:

```text
***MASKED***
```

## Limitaciones actuales

- No intercepta acciones realizadas dentro de iframes bloqueados por políticas del navegador si la extensión no tiene acceso al frame.
- No interpreta validaciones esperadas automáticamente; se pueden agregar manualmente después.
- La captura de scroll es opcional para evitar ruido.
- Algunas aplicaciones SPA pueden disparar eventos duplicados; el backend aplica deduplicación básica.
