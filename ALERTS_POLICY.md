# Politica de alertas de continuidad (MVP)

Define el job, destinatarios y reglas para alertas de continuidad.

## Job

- Frecuencia: diario a las 06:00 hora local del proyecto.
- Entrada: lista de soldadores con continuity_due_date en 30 dias.
- Salida: notificaciones y registro en ExpiryAlert.

## Destinatarios

- Admin del proyecto.
- Supervisor asignado al proyecto.
- Opcional: correo del soldador si esta registrado.

## Reglas de envio

- Crear alerta cuando faltan 30 dias para vencer.
- Reenviar cada 7 dias si sigue en riesgo.
- Si el soldador vuelve a continuidad, detener reenvios.

## Plantilla sugerida

Asunto:
- "Alerta de continuidad: {welder_name} vence el {due_date}"

Cuerpo:
- Proyecto: {project_name}
- Soldador: {welder_name}
- Ultima actividad: {last_activity_date}
- Fecha limite: {due_date}
