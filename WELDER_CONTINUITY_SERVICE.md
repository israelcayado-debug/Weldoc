# Logica backend: recalculo de continuidad (MVP)

Servicio para recalcular `WelderContinuity` en modo individual y batch.

## Recalculo individual

```text
function recalculateContinuity(welderId):
  last = ContinuityLogRepo.getMaxDateByWelder(welderId)
  if last is null:
    upsert WelderContinuity(welderId, status='out_of_continuity', last_activity_date=null)
    return

  due = addMonths(last, 6)
  status = today() <= due ? 'in_continuity' : 'out_of_continuity'

  upsert WelderContinuity({
    welder_id: welderId,
    last_activity_date: last,
    continuity_due_date: due,
    status: status,
    updated_at: now()
  })
```

## Recalculo por proyecto

```text
function recalculateContinuityByProject(projectId):
  welders = ContinuityLogRepo.listWeldersByProject(projectId)
  for each welderId in welders:
    last = ContinuityLogRepo.getMaxDateByWelderProject(welderId, projectId)
    due = addMonths(last, 6)
    status = today() <= due ? 'in_continuity' : 'out_of_continuity'
    upsert WelderContinuity(...)
```

## Consideraciones

- Si no hay actividad, se marca out_of_continuity.
- Si no hay logs en el proyecto, no se actualiza en batch (mantiene estado).
