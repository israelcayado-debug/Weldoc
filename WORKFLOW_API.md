# API de workflow (WPS/WPQ/PQR)

Endpoints y reglas de transicion para aprobaciones.

## Estados

- draft
- in_review
- approved
- archived

## Endpoints

POST /api/wps/{id}/submit-review
POST /api/wps/{id}/approve
POST /api/wps/{id}/archive

POST /api/pqr/{id}/submit-review
POST /api/pqr/{id}/approve
POST /api/pqr/{id}/archive

POST /api/wpq/{id}/submit-review
POST /api/wpq/{id}/approve
POST /api/wpq/{id}/archive

## Reglas

- submit-review: solo desde draft.
- approve: solo desde in_review y con validaciones en OK.
- archive: desde cualquier estado.
