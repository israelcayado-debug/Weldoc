# API de reportes y exportaciones (MVP)

Define endpoints para reportes minimos (avance y vencimientos) y exportaciones
a Excel/PDF.

## Reportes

### Avance del proyecto
GET /api/reports/progress?project_id=uuid

Response:
```json
{
  "project_id": "uuid",
  "total_welds": 1200,
  "by_status": {
    "planned": 400,
    "in_progress": 300,
    "completed": 450,
    "repair": 50
  },
  "visual_inspection": {
    "fit_up": { "pass": 300, "fail": 20 },
    "during_weld": { "pass": 280, "fail": 15 },
    "post_weld": { "pass": 260, "fail": 10 }
  }
}
```

### Vencimientos de soldadores
GET /api/reports/expiry?project_id=uuid

Response:
```json
{
  "project_id": "uuid",
  "expiring_30_days": [
    { "welder_id": "uuid", "name": "Juan Perez", "due_date": "2026-02-15" }
  ],
  "out_of_continuity": [
    { "welder_id": "uuid", "name": "Ana Ruiz", "last_activity": "2025-07-01" }
  ]
}
```

## Exportaciones

### Excel de Welding List
POST /api/exports/welding-list
```json
{
  "project_id": "uuid",
  "filters": {
    "status": ["planned", "in_progress"]
  }
}
```

Response:
```json
{
  "export_id": "uuid",
  "status": "queued"
}
```

### Excel de WPS/PQR/WPQ
POST /api/exports/qualifications
```json
{
  "project_id": "uuid",
  "type": "WPS"
}
```

### PDF de dossier final
POST /api/exports/dossier
```json
{
  "project_id": "uuid",
  "include": ["weld_list", "wps", "pqr", "wpq", "documents"]
}
```

## Estado de exportaciones

GET /api/exports/{export_id}
```json
{
  "export_id": "uuid",
  "status": "ready",
  "file_path": "/exports/..."
}
```
