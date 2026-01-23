# Modelo de datos (ERD) y nomenclatura

Convencion: tablas en singular con PascalCase. PK `id` (UUID). FK con sufijo `_id`.
Campos comunes: `created_at`, `updated_at`, `created_by`, `updated_by` donde aplique.

## Entidades y relaciones (alto nivel)

- Client 1..n Project
- Project 1..n ProjectUser (relaciona User + Role por proyecto)
- Role n..n Permission (RolePermission)
- User n..n Role (UserRole) + 0..n ProjectUser
- Project 1..n Document 1..n DocumentRevision
- Project 0..n Wps, Pqr, Wpq (pueden ser centrales o por proyecto)
- Wps n..n Pqr (WpsPqrLink)
- Project 1..n Drawing 1..n Weld (por revision)
- Drawing 1..1 WeldMap
- Weld 1..n WeldAttribute, WeldMaterial, WeldConsumable, VisualInspection
- Welder 1..n Wpq 1..n WpqProcess, WpqTest
- Welder 1..n ContinuityLog
- Project 1..n Report, Dossier

## Tablas base

### Identidad y seguridad
- User
  - id, name, email, status
  - created_at, updated_at
- Role
  - id, name, scope
- Permission
  - id, code, description
- UserRole
  - id, user_id, role_id
- RolePermission
  - id, role_id, permission_id
- ProjectUser
  - id, project_id, user_id, role_id
- AuditLog
  - id, entity, entity_id, action, user_id, at, diff_json

### Clientes y proyectos
- Client
  - id, name, tax_id, status
- Project
  - id, client_id, name, code, units, status
  - standard_set (ej: ASME_IX, ISO_15614_1, ISO_9606_1)

### Documentos
- Document
  - id, project_id, type, title, status
- DocumentRevision
  - id, document_id, revision, file_path, status

### Catalogos
- MaterialBase
  - id, spec, grade, group_no
- FillerMaterial
  - id, spec, classification, group_no
- JointType
  - id, code, geometry_json

### WPS / PQR
- Wps
  - id, project_id nullable, code, standard, status
- Pqr
  - id, project_id nullable, code, standard, status
- WpsPqrLink
  - id, wps_id, pqr_id
- WpsVariable
  - id, wps_id, name, value, unit
- PqrResult
  - id, pqr_id, test_type, result, report_path

### Soldadores y cualificacion
- Welder
  - id, name, employer, status
- Wpq
  - id, welder_id, code, standard, status
- WpqProcess
  - id, wpq_id, process, positions, thickness_range
- WpqTest
  - id, wpq_id, test_type, result, report_path
- ContinuityLog
  - id, welder_id, weld_id, date, process
- ExpiryAlert
  - id, welder_id, wpq_id, due_date, sent_at

### Planos, soldaduras y control
- Drawing
  - id, project_id, code, revision, file_path, status
- WeldMap
  - id, project_id, drawing_id, status
- Weld
  - id, project_id, drawing_id, number, status
- WeldAttribute
  - id, weld_id, name, value
- WeldMaterial
  - id, weld_id, material_id, heat_number
- WeldConsumable
  - id, weld_id, consumable_id, batch
- VisualInspection
  - id, weld_id, stage, result, notes, inspector_id, at

### Reportes y dossier
- Report
  - id, project_id, type, params_json, file_path
- Dossier
  - id, project_id, config_json, file_path
