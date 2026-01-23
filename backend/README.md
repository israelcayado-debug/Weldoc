# Backend (Django)

Estructura base para el backend en Django.

## Seeds

```
python seed_data.py
```

## Esquema OpenAPI

Regenera `openapi.yaml`:

```
export_schema.bat
```

## Continuidad de soldadores

Endpoints:
- Detalle por soldador: `POST /api/welders/{id}/continuity-recalculate/`
- Batch recomendado: `POST /api/welders/continuity-recalculate-batch/`
- Legacy (batch): `POST /api/welders/continuity-recalculate/`
