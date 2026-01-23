# Formato de geometria para WeldMark (MVP)

Se define un formato unificado para guardar marcas de soldadura en planos.
Se soportan dos tipos: bbox y poly.

## bbox

Caja delimitadora para una marca simple.
```json
{
  "type": "bbox",
  "x": 120,
  "y": 340,
  "w": 18,
  "h": 12
}
```

Reglas:
- x, y, w, h son numeros positivos.
- w y h mayores que 0.

## poly

Poligono para marcas irregulares.
```json
{
  "type": "poly",
  "points": [
    { "x": 10, "y": 10 },
    { "x": 20, "y": 10 },
    { "x": 20, "y": 20 }
  ]
}
```

Reglas:
- points contiene al menos 3 puntos.
- cada punto tiene x e y positivos.
