# Notas de migracion (rename de columnas)

## Objetivo

Estandarizar campos de reportes: `file_path` -> `report_path` en PqrResult y WpqTest.

## SQL sugerido (PostgreSQL)

```sql
ALTER TABLE "PqrResult" RENAME COLUMN file_path TO report_path;
ALTER TABLE "WpqTest" RENAME COLUMN file_path TO report_path;
```

## Compatibilidad

- Actualizar codigo backend que lea `file_path`.
- Actualizar queries/reportes existentes.
