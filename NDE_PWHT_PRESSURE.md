# END / PWHT / Pruebas de presion (fase 2)

Modelo y endpoints sugeridos para ensayos no destructivos, tratamientos termicos
y pruebas de presion.

## Entidades

- NdeRequest (id, project_id, weld_id, method, status, requested_by, requested_at)
- NdeResult (id, nde_request_id, result, defect_type, report_path, inspector_id)
- PwhtRecord (id, weld_id, cycle_params_json, result, report_path)
- PressureTest (id, project_id, line_id, test_type, pressure, duration, result, report_path)

## API END

POST /api/nde/requests
```json
{
  "project_id": "uuid",
  "weld_id": "uuid",
  "method": "RT",
  "requested_by": "uuid"
}
```

POST /api/nde/requests/{id}/results
```json
{
  "result": "pass",
  "defect_type": null,
  "report_path": "/files/nde/..."
}
```

## API PWHT

POST /api/pwht
```json
{
  "weld_id": "uuid",
  "cycle_params": { "temp": 620, "time_min": 90 },
  "result": "pass",
  "report_path": "/files/pwht/..."
}
```

Nota:
- `cycle_params` se almacena como `cycle_params_json`.

## API Pruebas de presion

POST /api/pressure-tests
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
