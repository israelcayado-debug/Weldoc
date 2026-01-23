# Mapeo de variables para reglas (MVP)

Este documento define como se transforma la informacion almacenada en
WpsVariable, PqrResult y WpqProcess a un objeto normalizado que consumen las
reglas. El objetivo es evitar reglas acopladas a estructuras internas.

## WPS / PQR (ASME IX + ISO 15614-1)

Fuente:
- WpsVariable (name, value, unit)
- PqrResult (test_type, result)
- Wps/Pqr (standard, status)

Objeto normalizado `wps`:
- status: Wps.status
- standard: Wps.standard
- material_pno: WpsVariable[name=material_pno].value
- filler_fno: WpsVariable[name=filler_fno].value
- processes: WpsVariable[name=processes].value (CSV -> array)
- position: WpsVariable[name=position].value
- thickness_range: WpsVariable[name=thickness_range].value (ej: "3-12")
- product_form: WpsVariable[name=product_form].value (plate/pipe)
- diameter_range: WpsVariable[name=diameter_range].value
- material_group: WpsVariable[name=material_group].value

Objeto normalizado `pqr`:
- status: Pqr.status
- standard: Pqr.standard
- material_pno: PqrResult[test_type=material_pno].result
- filler_fno: PqrResult[test_type=filler_fno].result
- processes: PqrResult[test_type=processes].result (CSV -> array)
- position: PqrResult[test_type=position].result
- thickness_qualified_range: PqrResult[test_type=thickness_range].result
- diameter_qualified_range: PqrResult[test_type=diameter_range].result
- material_group: PqrResult[test_type=material_group].result

## WPQ / WQTR (ASME IX + ISO 9606-1/4)

Fuente:
- WpqProcess (process, positions, thickness_range)
- WpqTest (test_type, result)
- Wpq (standard, status)

Objeto normalizado `wpq`:
- status: Wpq.status
- standard: Wpq.standard
- processes: WpqProcess.process (array)
- positions: WpqProcess.positions (CSV -> array)
- thickness_range: WpqProcess.thickness_range
- test_thickness_range: WpqTest[test_type=thickness_range].result
- position: WpqTest[test_type=position].result

## Reglas de transformacion (MVP)

- CSV -> array: split por coma, trim y uppercase.
- Rango numerico: "a-b" se parsea a { min, max }.
- Unidades: si existe unit, normalizar a mm en MVP.
- Campos inexistentes retornan null.
