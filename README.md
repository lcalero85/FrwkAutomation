# AutoTest Pro Framework

Base profesional para un framework de automatización web con Python, Selenium y reportería ejecutiva.

## Estado actual

Esta versión incluye la Fase 2 y Fase 3:

- Selenium Core.
- Driver Factory para Chrome, Firefox y Edge.
- Page Object Model base.
- Acciones encapsuladas.
- Assertions reutilizables.
- Logs técnicos.
- Screenshots en fallos.
- Ejecución por consola.
- Reporte HTML profesional.
- Reporte Excel profesional con hojas separadas y gráfica.
- Reporte PDF ejecutivo.
- Registro de pasos ejecutados.
- Resumen ejecutivo con métricas y recomendaciones.

## Instalación local

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

En Linux o macOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Ejecución demo

```bash
python run.py --browser chrome --headless false --env demo
```

También puedes indicar formatos de reporte:

```bash
python run.py --browser chrome --headless false --env demo --report html,excel,pdf
```

Modo headless:

```bash
python run.py --browser chrome --headless true --env demo --report html,excel,pdf
```

Firefox:

```bash
python run.py --browser firefox --headless false --env demo --report html,excel,pdf
```

Edge:

```bash
python run.py --browser edge --headless false --env demo --report html,excel,pdf
```

## Reportes generados

Al finalizar la ejecución se generan archivos en:

```text
reports/html/
reports/excel/
reports/pdf/
```

El reporte HTML incluye:

- Estado general.
- Porcentaje de éxito.
- Pasos ejecutados.
- Duración.
- Información del proyecto.
- Ambiente.
- Navegador.
- Tabla de pasos.
- Recomendaciones ejecutivas.

El reporte Excel incluye hojas:

- Resumen.
- Pasos ejecutados.
- Errores.
- Métricas.

El reporte PDF incluye:

- Portada ejecutiva.
- Métricas principales.
- Recomendaciones.
- Detalle de pasos.
- Sección de errores, si aplica.

## Comando principal

```bash
python run.py --browser chrome --headless false --env demo --report html,excel,pdf
```

## Estructura principal

```text
autotest_pro_framework/
├── framework/
│   ├── core/
│   ├── logging/
│   ├── reporting/
│   ├── runners/
│   └── utils/
├── examples/
├── config/
├── reports/
├── logs/
├── screenshots/
├── requirements.txt
├── .env.example
└── run.py
```

## Próxima fase recomendada

Fase 4: Persistencia en SQLite y API Backend con FastAPI.

En esa fase se debe agregar:

- Base de datos SQLite real.
- Modelos SQLAlchemy.
- Historial de ejecuciones.
- Registro de reportes generados.
- API REST.
- Endpoints para proyectos, suites, casos y ejecuciones.

---

# Fase 4: Persistencia SQLite y API Backend

Esta fase agrega una capa de persistencia local con SQLite y un backend API con FastAPI.

## Nuevos módulos agregados

```text
app/
├── api/
│   ├── main.py
│   └── routes/
├── database/
│   ├── connection.py
│   ├── init_db.py
│   └── models.py
├── schemas/
├── services/
└── security/
```

## Inicializar base de datos

Desde la raíz del proyecto:

```bash
python -m app.database.init_db
```

Esto crea la base SQLite en:

```text
storage/autotest_pro.db
```

También crea datos demo:

- Rol Administrador
- Usuario admin
- Ambiente demo
- Proyecto demo
- Suite demo
- Caso demo

Credenciales demo configurables desde `.env`:

```text
DEFAULT_ADMIN_USER=admin
DEFAULT_ADMIN_PASSWORD=Admin12345
```

## Levantar API local

Opción 1:

```bash
python api_server.py
```

Opción 2:

```bash
uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000
```

Abrir en navegador:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

## Endpoints principales

```text
GET  /health
GET  /api/dashboard/metrics
GET  /api/projects
POST /api/projects
GET  /api/executions
POST /api/executions/run-demo
GET  /api/reports
```

## Ejecutar prueba demo desde API

Desde Swagger:

```text
POST /api/executions/run-demo
```

Body:

