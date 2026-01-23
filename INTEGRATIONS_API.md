# API de eventos de integracion

Endpoints para listar y reintentar eventos.

## Listar eventos

GET /api/integrations/{id}/events?status=failed

Response:
```json
{
  "items": [
    {
      "id": "uuid",
      "event_type": "weld.completed",
      "status": "failed",
      "attempts": 5,
      "last_error": "timeout"
    }
  ]
}
```

## Reintentar evento

POST /api/integrations/events/{id}/retry

Response:
```json
{
  "id": "uuid",
  "status": "queued"
}
```
