# Gestion documental avanzada (fase 2)

Define flujo de revisiones, aprobaciones y firmas.

## Estados de documento

- draft
- in_review
- approved
- superseded
- archived

## Flujo

- draft -> in_review -> approved
- approved -> superseded (cuando se publica revision nueva)
- cualquier estado -> archived

## Reglas

- Solo una revision aprobada activa por documento.
- Una revision nueva inicia en draft (estado en DocumentRevision).
- Aprobacion requiere firma digital o aprobador asignado.

## Entidades adicionales

- DocumentApproval (document_revision_id, approver_id, status, signed_at)
- DocumentSignature (document_revision_id, signer_id, signature_blob, signed_at)
- DocumentRevision.status almacena el workflow.

## Endpoints sugeridos

- POST /api/documents/{id}/submit-review
- POST /api/documents/{id}/approve
- POST /api/documents/{id}/sign
