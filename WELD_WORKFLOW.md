# Workflow de soldadura (MVP)

Define estados, transiciones y reglas basicas para una soldadura.

## Estados

- planned: creada y pendiente de ejecucion.
- in_progress: asignada y en ejecucion.
- completed: soldadura terminada.
- repair: requiere reparacion.

## Transiciones permitidas

- planned -> in_progress
- in_progress -> completed
- in_progress -> repair
- repair -> in_progress
- repair -> completed

## Reglas

- No se puede pasar a completed si hay inspeccion visual post_weld en fail.
- Una soldadura en repair debe tener inspeccion visual post_weld = fail.
- Al pasar a completed, registrar fecha de cierre (campo opcional futuro).
