# Catalogo de reglas y motor simple (MVP)

Este catalogo permite configurar validaciones sin hardcode. Las reglas viven en
`ValidationRule` y se agrupan por norma y tipo en `ValidationRuleSet`.

## Estructura de datos

- ValidationRuleSet:
  - code: identificador estable (ej: ASME_IX_WPS)
  - applies_to: WPS, PQR, WPQ
  - standard: ASME_IX, ISO_15614_1, ISO_9606_1, ISO_9606_4
  - status: active/inactive

- ValidationRule:
  - code: identificador estable (ej: WPS_REQUIRE_PQR_APPROVED)
  - applies_to: WPS, PQR, WPQ
  - severity: error/warning/info
  - rule_json: definicion de regla
  - status: active/inactive

- ValidationRuleSetItem:
  - relaciona reglas con un ruleset y define orden de evaluacion.

## Formato de regla (rule_json)

Formato base:
```json
{
  "when": [
    { "field": "status", "op": "eq", "value": "approved" }
  ],
  "then": [
    { "field": "pqr_id", "op": "not_null" }
  ],
  "message": "Un WPS aprobado requiere PQR aprobado asociado."
}
```

Operadores soportados (MVP):
- eq, ne
- in, not_in
- not_null, is_null
- subset_of
- range_within

## Motor (logica simple)

- Cargar ruleset por norma + applies_to.
- Evaluar reglas en orden (sort_order).
- Si `when` se cumple, ejecutar `then` y devolver errores/avisos.
- Guardar resultados en memoria; no se persisten en MVP.

## Reglas iniciales (ejemplos)

### ASME_IX_WPS
- WPS_REQUIRE_PQR_APPROVED
  - when: status == approved
  - then: pqr.status == approved
- WPS_STANDARD_MATCH
  - then: wps.standard == pqr.standard
- WPS_PROCESS_SUBSET
  - then: wps.processes subset_of pqr.processes

### ISO_15614_1_WPS
- WPS_REQUIRE_PQR_APPROVED
- WPS_MATERIAL_GROUP_MATCH
  - then: wps.material_group == pqr.material_group

### ASME_IX_WPQ
- WPQ_STANDARD_MATCH
  - then: wpq.standard == ASME_IX
- WPQ_PROCESS_REQUIRED
  - then: wpq.processes not_null

### ISO_9606_1_WPQ
- WPQ_STANDARD_MATCH
  - then: wpq.standard == ISO_9606_1
