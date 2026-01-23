# Validaciones de negocio por modulo (MVP + fase 2)

## Proyectos
- No permitir cerrar proyecto con soldaduras abiertas.
- El codigo de proyecto debe ser unico.

## WPS/PQR
- No aprobar WPS sin PQR aprobado.
- No permitir borrar WPS si esta asignado a soldaduras.

## WPQ
- No asignar soldador sin WPQ aprobado.
- No aprobar WPQ si faltan ensayos requeridos.

## Welds
- No cerrar soldadura con inspeccion post_weld en fail.
- No permitir asignar WPS no aprobado.

## Documentos
- Una revision nueva supersede la anterior aprobada.
