# Configuracion minima de despliegue

Define entornos, variables y backups.

## Entornos

- dev: base de datos local, colas en memoria.
- staging: replica de produccion con datos anonimizados.
- prod: alta disponibilidad.

## Variables de entorno

- DB_URL
- JWT_SECRET
- FILE_STORAGE_PATH
- EMAIL_PROVIDER_URL
- INTEGRATION_HMAC_SECRET
- QUEUE_PROVIDER_URL

## Backups

- BD: diario, retencion 30 dias.
- Archivos: semanal, retencion 90 dias.
