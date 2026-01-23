# Logica del job de alertas (MVP)

Define el proceso diario que genera notificaciones de continuidad y actualiza
ExpiryAlert.

## Pseudocodigo

```text
function runContinuityAlerts():
  targetDate = today() + 30 days
  candidates = WelderContinuityRepo.listByDueDate(targetDate)

  for each c in candidates:
    if c.status != 'in_continuity':
      continue

    lastAlert = ExpiryAlertRepo.getLastByWelder(c.welder_id)
    if lastAlert and daysBetween(lastAlert.sent_at, now()) < 7:
      continue

    projectAdmins = ProjectRepo.getAdminsByWelder(c.welder_id)
    supervisors = ProjectRepo.getSupervisorsByWelder(c.welder_id)

    recipients = unique(projectAdmins + supervisors)
    for each user in recipients:
      NotificationRepo.insert({
        project_id: user.project_id,
        recipient_id: user.id,
        channel: 'email',
        subject: formatSubject(c),
        body: formatBody(c, user.project_id),
        status: 'queued'
      })

    ExpiryAlertRepo.insert({
      welder_id: c.welder_id,
      wpq_id: latestApprovedWpqId(c.welder_id),
      due_date: c.continuity_due_date,
      sent_at: now()
    })
```

## Notas

- `listByDueDate` filtra por continuity_due_date = targetDate.
- `ProjectRepo.getAdminsByWelder` se resuelve por proyectos con actividad del
  soldador en los ultimos 6 meses.
- `latestApprovedWpqId` busca la ultima cualificacion aprobada del soldador.
