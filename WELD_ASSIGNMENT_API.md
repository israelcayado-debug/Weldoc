# API de asignacion de WPS y soldadores

Define endpoints para asignar WPS y soldadores a soldaduras.

## WPS

### Asignar WPS a soldadura
POST /api/welds/{id}/wps-assignments
```json
{
  "wps_id": "uuid",
  "assigned_by": "uuid"
}
```

Reglas:
- WPS debe estar en status = approved.
- WPS.standard debe estar permitido en el proyecto.
- Desactivar asignaciones previas (status = removed) si solo se permite un WPS activo.

### Listar asignaciones de WPS
GET /api/welds/{id}/wps-assignments

### Remover asignacion
DELETE /api/welds/{id}/wps-assignments/{assignment_id}

## Soldadores

### Asignar soldador a soldadura
POST /api/welds/{id}/welder-assignments
```json
{
  "welder_id": "uuid",
  "assigned_by": "uuid"
}
```

Reglas:
- Soldador debe estar en continuidad.
- Registrar fecha/hora de asignacion.

### Listar asignaciones de soldadores
GET /api/welds/{id}/welder-assignments

### Remover asignacion
DELETE /api/welds/{id}/welder-assignments/{assignment_id}
