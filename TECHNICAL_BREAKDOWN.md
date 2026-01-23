# Desglose tecnico por sprint (MVP)

Este documento traduce el roadmap a entregables tecnicos: modelo de datos,
APIs y pantallas por sprint. Alcance alineado a ASME IX + ISO 15614-1 y
ISO 9606-1/4.

## Sprint 1: Fundaciones

Entidades base:
- User (id, name, email, status)
- Role (id, name)
- Permission (id, code, scope)
- UserRole (user_id, role_id, project_id nullable)
- AuditLog (entity, entity_id, action, user_id, at, diff_json)
- Client (id, name, tax_id, status)
- Project (id, client_id, name, code, units, status)
- ProjectUser (project_id, user_id, role_id)
- Document (id, project_id, type, title, status)
- DocumentRevision (document_id, revision, file_path, status, created_by, created_at)

APIs:
- POST/GET/PUT users, roles, permissions.
- POST/GET/PUT projects; POST project users.
- POST/GET/PUT clients.
- POST/GET documents; POST document revisions.
- GET audit logs por entidad/proyecto.

Pantallas:
- Login y gestion de usuarios/roles.
- Clientes.
- Proyectos (alta/configuracion).
- Repositorio documental basico (carga y versionado).

## Sprint 2: WPS/PQR (ASME IX + ISO 15614-1)

Entidades:
- Wps (id, code, standard, status, project_id nullable)
- Pqr (id, code, standard, status, project_id nullable)
- WpsPqrLink (wps_id, pqr_id)
- WpsVariable (wps_id, name, value, unit)
- PqrResult (pqr_id, test_type, result, report_path)
- MaterialBase (id, spec, grade, group_no)
- FillerMaterial (id, spec, classification, group_no)
- JointType (id, code, geometry_json)

APIs:
- CRUD WPS/PQR; linkear PQR a WPS.
- Catalogos: material base, aporte, tipos de junta.
- Validaciones de reglas esenciales por norma.

Pantallas:
- Formulario guiado WPS.
- Formulario guiado PQR.
- Repositorio WPS/PQR + importacion basica.

## Sprint 3: WPQ/WQTR (ASME IX + ISO 9606-1/4)

Entidades:
- Welder (id, name, employer, status)
- Wpq (id, welder_id, code, standard, status)
- WpqProcess (wpq_id, process, positions, thickness_range)
- WpqTest (wpq_id, test_type, result, report_path)
- ContinuityLog (welder_id, weld_id, date, process)
- ExpiryAlert (welder_id, wpq_id, due_date, sent_at)

APIs:
- CRUD welders y WPQ/WQTR.
- Registrar continuidad.
- Alertas de vencimiento.
- Importacion basica de cualificaciones.

Pantallas:
- Formulario guiado WPQ/WQTR.
- Ficha de soldador con continuidad.
- Alertas de vencimiento.

## Sprint 4: Weld mapping, welding map y welding list

Entidades:
- Drawing (id, project_id, code, revision, file_path, status)
- WeldMap (id, project_id, drawing_id, status)
- Weld (id, project_id, drawing_id, number, status)
- WeldAttribute (weld_id, name, value)
- WeldMaterial (weld_id, material_id, heat_number)
- WeldConsumable (weld_id, consumable_id, batch)
- VisualInspection (weld_id, stage, result, notes, inspector_id, at)

APIs:
- CRUD planos y revisiones.
- Marcar soldaduras en plano y crear Weld.
- Listado de soldaduras con filtros y estados.
- Registrar inspeccion visual por etapa.

Pantallas:
- Welding Map por proyecto (plano + marcado).
- Welding List por proyecto (tabla + filtros).
- Detalle de soldadura con trazabilidad e inspeccion.

## Sprint 5: Reportes, exportaciones y dossier final

Entidades:
- Report (id, project_id, type, params_json, file_path)
- Dossier (id, project_id, config_json, file_path)

APIs:
- Reportes de avance y vencimientos.
- Exportacion a Excel.
- Generacion de dossier v1 en PDF.

Pantallas:
- Reportes y exportaciones.
- Configuracion y generacion de dossier final.
