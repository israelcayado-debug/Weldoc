# Contratos de API para weld mapping, welding list y trazabilidad

Endpoints para planos, mapas de soldadura, soldaduras, trazabilidad y
inspecciones visuales.

## Planos y revisiones

### Crear plano
POST /api/drawings
```json
{
  "project_id": "uuid",
  "code": "DRW-PRJ-2026-001-005",
  "revision": "R1",
  "file_path": "/files/drawings/...",
  "status": "active"
}
```

### Listar planos por proyecto
GET /api/drawings?project_id=uuid

### Crear nueva revision
POST /api/drawings/{id}/revisions
```json
{
  "revision": "R2",
  "file_path": "/files/drawings/..."
}
```

Nota:
- Este endpoint crea un nuevo registro en `Drawing` con el mismo `code`
  y la nueva `revision`.

## Welding Map

### Crear mapa para un plano
POST /api/weld-maps
```json
{
  "project_id": "uuid",
  "drawing_id": "uuid",
  "status": "active"
}
```

### Guardar marcado de soldaduras
POST /api/weld-maps/{id}/marks
```json
{
  "marks": [
    {
      "number": "WELD-PRJ-2026-001-0001",
      "geometry": { "type": "bbox", "x": 120, "y": 340, "w": 18, "h": 12 },
      "attributes": [
        { "name": "joint_type", "value": "BW" },
        { "name": "size", "value": "6mm" }
      ]
    }
  ]
}
```

## Welding List (soldaduras)

### Crear soldadura
POST /api/welds
```json
{
  "project_id": "uuid",
  "drawing_id": "uuid",
  "number": "WELD-PRJ-2026-001-0001",
  "status": "planned",
  "attributes": [
    { "name": "joint_type", "value": "BW" },
    { "name": "size", "value": "6mm" }
  ]
}
```

### Listar soldaduras por proyecto
GET /api/welds?project_id=uuid&status=planned

### Actualizar estado de soldadura
PUT /api/welds/{id}
```json
{
  "status": "in_progress"
}
```

### Cerrar soldadura (completed)
POST /api/welds/{id}/close
```json
{
  "closed_at": "2026-01-22T10:30:00Z"
}
```

Reglas:
- Ejecutar validaciones del workflow (inspeccion post_weld != fail).
- Registrar continuidad para soldadores asignados activos.

## Trazabilidad de materiales y consumibles

### Asignar material base
POST /api/welds/{id}/materials
```json
{
  "material_id": "uuid",
  "heat_number": "HN-12345"
}
```

### Asignar consumible
POST /api/welds/{id}/consumables
```json
{
  "consumable_id": "uuid",
  "batch": "BATCH-001"
}
```

## Inspeccion visual

### Registrar inspeccion por etapa
POST /api/welds/{id}/visual-inspections
```json
{
  "stage": "fit_up",
  "result": "pass",
  "notes": "OK",
  "inspector_id": "uuid"
}
```

### Listar inspecciones por soldadura
GET /api/welds/{id}/visual-inspections
