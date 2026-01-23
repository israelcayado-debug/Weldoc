# Colas y workers (MVP + fase 3)

Define colas internas y workers para tareas async.

## Colas

- validation_queue: validaciones async (warnings).
- export_queue: exportaciones Excel/PDF.
- notification_queue: envio de correos/notificaciones.
- integration_queue: entrega de webhooks.

## Workers

- ValidationWorker: procesa validation_queue.
- ExportWorker: genera archivos y actualiza estado.
- NotificationWorker: envia emails e in_app.
- IntegrationWorker: entrega webhooks con reintentos.

## Politicas

- Retry exponencial para export y integrations.
- Idempotencia por job_id/event_id.
- Logs basicos por job y error.
