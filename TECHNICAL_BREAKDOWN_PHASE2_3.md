# Desglose tecnico por sprint (fase 2 y 3)

Entrega tecnica por sprint para fases posteriores al MVP.

## Sprint 6: Documentos avanzados + auditoria

Entidades:
- DocumentApproval (document_revision_id, approver_id, status, signed_at)
- DocumentSignature (document_revision_id, signer_id, signature_blob, signed_at)
- AuditEvent (id, event_code, entity, entity_id, user_id, at, payload_json)

APIs:
- POST /api/documents/{id}/submit-review
- POST /api/documents/{id}/approve
- POST /api/documents/{id}/sign
- GET /api/audit/events

Pantallas:
- Repositorio con estados y aprobaciones.
- Historial de auditoria.

## Sprint 7: END / PWHT / Pruebas de presion

Entidades:
- NdeRequest, NdeResult
- PwhtRecord
- PressureTest

APIs:
- END: requests, results
- PWHT: create, update, list
- Pressure tests: create, update, list

Pantallas:
- Solicitudes y resultados de END.
- Registro de PWHT.
- Pruebas de presion por linea/sistema.

## Sprint 8: Carga masiva + reportes avanzados

Entidades:
- ImportJob (id, type, status, created_by, file_path)
- ImportError (job_id, row_number, message)

APIs:
- POST /api/imports
- GET /api/imports/{id}
- GET /api/reports/productivity
- GET /api/reports/yield

Pantallas:
- Carga masiva con preview de errores.
- Reportes avanzados.

## Sprint 9: Numeracion configurable + integraciones

Entidades:
- NumberingRule (project_id, type, pattern, next_seq)
- IntegrationEndpoint (name, url, status, auth_json)

APIs:
- CRUD numbering rules.
- Webhooks basicos (export WPS/WPQ/Welds).

Pantallas:
- Configuracion de numeracion.
- Configuracion de integraciones.

## Sprint 10: Calidad avanzada

Entidades:
- NdeSamplingRule (project_id, method, ratio, penalty_json)
- WorkPack (project_id, code, status)
- Traveler (work_pack_id, file_path, status)

APIs:
- CRUD sampling rules.
- CRUD work packs y travelers.
- QR labels endpoint.

Pantallas:
- Configuracion de muestreo END.
- Work packs y travelers.
