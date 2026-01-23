# API de notificaciones (MVP)

Define endpoints para consultar y administrar notificaciones.

## Endpoints

### Listar por usuario
GET /api/notifications?recipient_id=uuid&status=queued

Response:
```json
{
  "items": [
    {
      "id": "uuid",
      "subject": "Alerta de continuidad: Juan Perez vence el 2026-02-15",
      "status": "queued",
      "created_at": "2026-01-15T06:00:00Z"
    }
  ]
}
```

### Crear notificacion (uso interno)
POST /api/notifications
```json
{
  "project_id": "uuid",
  "recipient_id": "uuid",
  "channel": "email",
  "subject": "Alerta de continuidad...",
  "body": "..."
}
```

### Actualizar estado
PUT /api/notifications/{id}
```json
{
  "status": "sent",
  "sent_at": "2026-01-15T06:10:00Z"
}
```
