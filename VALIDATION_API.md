# APIs del motor de validacion (MVP)

Este documento define endpoints, payloads y flujo de ejecucion del motor de
validacion para WPS/PQR/WPQ. Se asume API REST.

## Endpoints

### Obtener ruleset por norma y tipo
GET /api/validation/rulesets?applies_to=WPS&standard=ASME_IX

Respuesta:
```json
{
  "ruleset": {
    "id": "uuid",
    "code": "ASME_IX_WPS",
    "applies_to": "WPS",
    "standard": "ASME_IX",
    "status": "active"
  },
  "rules": [
    {
      "id": "uuid",
      "code": "WPS_REQUIRE_PQR_APPROVED",
      "severity": "error",
      "rule_json": {}
    }
  ]
}
```

### Ejecutar validacion (interna o publica)
POST /api/validation/execute

Request:
```json
{
  "applies_to": "WPS",
  "standard": "ASME_IX",
  "entity_id": "uuid",
  "ruleset_code": "ASME_IX_WPS"
}
```

Response:
```json
{
  "entity_id": "uuid",
  "status": "failed",
  "errors": [
    {
      "code": "WPS_REQUIRE_PQR_APPROVED",
      "message": "Un WPS aprobado requiere un PQR aprobado."
    }
  ],
  "warnings": []
}
```

### Ejecutar validacion con payload (sin persistencia)
POST /api/validation/execute/payload

Request:
```json
{
  "applies_to": "WPS",
  "standard": "ASME_IX",
  "ruleset_code": "ASME_IX_WPS",
  "entity": {
    "wps": {},
    "pqr": {}
  }
}
```

Response:
```json
{
  "status": "passed",
  "errors": [],
  "warnings": []
}
```

### Gestion de reglas
POST /api/validation/rules
GET /api/validation/rules
PUT /api/validation/rules/{id}

Request (POST/PUT):
```json
{
  "code": "WPS_PROCESS_SUBSET",
  "name": "Procesos dentro del PQR",
  "applies_to": "WPS",
  "severity": "error",
  "rule_json": {},
  "status": "active"
}
```

### Gestion de rulesets
POST /api/validation/rulesets
GET /api/validation/rulesets
PUT /api/validation/rulesets/{id}

Request (POST/PUT):
```json
{
  "code": "ASME_IX_WPS",
  "name": "ASME IX WPS",
  "applies_to": "WPS",
  "standard": "ASME_IX",
  "status": "active"
}
```

### Gestion de items por ruleset
POST /api/validation/rulesets/{id}/items
DELETE /api/validation/rulesets/{id}/items/{item_id}

Request (POST):
```json
{
  "rule_id": "uuid",
  "sort_order": 10
}
```

## Flujo de ejecucion recomendado

1. El usuario guarda un WPS/WPQ en borrador.
2. Se ejecuta validacion con severidad "warning" en background.
3. Al solicitar aprobacion, se ejecuta validacion completa.
4. Si hay errores, se bloquea el cambio de estado a "approved".
5. Los resultados se devuelven a la UI para mostrar mensajes y campos fallidos.

## Integracion con WPS/WPQ

- WPS: al aprobar, llamar a `/api/validation/execute` con ruleset segun norma.
- WPQ: al aprobar, llamar a `/api/validation/execute` con ruleset segun norma.
- Opcional: validar durante el formulario usando `/execute/payload`.
