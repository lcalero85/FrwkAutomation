# AutoTest Pro Framework - Phase 18 Fix 07

## Objetivo
Corrección profunda del sistema de idioma para evitar textos mezclados entre español e inglés en toda la interfaz.

## Cambios principales

- Se agregó un glosario bilingüe autoritativo para sobrescribir traducciones ambiguas heredadas.
- Se corrigieron textos en módulos principales:
  - Dashboard
  - Projects / Proyectos
  - Recorder / Grabador
  - Scheduler / Programador
  - Executions / Ejecuciones
  - Reports / Reportes
  - Templates / Plantillas
  - Profile / Perfil
  - Users / Usuarios
  - Audit / Auditoría
  - Settings / Configuración
  - FAQ / Preguntas frecuentes
  - About / Acerca de
- Se mejoró la traducción de textos generados dinámicamente por JavaScript.
- Se agregó traducción del título de la pestaña del navegador.
- Se corrigió la aplicación de variables CSS de tamaño de fuente para respetar el tamaño seleccionado.

## Regla para futuros textos
Todo texto nuevo debe registrarse en el glosario de `app/web/static/js/app.js` o, preferiblemente, usarse con `data-i18n` en templates nuevos.
