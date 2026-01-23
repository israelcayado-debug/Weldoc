# APIs fase 2 (documentos avanzados, END/PWHT/pressure, importaciones)

## Documentos avanzados

POST /api/documents/{id}/submit-review
POST /api/documents/{id}/approve
POST /api/documents/{id}/sign

Request (approve):
```json
{
  "approver_id": "uuid",
  "status": "approved"
}
```

Request (submit-review):
```json
{
  "submitted_by": "uuid"
}
```

Request (sign):
```json
{
  "signer_id": "uuid",
  "signature_blob": "base64..."
}
```

Reglas:
- Solo se aprueba si todos los aprobadores requeridos aprobaron.
- `sign` requiere `signature_blob`.
- DocumentRevision.status permitido: draft, in_review, approved, superseded, archived.

## END (NDE)

POST /api/nde/requests
GET /api/nde/requests?project_id=uuid
POST /api/nde/requests/{id}/results

Request (create):
```json
{
  "project_id": "uuid",
  "weld_id": "uuid",
  "method": "RT",
  "requested_by": "uuid",
  "status": "requested"
}
```

Request (result):
```json
{
  "result": "pass",
  "defect_type": null,
  "report_path": "/files/nde/..."
}
```

Reglas:
- method permitido: RT, UT, MT, PT, VT.
- status permitido: requested, scheduled, completed.

## PWHT

POST /api/pwht
GET /api/pwht?weld_id=uuid

Request:
```json
{
  "weld_id": "uuid",
  "cycle_params": { "temp": 620, "time_min": 90 },
  "result": "pass",
  "report_path": "/files/pwht/..."
}
```

Nota:
- `cycle_params` se persiste como `cycle_params_json` en la BD.

## Pruebas de presion

POST /api/pressure-tests
GET /api/pressure-tests?project_id=uuid

Request:
```json
{
  "project_id": "uuid",
  "line_id": "LINE-001",
  "test_type": "hydro",
  "pressure": 180,
  "duration_min": 60,
  "result": "pass",
  "report_path": "/files/pressure/..."
}
```

Reglas:
- test_type permitido: hydro, pneumatic.
- result permitido: pass, fail.

## Importaciones

POST /api/imports
GET /api/imports/{id}
GET /api/imports/{id}/errors

Request:
```json
{
  "type": "WPS",
  "file_path": "/imports/wps.xlsx",
  "status": "queued"
}
```

Reglas:
- type permitido: WPS, PQR, WPQ, WELD.
- status permitido: queued, running, completed, failed.