```json
{
  "browser": "chrome",
  "headless": false,
  "environment": "demo",
  "test": "login_demo",
  "report": "html,excel,pdf"
}
```

La ejecución seguirá generando reportes en:

```text
reports/html/
reports/excel/
reports/pdf/
```

Y también guardará el resultado en SQLite.

## Fase 6 - Grabador de pasos

La versión 0.6.0 agrega el módulo de grabador de pasos.

URL principal:

```text
http://127.0.0.1:8000/ui/recorder
```

Endpoints disponibles en Swagger:

```text
http://127.0.0.1:8000/docs
```

El grabador permite crear casos, registrar pasos, sugerir selectores básicos y generar código Python base para un Page Object.


## Fase 7 - Scheduler y orquestador

Esta versión agrega una pantalla de scheduler en `/ui/scheduler` y nuevos endpoints para administrar jobs programados.

### Endpoints nuevos

- `GET /api/scheduler/jobs`
- `POST /api/scheduler/jobs`
- `GET /api/scheduler/jobs/{job_id}`
- `PUT /api/scheduler/jobs/{job_id}`
- `DELETE /api/scheduler/jobs/{job_id}`
- `POST /api/scheduler/jobs/{job_id}/run-now`

### Probar en local

```bash
python -m app.database.init_db
python api_server.py
```

Abrir:

```text
http://127.0.0.1:8000/ui/scheduler
```

En esta fase el scheduler permite crear jobs y ejecutarlos bajo demanda. La ejecución recurrente en background queda preparada para una fase posterior con APScheduler persistente.

## Fase 8 - Seguridad, login, usuarios y roles

Esta versión agrega autenticación para la interfaz web y endpoints API para usuarios y roles.

### Acceso inicial

Después de inicializar la base de datos, se crea un usuario administrador por defecto:

```text
Usuario: admin
Contraseña: Admin12345
```

Estos valores pueden cambiarse en `.env` usando:

```env
DEFAULT_ADMIN_USER=admin
DEFAULT_ADMIN_EMAIL=admin@autotestpro.local
DEFAULT_ADMIN_PASSWORD=Admin12345
SECRET_KEY=change-this-secret-key-in-production
```

### Levantar en local

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m app.database.init_db
python api_server.py
```

Luego abre:

```text
http://127.0.0.1:8000/login
```

### Módulos nuevos

- Login web con cookie HTTPOnly.
- Logout.
- Middleware lógico de protección para las vistas `/ui`.
- Token JWT para API.
- Endpoints `/api/auth/login`, `/api/auth/me`, `/api/auth/logout`.
- Endpoints `/api/users` y `/api/roles`.
- Pantalla `/ui/users` para administración inicial de usuarios.
- Roles base: Administrador, QA Lead, QA Automation y Viewer.


## Fase 9 - Seguridad y auditoría

Esta versión agrega permisos finos por rol, auditoría, cambio de contraseña, perfil de usuario, protección de endpoints y headers básicos de seguridad.

Nuevas URLs:

```text
http://127.0.0.1:8000/ui/profile
http://127.0.0.1:8000/ui/audit
```

Para una instalación limpia:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m app.database.init_db
python api_server.py
```

## Fase 10 - Configuraciones reales y marca blanca

La plataforma ahora incluye un módulo funcional de configuración desde la interfaz:

- Marca blanca.
- Nombre comercial.
- Texto del logo.
- Colores principales.
- Correo de soporte.
- Sitio web.
- Tema, idioma y zona horaria.
- Rutas de reportes, logs, screenshots y videos.
- Parámetros globales de ejecución.
- Configuración SMTP base.

### Acceso

```text
http://127.0.0.1:8000/ui/settings
```

### Endpoints

```text
GET  /api/settings/public
GET  /api/settings
PUT  /api/settings
POST /api/settings/reset
```

Versión de la fase: `0.11.0`.


## Fase 11 - Envío real de reportes por correo

Se agregó configuración SMTP funcional, correo de prueba y envío de reportes HTML/Excel/PDF desde la pantalla de reportes. Ver `PHASE_11_EMAIL_GUIDE.md`.

