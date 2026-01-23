# Carga masiva (fase 2)

Define plantillas y mapeo para importacion de datos.

## Plantillas

- WPS/PQR: columnas clave (code, standard, material_pno, processes, thickness_range)
- WPQ: columnas clave (welder, standard, process, positions, thickness_range)
- Welds: columnas (number, drawing, joint_type, size, status)

## Flujo

1. Usuario descarga plantilla.
2. Completa y sube Excel.
3. Sistema mapea columnas y valida.
4. Se ejecuta importacion y se reportan errores fila a fila.
