# APIs fase 3 (numeracion, integraciones, work packs)

## Numeracion

POST /api/numbering-rules
GET /api/numbering-rules?project_id=uuid
PUT /api/numbering-rules/{id}

Request:
```json
{
  "project_id": "uuid",
  "type": "WPS",
  "pattern": "WPS-{ProjectCode}-{Seq3}",
  "next_seq": 1
}
```

Reglas:
- type permitido: WPS, PQR, WPQ, WELD, DRAWING.
- pattern debe incluir {Seq3} o {Seq4}.

## Integraciones

POST /api/integrations
GET /api/integrations
PUT /api/integrations/{id}

Request:
```json
{
  "name": "ERP-Bridge",
  "url": "https://erp.local/webhook",
  "status": "active",
  "auth": { "type": "token", "value": "..." }
}
```

Reglas:
- url debe ser valida.

## Work packs y travelers

POST /api/work-packs
GET /api/work-packs?project_id=uuid
POST /api/work-packs/{id}/travelers
GET /api/work-packs/{id}/travelers

Request (work-pack):
```json
{
  "project_id": "uuid",
  "code": "WP-001",
  "status": "open"
}
```

Request (traveler):
```json
{
  "file_path": "/files/travelers/...",
  "status": "draft"
}
```

Reglas:
- WorkPack.status permitido: open, in_progress, closed.
- Traveler.status permitido: draft, issued, closed.