## Fase 12 - Descarga de reportes y visor de evidencias

Esta versión agrega descarga directa de reportes y visor de evidencias desde la interfaz web.

Nuevas opciones principales:

- Descargar reporte HTML.
- Descargar reporte Excel.
- Descargar reporte PDF.
- Ver reporte HTML desde la interfaz.
- Abrir reporte HTML en nueva pestaña.
- Consultar evidencias por ejecución.
- Previsualizar screenshots.
- Descargar evidencias individuales.

Pantalla:

```text
http://127.0.0.1:8000/ui/reports
```

Endpoints agregados:

```text
GET /api/reports/{report_id}
GET /api/reports/{report_id}/download/{file_type}
GET /api/reports/{report_id}/view/html
GET /api/reports/{report_id}/evidences
GET /api/reports/{report_id}/evidences/{step_id}/view
GET /api/reports/{report_id}/evidences/{step_id}/download
```

## Fase 13 - Visor avanzado de ejecución y trazabilidad

Esta versión incluye una mejora importante para analizar ejecuciones desde la interfaz:

- Vista avanzada por ejecución.
- Línea de tiempo de pasos.
- Resumen técnico.
- Fallos detectados.
- Logs reconstruidos.
- Evidencias por paso.
- Acceso a reportes generados.
- Comparación entre ejecuciones.

URL principal:

```text
http://127.0.0.1:8000/ui/executions
```

Visor avanzado:

```text
http://127.0.0.1:8000/ui/executions/{execution_id}
```

Guía detallada:

```text
PHASE_13_EXECUTION_TRACEABILITY_GUIDE.md
```

## Fase 14 - Ejecución real de casos grabados

Se agregó la ejecución real de casos creados en el módulo Grabador.

URL:

```text
http://127.0.0.1:8000/ui/recorder
```

Endpoint:

```text
POST /api/recorder/cases/{case_id}/run
```

El seed de base de datos crea un caso listo para probar llamado `login_recorded_demo`.

Para probarlo:

```bash
python -m app.database.init_db
python api_server.py
```

Luego inicia sesión, entra al Grabador, abre el caso demo y presiona `Ejecutar`.

## Fase 15 - Grabador automático con extensión de Chrome

Esta versión agrega una extensión local para capturar acciones reales desde Chrome y convertirlas en pasos grabados dentro del módulo Recorder.

Carpeta de la extensión:

```text
browser_extension/autotest_recorder
```

Flujo rápido:

1. Levanta la plataforma con `python api_server.py`.
2. Entra a `/ui/recorder`.
3. Crea o abre un caso grabado.
4. Presiona `Grabador automático`.
5. Instala la extensión desde `chrome://extensions` usando `Load unpacked`.
6. Configura en la extensión el Case ID y `http://127.0.0.1:8000`.
7. Activa la captura e interactúa con el sitio bajo prueba.
8. Regresa a Recorder y presiona `Refrescar pasos`.

Guía completa: `PHASE_15_BROWSER_RECORDER_GUIDE.md`.


## Fase 16 - Grabador automático más fácil de usar

Se agregó un asistente visual para el grabador automático, estado de conexión, limpieza de duplicados, borrado de pasos y una extensión de Chrome más entendible. Ver `PHASE_16_RECORDER_UX_GUIDE.md`.

## Fase 17: Exportación a Page Object

El módulo Grabador ahora permite exportar un caso capturado como código Python profesional:

- Page Object generado.
- Test Pytest generado.
- README de uso.
- ZIP descargable listo para versionar.

Ruta principal:

```text
/ui/recorder
```

Endpoints principales:

```text
GET  /api/recorder/cases/{case_id}/export/preview
POST /api/recorder/cases/{case_id}/export
GET  /api/recorder/cases/{case_id}/export/download
```


## Fase 18 - Plantillas profesionales

Esta versión incluye una biblioteca de plantillas para crear rápidamente proyectos, suites y casos grabados.

Nueva URL:

```text
http://127.0.0.1:8000/ui/templates
```

Guía técnica:

```text
PHASE_18_PROFESSIONAL_TEMPLATES_GUIDE.md
```
