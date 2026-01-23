# Politica y versionado de migraciones

Este proyecto usa migraciones incrementales con version numerica.

## Convenciones

- Formato: `NNN_descripcion_corta.sql`.
- Version numerica incremental (001, 002, 003...).
- Cada migracion es idempotente cuando sea posible.

## Tabla de control

`SchemaVersion` registra la version aplicada:

- version (int) = numero de migracion.
- name (text) = descripcion corta.
- applied_at (timestamp).

## Migraciones registradas

001_initial_schema
- Base completa del esquema actual (ver `schema.sql`).

002_rename_report_paths
- Renombrar `file_path` -> `report_path` en `PqrResult` y `WpqTest`.
- SQL en `MIGRATION_NOTES.md`.

003_physical_types
- Ajuste de tipos fisicos (varchar) en campos clave.
- Ver `schema.sql` para el detalle.
