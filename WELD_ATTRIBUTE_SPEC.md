# Atributos de soldadura (MVP)

El sistema usa un catalogo de atributos para normalizar los datos de cada
soldadura y permitir filtros consistentes en la Welding List.

## Catalogo minimo

- joint_type (enum): BW, FW, Fillet, Lap, Butt
- size (number): tamaño de cordon (mm o in)
- process (enum): SMAW, GTAW, GMAW, FCAW, SAW
- position (enum): 1G, 2G, 5G, 6G, PA, PB, PC, PF
- material_pno (text): P-Number (ASME)
- material_group (text): Grupo ISO

## Reglas de validacion

- Atributos enum deben existir en el catalogo.
- Atributos number deben venir con unidad compatible con el proyecto.
- Atributos text aceptan cualquier valor no vacio.

## Mapeo a WeldAttribute

WeldAttribute:
- name: codigo del atributo (ej: joint_type)
- value: valor normalizado (ej: BW)

WeldAttributeCatalog:
- code: codigo unico (joint_type)
- name: nombre visible ("Tipo de junta")
- data_type: text/number/enum
- unit: mm/in (si aplica)
