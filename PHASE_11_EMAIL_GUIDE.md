# Fase 11 - Envío de reportes por correo SMTP

Esta fase agrega el envío real de correos desde AutoTest Pro Framework.

## Funcionalidades

- Configuración SMTP desde `/ui/settings`.
- Envío de correo de prueba.
- Envío de reportes HTML, Excel y PDF desde `/ui/reports`.
- Adjuntos seleccionables por tipo.
- Destinatarios múltiples separados por coma, punto y coma o salto de línea.
- Auditoría de correos exitosos y fallidos.
- Endpoint API para envío de reporte por correo.

## Configuración SMTP

Desde Configuración ingresa:

- Servidor SMTP.
- Puerto SMTP.
- Usuario SMTP.
- Contraseña SMTP o app password.
- Correo remitente.
- TLS o SSL directo.
- Destinatarios por defecto.

Para Gmail normalmente se usa:

- SMTP: `smtp.gmail.com`
- Puerto: `587`
- TLS: `true`
- SSL directo: `false`
- Contraseña: App Password de Google, no la contraseña normal de la cuenta.

## Endpoints nuevos

```text
POST /api/email/test
POST /api/email/reports/{report_id}/send
```

## Nota de seguridad

Para un producto comercial, se recomienda cifrar `smtp_password` en base de datos o leerlo únicamente desde variables de entorno. Esta fase lo deja funcional para entorno local/MVP.
