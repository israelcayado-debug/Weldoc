# Numeracion configurable (fase 2)

Define como personalizar prefijos por cliente/proyecto.

## Configuracion

- project.numbering.wps_prefix (default: WPS-{ProjectCode}-)
- project.numbering.pqr_prefix (default: PQR-{ProjectCode}-)
- project.numbering.wpq_prefix (default: WPQ-{WelderIdShort}-)
- project.numbering.weld_prefix (default: WELD-{ProjectCode}-)

## Reglas

- Variables permitidas: {ProjectCode}, {Year}, {Seq3}, {Seq4}, {WelderIdShort}
- Secuencias independientes por tipo.
