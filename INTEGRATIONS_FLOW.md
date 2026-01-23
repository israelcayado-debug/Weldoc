# Flujo de integraciones (fase 3)

Define eventos que disparan webhooks y payloads.

## Eventos

- wps.approved
- wpq.approved
- weld.completed
- weldmap.updated

## Payload base

```json
{
  "event": "weld.completed",
  "at": "2026-01-22T10:30:00Z",
  "project_id": "uuid",
  "entity_id": "uuid",
  "data": {}
}
```

## Payloads por evento

### wps.approved
```json
{
  "event": "wps.approved",
  "project_id": "uuid",
  "entity_id": "uuid",
  "data": {
    "code": "WPS-PRJ-2026-001-001",
    "standard": "ASME_IX"
  }
}
```

### wpq.approved
```json
{
  "event": "wpq.approved",
  "project_id": "uuid",
  "entity_id": "uuid",
  "data": {
    "code": "WPQ-JP01-001",
    "standard": "ISO_9606_1"
  }
}
```

### weld.completed
```json
{
  "event": "weld.completed",
  "project_id": "uuid",
  "entity_id": "uuid",
  "data": {
    "number": "WELD-PRJ-2026-001-0001",
    "status": "completed",
    "closed_at": "2026-01-22T10:30:00Z"
  }
}
```

### weldmap.updated
```json
{
  "event": "weldmap.updated",
  "project_id": "uuid",
  "entity_id": "uuid",
  "data": {
    "drawing_id": "uuid",
    "updated_at": "2026-01-22T10:30:00Z"
  }
}
```

## Mecanismo de entrega

- Entrega async via cola.
- Reintentos: 5 intentos (1m, 5m, 15m, 1h, 6h).
- Firma: HMAC-SHA256 con secreto por IntegrationEndpoint.
- Headers:
  - X-Event-Id
  - X-Event-Type
  - X-Signature
  - X-Delivered-At

## Estado de envio

- queued -> sent -> failed
- Si falla en todos los reintentos, marcar failed y notificar admin.
