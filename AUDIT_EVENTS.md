# Auditoria detallada (fase 2)

Eventos sugeridos:

- user.login, user.logout
- project.create, project.update
- wps.create, wps.update, wps.approve
- pqr.create, pqr.update, pqr.approve
- wpq.create, wpq.update, wpq.approve
- weld.create, weld.update, weld.close
- document.upload, document.revision
- report.export

Payload sugerido:
- entity_id
- user_id
- at
- diff_json
