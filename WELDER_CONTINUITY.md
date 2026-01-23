# Continuidad de soldadores (MVP)

Define calculo, bloqueo y alertas para continuidad.

## Conceptos

- Continuidad se pierde si no hay actividad registrada en 6 meses.
- Actividad = registro en ContinuityLog asociado a un weld.
- Vencimiento = fecha limite calculada desde la ultima actividad.

## Calculo

- last_activity_date = max(ContinuityLog.date) por soldador.
- continuity_due_date = last_activity_date + 6 meses.
- status:
  - in_continuity: hoy <= continuity_due_date
  - out_of_continuity: hoy > continuity_due_date

## Calculo por proyecto (batch)

- Obtener soldadores con actividad en el proyecto:
  - JOIN Weld -> ContinuityLog por weld_id.
  - Filtrar Weld.project_id = project_id.
- Para cada soldador, usar last_activity_date dentro del proyecto.
- Si no hay actividad en el proyecto, no recalcular (se ignora).

## Reglas de bloqueo

- No permitir asignar soldadores out_of_continuity a soldaduras.
- Bloquear aprobacion de WPQ si el soldador esta out_of_continuity.

## Alertas

- Generar alerta 30 dias antes de continuity_due_date.
- Reenviar alerta cada 7 dias si sigue en riesgo.

## Endpoints sugeridos

- GET /api/welders/{id}/continuity
- POST /api/welders/{id}/continuity-recalculate
- POST /api/welders/continuity-recalculate-batch

Request:
```json
{
  "project_id": "uuid",
  "scope": "project"
}
```

Reglas:
- scope = project: recalcula solo soldadores con actividad en el proyecto.
- scope = global: recalcula todos los soldadores.

### Continuidad por proyecto (semaforo)
GET /api/projects/{id}/continuity

Response:
```json
{
  "project_id": "uuid",
  "summary": {
    "in_continuity": 12,
    "out_of_continuity": 3
  },
  "items": [
    {
      "welder_id": "uuid",
      "name": "Juan Perez",
      "status": "in_continuity",
      "last_activity_date": "2026-01-10",
      "continuity_due_date": "2026-07-10"
    }
  ]
}
```
