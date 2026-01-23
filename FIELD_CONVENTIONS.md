# Convenciones de nombres de campos (API y BD)

Objetivo: evitar ambiguedades entre archivos generales y reportes.

## Reglas

- `file_path`: archivos generales (documentos, planos, imports, exports).
- `report_path`: archivos de reportes/ensayos (NDE, PWHT, pressure tests).
- `signature_blob`: firma binaria.
- `*_json`: campos JSON en BD; en API se usa nombre simple sin sufijo
  cuando es mas legible (ej: `cycle_params` -> `cycle_params_json`).

## Ejemplos

- DocumentRevision.file_path (documentos).
- Drawing.file_path (planos).
- NdeResult.report_path (reportes END).
- PwhtRecord.report_path (reportes PWHT).
- PressureTest.report_path (reportes de presion).
- PqrResult.report_path (reportes de calificacion).
- WpqTest.report_path (reportes de calificacion).
