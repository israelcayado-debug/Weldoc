# Plan de testing (MVP)

## Unit tests
- Validaciones de reglas (motor de reglas).
- Calculo de continuidad y alertas.
- Workflow de estados (WPS/WPQ/Weld).

## Integration tests
- API WPS/PQR/WPQ con validaciones.
- API weld mapping + welding list.
- Exportaciones (cola + descarga).

## E2E tests
- Flujo completo: crear proyecto -> WPS/PQR -> WPQ -> weld map -> cerrar soldadura.
- Alertas de continuidad y notificaciones.

## Smoke tests por sprint
- Sprint 1: login, proyectos, documentos.
- Sprint 2: WPS/PQR con aprobacion.
- Sprint 3: WPQ con continuidad.
- Sprint 4: weld mapping, lista y cierre.
- Sprint 5: reportes y exportaciones.
