# Fase 16 - Mejoras del grabador automático

Esta fase mejora la experiencia de uso del grabador automático para que sea más clara y práctica.

## Mejoras principales

- Asistente visual del grabador automático dentro de `/ui/recorder`.
- Copia rápida de Case ID y API base.
- Estado de conexión y contador de pasos capturados.
- Botón para limpiar pasos duplicados o ruido de la extensión.
- Botón para borrar todos los pasos de un caso.
- Extensión de Chrome con instrucciones más claras.
- Indicador visual en el sitio bajo prueba cuando la captura está activa.

## Flujo recomendado

1. Inicia sesión en AutoTest Pro.
2. Entra a `/ui/recorder`.
3. Crea un caso o abre uno existente.
4. Presiona `Abrir asistente automático`.
5. Copia el Case ID y la API base.
6. Instala la extensión desde `chrome://extensions` usando `Load unpacked`.
7. Pega los datos en la extensión y presiona `Guardar y activar`.
8. Recarga el sitio bajo prueba.
9. Realiza el flujo de prueba.
10. Regresa a AutoTest Pro, presiona `Refrescar pasos` y luego `Limpiar duplicados`.
11. Ejecuta el caso grabado.

## Endpoints agregados

- `GET /api/recorder/cases/{case_id}/browser-recorder-status`
- `POST /api/recorder/cases/{case_id}/cleanup`
- `DELETE /api/recorder/cases/{case_id}/steps`

## Nota técnica

La extensión sigue siendo local y está pensada para ambientes de prueba. El endpoint público del grabador debe mantenerse restringido a localhost cuando se use en modo producto.
