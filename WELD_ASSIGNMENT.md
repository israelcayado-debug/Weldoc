# Asignacion de WPS y soldadores a soldaduras (MVP)

Define el modelo de asignacion para controlar el cumplimiento de procedimientos
y trazabilidad de quien ejecuta cada soldadura.

## Reglas generales

- Cada soldadura debe tener al menos un WPS asignado antes de iniciar.
- Una soldadura puede tener uno o mas soldadores asignados.
- No se puede asignar un soldador fuera de continuidad.
- El WPS asignado debe estar aprobado y acorde a la norma del proyecto.

## Entidades

- WeldWpsAssignment: relaciona soldadura con WPS activo.
- WeldWelderAssignment: relaciona soldadura con soldador(es).

## Campos sugeridos

WeldWpsAssignment:
- weld_id
- wps_id
- assigned_at
- assigned_by
- status (active/removed)

WeldWelderAssignment:
- weld_id
- welder_id
- assigned_at
- assigned_by
- status (active/removed)

## Validaciones

- No permitir asignar WPS con status != approved.
- No permitir asignar soldador si esta fuera de continuidad.
