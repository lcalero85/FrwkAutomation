# AutoTest Pro Framework - Fase 9

## Seguridad, permisos y auditoría

Esta fase fortalece la seguridad inicial de la plataforma agregando controles más finos sobre roles, permisos y acciones auditables.

## Nuevas capacidades

- Permisos por rol almacenados en SQLite.
- Protección de endpoints principales por permisos.
- Auditoría de login exitoso, login fallido, logout, creación/edición de usuarios y cambio de contraseña.
- Pantalla de auditoría para administradores.
- Pantalla de perfil y cambio de contraseña.
- Rate limit básico en memoria para intentos fallidos de login API.
- Headers básicos de seguridad HTTP.
- Token JWT con expiración configurable.

## Nuevas tablas

- `permissions`
- `role_permissions`
- `audit_logs`

## Nuevas pantallas

- `/ui/profile`
- `/ui/audit`

## Nuevos endpoints

- `POST /api/auth/change-password`
- `GET /api/audit-logs`

## Credenciales iniciales

Usuario: `admin`

Contraseña: `Admin12345`

## Recomendación

Si vienes de una fase anterior, elimina la base local para que se creen las nuevas tablas y permisos:

```bash
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

del storage\autotest_pro.db
python -m app.database.init_db
python api_server.py
```

Luego abre:

```text
http://127.0.0.1:8000/login
```
