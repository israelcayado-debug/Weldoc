# Matriz de permisos por modulo (MVP)

Roles base:
- Admin
- Supervisor
- Inspector
- Soldador

Permisos por modulo:
- Users: Admin (R/W), Supervisor (R), Inspector (-), Soldador (-)
- Projects: Admin (R/W), Supervisor (R/W), Inspector (R), Soldador (R)
- WPS/PQR: Admin (R/W), Supervisor (R), Inspector (R), Soldador (R)
- WPQ/WQTR: Admin (R/W), Supervisor (R), Inspector (R), Soldador (R)
- WeldMap/List: Admin (R/W), Supervisor (R/W), Inspector (R), Soldador (R)
- Inspections: Admin (R/W), Supervisor (R/W), Inspector (R/W), Soldador (R)
- Reports/Exports: Admin (R/W), Supervisor (R), Inspector (R), Soldador (-)
- Document Repo: Admin (R/W), Supervisor (R/W), Inspector (R), Soldador (R)

Notas:
- R/W: leer y escribir.
- R: solo lectura.
- "-": sin acceso.
