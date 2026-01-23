# Logica backend: cierre de soldadura (MVP)

Servicio responsable de cerrar una soldadura y disparar continuidad.

## Pseudocodigo

```text
function closeWeld(weldId, closedAt, userId):
  weld = WeldRepo.getById(weldId)
  assert weld.status in ['planned', 'in_progress', 'repair']

  // Validacion: no permitir cierre si post_weld = fail
  lastPost = VisualInspectionRepo.getLastByStage(weldId, 'post_weld')
  if lastPost and lastPost.result == 'fail':
    throw ValidationError('post_weld_fail')

  // Cambiar estado
  WeldRepo.update(weldId, {
    status: 'completed',
    closed_at: closedAt or now()
  })

  // Asignaciones de soldadores activas
  welders = WeldWelderAssignmentRepo.listActiveByWeld(weldId)

  // WPS activo mas reciente
  wps = WeldWpsAssignmentRepo.getLatestActive(weldId)
  process = wps ? WpsVariableRepo.getValue(wps.id, 'processes')[0] : 'unknown'

  for each welder in welders:
    ContinuityLogRepo.insert({
      welder_id: welder.id,
      weld_id: weldId,
      date: closedAt or today(),
      process: process
    })
    WelderContinuityService.recalculate(welder.id)

  AuditLogRepo.insert({
    entity: 'Weld',
    entity_id: weldId,
    action: 'close',
    user_id: userId
  })

  return WeldRepo.getById(weldId)
```

## Notas

- `closed_at` se agrega en una migracion futura (no esta en el esquema MVP).
- `processes` se lee del WPS activo; si son varios, se toma el primero.
- Si no hay soldadores asignados, no se registra continuidad.
