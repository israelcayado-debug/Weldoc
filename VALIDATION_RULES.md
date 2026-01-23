# Reglas de validacion minimas por norma (MVP)

Este documento define un set minimo de validaciones para WPS/PQR y WPQ/WQTR.
No sustituye los codigos, pero evita combinaciones claramente invalidas.

## ASME IX (WPS/PQR)

Variables esenciales (ejemplos de control):
- Proceso de soldeo: cambios de proceso requieren nuevo PQR.
- Tipo de junta y posicion: cambios fuera del rango aprobado invalidan.
- Material base: cambio de P-Number requiere nuevo PQR.
- Metal de aporte: cambio de F-Number requiere nuevo PQR.
- Espesor: rango de aprobacion depende del espesor ensayado.

Validaciones MVP:
- No permitir WPS sin PQR aprobado asociado (si el estado es "approved").
- Forzar que WPS.standard == PQR.standard.
- Forzar que WPS.material_base_pno == PQR.material_base_pno.
- Forzar que WPS.filler_fno == PQR.filler_fno.
- Forzar que WPS.processes sea subconjunto de PQR.processes.
- Validar rango de espesor: WPS.thickness_range dentro del rango del PQR.
- Validar posicion: WPS.position dentro del rango aprobado.

## ISO 15614-1 (WPS/PQR)

Variables esenciales (ejemplos de control):
- Grupo de material (material group).
- Proceso de soldeo.
- Espesor y diametro (si aplica tuberia).
- Tipo de junta y posicion.

Validaciones MVP:
- No permitir WPS aprobado sin PQR aprobado asociado.
- Forzar que WPS.standard == PQR.standard.
- Forzar que material group coincida entre WPS y PQR.
- Validar rango de espesor y diametro segun PQR.
- Validar posicion dentro del rango aprobado.

## ASME IX (WPQ/WQTR)

Variables esenciales (ejemplos de control):
- Proceso de soldeo.
- Tipo de junta y posicion.
- Espesor o diametro de prueba.

Validaciones MVP:
- WPQ.standard debe ser ASME_IX.
- WPQ.processes no puede estar vacio.
- Validar rango de espesor/diametro segun prueba.
- Validar posiciones segun prueba.

## ISO 9606-1 / 9606-4 (WPQ/WQTR)

Variables esenciales (ejemplos de control):
- Proceso de soldeo.
- Rango de espesor y diametro.
- Posicion de soldeo.
- Tipo de material (segun 9606-1 o 9606-4).

Validaciones MVP:
- WPQ.standard debe ser ISO_9606_1 o ISO_9606_4.
- WPQ.processes no puede estar vacio.
- Validar rango de espesor y diametro segun prueba.
- Validar posiciones segun prueba.

## Reglas de continuidad (minimas)

- Si no hay continuidad registrada en 6 meses, marcar como "fuera de continuidad".
- Generar alerta 30 dias antes del vencimiento.
- Bloquear asignacion de soldador fuera de continuidad.
