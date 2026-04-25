# Fase 10 - Configuraciones reales y marca blanca

Esta fase agrega configuración editable desde la interfaz para preparar AutoTest Pro Framework como producto comercial o herramienta licenciada.

## Nuevas capacidades

- Configuración real de marca blanca.
- Nombre de aplicación editable.
- Nombre comercial / empresa.
- Texto corto para logo.
- Tagline superior de la interfaz.
- Colores principales de la UI.
- Correo de soporte y sitio web.
- Tema visual seleccionado.
- Idioma y zona horaria.
- Rutas globales de reportes, logs, screenshots y videos.
- Parámetros globales de ejecución.
- Configuración SMTP base.
- Vista previa de marca en tiempo real.
- Auditoría al guardar o restaurar configuración.

## URLs

- Interfaz de configuración: `http://127.0.0.1:8000/ui/settings`
- Swagger: `http://127.0.0.1:8000/docs`

## Endpoints nuevos

```text
GET  /api/settings/public
GET  /api/settings
PUT  /api/settings
POST /api/settings/reset
```

## Uso

1. Inicia sesión con el usuario administrador.
2. Entra a Configuración.
3. Cambia nombre, colores y rutas.
4. Guarda configuración.
5. Recarga la página para ver todos los cambios aplicados en layout y login.

## Nota

El módulo SMTP queda preparado para integrarse con el envío real de reportes en una fase posterior.
