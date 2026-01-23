# Registro automatico de continuidad (MVP)

Define el flujo para registrar continuidad al cerrar una soldadura.

## Trigger

- Al cambiar el estado de una soldadura a `completed`.

## Pasos

1. Obtener soldadores asignados activos en WeldWelderAssignment.
2. Para cada soldador, insertar ContinuityLog:
   - welder_id
   - weld_id
   - date = fecha de cierre de la soldadura (o now)
   - process = proceso principal del WPS asignado
3. Recalcular continuidad del soldador.

## Reglas

- Si no hay WPS asignado activo, registrar process como "unknown".
- Si hay varios WPS, usar el mas reciente asignado.
