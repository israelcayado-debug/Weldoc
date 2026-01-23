# Ejemplos de reglas reales (MVP)

Estos ejemplos usan campos de negocio resueltos por el motor a partir de las
variables de WPS/PQR/WPQ. En el MVP, se recomienda mapear claves de
`WpsVariable`/`WpqProcess` a un objeto normalizado (ej: wps.material_pno).

## ASME IX - WPS

### WPS_REQUIRE_PQR_APPROVED
```json
{
  "when": [
    { "field": "wps.status", "op": "eq", "value": "approved" }
  ],
  "then": [
    { "field": "pqr.status", "op": "eq", "value": "approved" }
  ],
  "message": "Un WPS aprobado requiere un PQR aprobado."
}
```

### WPS_MATERIAL_PNO_MATCH
```json
{
  "then": [
    { "field": "wps.material_pno", "op": "eq", "value": "${pqr.material_pno}" }
  ],
  "message": "El P-Number del material base debe coincidir con el PQR."
}
```

### WPS_FILLER_FNO_MATCH
```json
{
  "then": [
    { "field": "wps.filler_fno", "op": "eq", "value": "${pqr.filler_fno}" }
  ],
  "message": "El F-Number del metal de aporte debe coincidir con el PQR."
}
```

### WPS_PROCESS_SUBSET
```json
{
  "then": [
    { "field": "wps.processes", "op": "subset_of", "value": "${pqr.processes}" }
  ],
  "message": "Los procesos del WPS deben estar cubiertos por el PQR."
}
```

### WPS_THICKNESS_RANGE_WITHIN
```json
{
  "then": [
    {
      "field": "wps.thickness_range",
      "op": "range_within",
      "value": "${pqr.thickness_qualified_range}"
    }
  ],
  "message": "El rango de espesor del WPS debe estar dentro del rango del PQR."
}
```

### WPS_POSITION_WITHIN
```json
{
  "then": [
    { "field": "wps.position", "op": "in", "value": "${pqr.positions}" }
  ],
  "message": "La posicion del WPS debe estar cubierta por el PQR."
}
```

## ISO 15614-1 - WPS

### WPS_MATERIAL_GROUP_MATCH
```json
{
  "then": [
    {
      "field": "wps.material_group",
      "op": "eq",
      "value": "${pqr.material_group}"
    }
  ],
  "message": "El grupo de material debe coincidir con el PQR."
}
```

### WPS_DIAMETER_RANGE_WITHIN
```json
{
  "when": [
    { "field": "wps.product_form", "op": "eq", "value": "pipe" }
  ],
  "then": [
    {
      "field": "wps.diameter_range",
      "op": "range_within",
      "value": "${pqr.diameter_qualified_range}"
    }
  ],
  "message": "El rango de diametro debe estar dentro del aprobado en el PQR."
}
```

## ASME IX - WPQ

### WPQ_STANDARD_MATCH
```json
{
  "then": [
    { "field": "wpq.standard", "op": "eq", "value": "ASME_IX" }
  ],
  "message": "La cualificacion debe estar en ASME IX."
}
```

### WPQ_PROCESS_REQUIRED
```json
{
  "then": [
    { "field": "wpq.processes", "op": "not_null" }
  ],
  "message": "La cualificacion requiere al menos un proceso de soldeo."
}
```

### WPQ_THICKNESS_RANGE_WITHIN
```json
{
  "then": [
    {
      "field": "wpq.thickness_range",
      "op": "range_within",
      "value": "${wpq.test_thickness_range}"
    }
  ],
  "message": "El rango de espesor debe estar dentro del rango calificado."
}
```

## ISO 9606-1 / 9606-4 - WPQ

### WPQ_STANDARD_MATCH_9606_1
```json
{
  "then": [
    { "field": "wpq.standard", "op": "eq", "value": "ISO_9606_1" }
  ],
  "message": "La cualificacion debe estar en ISO 9606-1."
}
```

### WPQ_STANDARD_MATCH_9606_4
```json
{
  "then": [
    { "field": "wpq.standard", "op": "eq", "value": "ISO_9606_4" }
  ],
  "message": "La cualificacion debe estar en ISO 9606-4."
}
```

### WPQ_POSITION_WITHIN
```json
{
  "then": [
    { "field": "wpq.position", "op": "in", "value": "${wpq.positions}" }
  ],
  "message": "La posicion indicada debe estar dentro de las posiciones aprobadas."
}
```
