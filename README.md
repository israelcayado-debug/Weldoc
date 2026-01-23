# WeldDoc

Plataforma para gestion de soldadura (WPS/PQR, WPQ, proyectos, mapas de soldadura, reportes).

## Arranque rapido (desarrollo)

1) Crear entorno virtual e instalar dependencias.
2) Aplicar migraciones y arrancar servidor.

Ejemplo:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
python backend\manage.py migrate
python backend\manage.py runserver 0.0.0.0:8002
```

Si prefieres, usa el script:

```
backend\run_dev.bat
```

## Variables de entorno

Valores opcionales (defaults en settings):

```
DJANGO_SECRET_KEY=dev-only-change-me
DJANGO_SETTINGS_MODULE=config.settings.dev
```

Puedes copiar `.env.example` y ajustar lo necesario.

## Estructura

- `backend/`: Django + API.
- `infra/`: notas de despliegue.
- `docs` en raiz: especificaciones y roadmap.
