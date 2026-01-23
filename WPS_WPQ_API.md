# Contratos de API para WPS/WPQ y validacion

Define endpoints principales, payloads y puntos de validacion para WPS/PQR y
WPQ/WQTR.

## WPS / PQR

### Crear WPS
POST /api/wps
```json
{
  "project_id": "uuid",
  "code": "WPS-PRJ-2026-001-001",
  "standard": "ASME_IX",
  "status": "draft",
  "variables": [
    { "name": "material_pno", "value": "P-No.1" },
    { "name": "processes", "value": "SMAW,GTAW" },
    { "name": "position", "value": "1G" },
    { "name": "thickness_range", "value": "3-12", "unit": "mm" }
  ]
}
```

### Actualizar WPS
PUT /api/wps/{id}
```json
{
  "status": "draft",
  "variables": [
    { "name": "processes", "value": "SMAW" }
  ]
}
```

### Aprobar WPS
POST /api/wps/{id}/approve
```json
{
  "pqr_ids": ["uuid"]
}
```

Validacion:
- Ejecutar `/api/validation/execute` con ruleset segun Wps.standard.
- Bloquear si hay errores.

### Enviar WPS a revision
POST /api/wps/{id}/submit-review

Reglas:
- Transicion: draft -> in_review.

### Crear PQR
POST /api/pqr
```json
{
  "project_id": "uuid",
  "code": "PQR-PRJ-2026-001-001",
  "standard": "ASME_IX",
  "status": "draft",
  "results": [
    { "test_type": "material_pno", "result": "P-No.1" },
    { "test_type": "processes", "result": "SMAW,GTAW" },
    { "test_type": "thickness_range", "result": "3-12", "unit": "mm" }
  ]
}
```

### Aprobar PQR
POST /api/pqr/{id}/approve
```json
{
  "status": "approved"
}
```

Validacion:
- Validacion minima (completitud de resultados requeridos por norma).

### Enviar PQR a revision
POST /api/pqr/{id}/submit-review

Reglas:
- Transicion: draft -> in_review.

## WPQ / WQTR

### Crear soldador
POST /api/welders
```json
{
  "name": "Juan Perez",
  "employer": "ACME",
  "status": "active"
}
```

### Crear WPQ
POST /api/wpq
```json
{
  "welder_id": "uuid",
  "code": "WPQ-JP01-001",
  "standard": "ISO_9606_1",
  "status": "draft",
  "processes": [
    { "process": "GMAW", "positions": "PA,PB", "thickness_range": "3-12" }
  ],
  "tests": [
    { "test_type": "thickness_range", "result": "3-12", "unit": "mm" },
    { "test_type": "position", "result": "PA,PB" }
  ]
}
```

### Aprobar WPQ
POST /api/wpq/{id}/approve
```json
{
  "status": "approved"
}
```

Validacion:
- Ejecutar `/api/validation/execute` con ruleset segun Wpq.standard.
- Bloquear si hay errores.

### Enviar WPQ a revision
POST /api/wpq/{id}/submit-review

Reglas:
- Transicion: draft -> in_review.

## Disparo de validacion (UI/Backend)

- Guardado en borrador: usar `/api/validation/execute/payload` para warnings.
- Cambio de estado a aprobado: usar `/api/validation/execute` y bloquear en error.
- Mostrar mensajes y campos asociados en la UI.
