# API del catalogo de atributos de soldadura

Define endpoints para administrar el catalogo y usarlo en la creacion/edicion
de soldaduras.

## Catalogo

### Crear atributo
POST /api/weld-attributes/catalog
```json
{
  "code": "joint_type",
  "name": "Tipo de junta",
  "data_type": "enum",
  "unit": null,
  "status": "active",
  "enum_values": ["BW", "FW", "Fillet", "Lap", "Butt"]
}
```

### Listar catalogo
GET /api/weld-attributes/catalog?status=active

### Actualizar atributo
PUT /api/weld-attributes/catalog/{id}
```json
{
  "name": "Tipo de junta",
  "status": "active"
}
```

## Uso en soldaduras

### Crear soldadura con atributos
POST /api/welds
```json
{
  "project_id": "uuid",
  "drawing_id": "uuid",
  "number": "WELD-PRJ-2026-001-0001",
  "status": "planned",
  "attributes": [
    { "name": "joint_type", "value": "BW" },
    { "name": "size", "value": "6", "unit": "mm" }
  ]
}
```

Reglas:
- `name` debe existir en el catalogo activo.
- `value` debe respetar el tipo (enum/number/text).
- `unit` se valida contra la unidad del catalogo cuando aplica.

Persistencia:
- `enum_values` se almacena como JSONB en `WeldAttributeCatalog`.
- Para `data_type = enum`, `enum_values` es obligatorio.
