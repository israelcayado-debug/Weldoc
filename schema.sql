-- PostgreSQL schema for MVP (ASME IX + ISO 15614-1 / ISO 9606-1/4)
-- Naming: PascalCase tables, snake_case columns, UUID PKs.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE "SchemaVersion" (
  version integer PRIMARY KEY,
  name varchar(200) NOT NULL,
  applied_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE "User" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  name varchar(200) NOT NULL,
  email varchar(320) NOT NULL UNIQUE,
  status varchar(30) NOT NULL DEFAULT 'active',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE "Role" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  name varchar(200) NOT NULL UNIQUE,
  scope varchar(30) NOT NULL DEFAULT 'global'
);

CREATE TABLE "Permission" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  code varchar(100) NOT NULL UNIQUE,
  description text
);

CREATE TABLE "UserRole" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL REFERENCES "User"(id),
  role_id uuid NOT NULL REFERENCES "Role"(id),
  UNIQUE (user_id, role_id)
);

CREATE TABLE "RolePermission" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  role_id uuid NOT NULL REFERENCES "Role"(id),
  permission_id uuid NOT NULL REFERENCES "Permission"(id),
  UNIQUE (role_id, permission_id)
);

CREATE TABLE "Client" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  name varchar(200) NOT NULL,
  tax_id varchar(50),
  status varchar(30) NOT NULL DEFAULT 'active'
);

CREATE TABLE "Project" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  client_id uuid REFERENCES "Client"(id),
  name varchar(200) NOT NULL,
  code varchar(100) NOT NULL UNIQUE,
  units varchar(20) NOT NULL DEFAULT 'metric',
  status varchar(30) NOT NULL DEFAULT 'active',
  standard_set varchar(30)[] NOT NULL DEFAULT ARRAY['ASME_IX']
);

CREATE TABLE "ProjectUser" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid NOT NULL REFERENCES "Project"(id),
  user_id uuid NOT NULL REFERENCES "User"(id),
  role_id uuid NOT NULL REFERENCES "Role"(id),
  UNIQUE (project_id, user_id, role_id)
);

CREATE TABLE "AuditLog" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  entity varchar(50) NOT NULL,
  entity_id uuid NOT NULL,
  action varchar(50) NOT NULL,
  user_id uuid NOT NULL REFERENCES "User"(id),
  at timestamptz NOT NULL DEFAULT now(),
  diff_json jsonb
);

CREATE TABLE "Document" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid NOT NULL REFERENCES "Project"(id),
  type varchar(50) NOT NULL,
  title varchar(200) NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'active'
);

CREATE TABLE "DocumentRevision" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  document_id uuid NOT NULL REFERENCES "Document"(id),
  revision varchar(20) NOT NULL,
  file_path varchar(512) NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'draft',
  created_by uuid REFERENCES "User"(id),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE "MaterialBase" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  spec varchar(100) NOT NULL,
  grade varchar(100),
  group_no varchar(50)
);

CREATE TABLE "FillerMaterial" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  spec varchar(100) NOT NULL,
  classification varchar(100),
  group_no varchar(50)
);

CREATE TABLE "JointType" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  code varchar(100) NOT NULL UNIQUE,
  geometry_json jsonb
);

CREATE TABLE "Wps" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid REFERENCES "Project"(id),
  code varchar(100) NOT NULL,
  standard varchar(30) NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'draft'
);

CREATE UNIQUE INDEX wps_project_code_unique
  ON "Wps"(project_id, code);

CREATE TABLE "Pqr" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid REFERENCES "Project"(id),
  code varchar(100) NOT NULL,
  standard varchar(30) NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'draft'
);

CREATE UNIQUE INDEX pqr_project_code_unique
  ON "Pqr"(project_id, code);

CREATE TABLE "WpsPqrLink" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  wps_id uuid NOT NULL REFERENCES "Wps"(id),
  pqr_id uuid NOT NULL REFERENCES "Pqr"(id),
  UNIQUE (wps_id, pqr_id)
);

CREATE TABLE "WpsVariable" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  wps_id uuid NOT NULL REFERENCES "Wps"(id),
  name varchar(200) NOT NULL,
  value text NOT NULL,
  unit varchar(20)
);

CREATE TABLE "PqrResult" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  pqr_id uuid NOT NULL REFERENCES "Pqr"(id),
  test_type varchar(50) NOT NULL,
  result varchar(20) NOT NULL,
  report_path varchar(512)
);

CREATE TABLE "Welder" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  name varchar(200) NOT NULL,
  employer varchar(200),
  status varchar(30) NOT NULL DEFAULT 'active'
);

CREATE TABLE "Wpq" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  welder_id uuid NOT NULL REFERENCES "Welder"(id),
  code varchar(100) NOT NULL,
  standard varchar(30) NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'draft'
);

CREATE UNIQUE INDEX wpq_welder_code_unique
  ON "Wpq"(welder_id, code);

CREATE TABLE "WpqProcess" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  wpq_id uuid NOT NULL REFERENCES "Wpq"(id),
  process varchar(30) NOT NULL,
  positions varchar(100),
  thickness_range varchar(50)
);

CREATE TABLE "WpqTest" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  wpq_id uuid NOT NULL REFERENCES "Wpq"(id),
  test_type varchar(50) NOT NULL,
  result varchar(20) NOT NULL,
  report_path varchar(512)
);

CREATE TABLE "Drawing" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid NOT NULL REFERENCES "Project"(id),
  code varchar(100) NOT NULL,
  revision varchar(20) NOT NULL,
  file_path varchar(512) NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'active'
);

CREATE UNIQUE INDEX drawing_project_code_rev_unique
  ON "Drawing"(project_id, code, revision);

CREATE TABLE "WeldMap" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid NOT NULL REFERENCES "Project"(id),
  drawing_id uuid NOT NULL REFERENCES "Drawing"(id),
  status varchar(30) NOT NULL DEFAULT 'active'
);

CREATE TABLE "WeldMark" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  weld_map_id uuid NOT NULL REFERENCES "WeldMap"(id),
  weld_id uuid NOT NULL REFERENCES "Weld"(id),
  geometry jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE "Weld" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid NOT NULL REFERENCES "Project"(id),
  drawing_id uuid REFERENCES "Drawing"(id),
  number varchar(100) NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'planned',
  closed_at timestamptz
);

CREATE TABLE "WeldWpsAssignment" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  weld_id uuid NOT NULL REFERENCES "Weld"(id),
  wps_id uuid NOT NULL REFERENCES "Wps"(id),
  assigned_at timestamptz NOT NULL DEFAULT now(),
  assigned_by uuid REFERENCES "User"(id),
  status varchar(30) NOT NULL DEFAULT 'active'
);

CREATE TABLE "WeldWelderAssignment" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  weld_id uuid NOT NULL REFERENCES "Weld"(id),
  welder_id uuid NOT NULL REFERENCES "Welder"(id),
  assigned_at timestamptz NOT NULL DEFAULT now(),
  assigned_by uuid REFERENCES "User"(id),
  status varchar(30) NOT NULL DEFAULT 'active'
);

CREATE UNIQUE INDEX weld_project_number_unique
  ON "Weld"(project_id, number);

CREATE TABLE "WeldAttribute" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  weld_id uuid NOT NULL REFERENCES "Weld"(id),
  name varchar(200) NOT NULL,
  value text NOT NULL
);

CREATE TABLE "WeldAttributeCatalog" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  code varchar(100) NOT NULL UNIQUE,
  name varchar(200) NOT NULL,
  data_type varchar(20) NOT NULL DEFAULT 'text',
  enum_values jsonb,
  unit varchar(20),
  status varchar(30) NOT NULL DEFAULT 'active'
);

CREATE TABLE "WeldMaterial" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  weld_id uuid NOT NULL REFERENCES "Weld"(id),
  material_id uuid NOT NULL REFERENCES "MaterialBase"(id),
  heat_number varchar(50) NOT NULL
);

CREATE TABLE "WeldConsumable" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  weld_id uuid NOT NULL REFERENCES "Weld"(id),
  consumable_id uuid NOT NULL REFERENCES "FillerMaterial"(id),
  batch varchar(50)
);

CREATE TABLE "VisualInspection" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  weld_id uuid NOT NULL REFERENCES "Weld"(id),
  stage varchar(20) NOT NULL,
  result varchar(20) NOT NULL,
  notes text,
  inspector_id uuid REFERENCES "User"(id),
  at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE "ContinuityLog" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  welder_id uuid NOT NULL REFERENCES "Welder"(id),
  weld_id uuid REFERENCES "Weld"(id),
  date date NOT NULL,
  process varchar(30) NOT NULL
);

CREATE TABLE "ExpiryAlert" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  welder_id uuid NOT NULL REFERENCES "Welder"(id),
  wpq_id uuid NOT NULL REFERENCES "Wpq"(id),
  due_date date NOT NULL,
  sent_at timestamptz
);

CREATE TABLE "WelderContinuity" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  welder_id uuid NOT NULL REFERENCES "Welder"(id),
  last_activity_date date,
  continuity_due_date date,
  status varchar(30) NOT NULL DEFAULT 'in_continuity',
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE "Notification" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid REFERENCES "Project"(id),
  recipient_id uuid REFERENCES "User"(id),
  channel varchar(20) NOT NULL DEFAULT 'email',
  subject varchar(200) NOT NULL,
  body text NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'queued',
  sent_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE "DocumentApproval" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  document_revision_id uuid NOT NULL REFERENCES "DocumentRevision"(id),
  approver_id uuid NOT NULL REFERENCES "User"(id),
  status varchar(30) NOT NULL DEFAULT 'pending',
  signed_at timestamptz
);

CREATE TABLE "DocumentSignature" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  document_revision_id uuid NOT NULL REFERENCES "DocumentRevision"(id),
  signer_id uuid NOT NULL REFERENCES "User"(id),
  signature_blob bytea NOT NULL,
  signed_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE "AuditEvent" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_code varchar(100) NOT NULL,
  entity varchar(50) NOT NULL,
  entity_id uuid NOT NULL,
  user_id uuid NOT NULL REFERENCES "User"(id),
  at timestamptz NOT NULL DEFAULT now(),
  payload_json jsonb
);

CREATE TABLE "NdeRequest" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid NOT NULL REFERENCES "Project"(id),
  weld_id uuid REFERENCES "Weld"(id),
  method varchar(10) NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'requested',
  requested_by uuid REFERENCES "User"(id),
  requested_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE "NdeResult" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  nde_request_id uuid NOT NULL REFERENCES "NdeRequest"(id),
  result varchar(20) NOT NULL,
  defect_type varchar(50),
  report_path varchar(512),
  inspector_id uuid REFERENCES "User"(id)
);

CREATE TABLE "PwhtRecord" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  weld_id uuid NOT NULL REFERENCES "Weld"(id),
  cycle_params_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  result varchar(20) NOT NULL,
  report_path varchar(512)
);

CREATE TABLE "PressureTest" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid NOT NULL REFERENCES "Project"(id),
  line_id varchar(100) NOT NULL,
  test_type varchar(50) NOT NULL,
  pressure numeric,
  duration_min integer,
  result varchar(20) NOT NULL,
  report_path varchar(512)
);

CREATE TABLE "ImportJob" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  type varchar(50) NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'queued',
  created_by uuid REFERENCES "User"(id),
  file_path varchar(512) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE "ImportError" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  job_id uuid NOT NULL REFERENCES "ImportJob"(id),
  row_number integer NOT NULL,
  message text NOT NULL
);

CREATE TABLE "NumberingRule" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid NOT NULL REFERENCES "Project"(id),
  type varchar(50) NOT NULL,
  pattern varchar(200) NOT NULL,
  next_seq integer NOT NULL DEFAULT 1
);

CREATE TABLE "IntegrationEndpoint" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  name varchar(200) NOT NULL,
  url varchar(2048) NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'active',
  auth_json jsonb
);

CREATE TABLE "IntegrationEvent" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  integration_id uuid NOT NULL REFERENCES "IntegrationEndpoint"(id),
  event_type varchar(100) NOT NULL,
  payload_json jsonb NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'queued',
  attempts integer NOT NULL DEFAULT 0,
  last_error text,
  created_at timestamptz NOT NULL DEFAULT now(),
  delivered_at timestamptz
);

CREATE TABLE "NdeSamplingRule" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid NOT NULL REFERENCES "Project"(id),
  method varchar(10) NOT NULL,
  ratio numeric NOT NULL,
  penalty_json jsonb
);

CREATE TABLE "WorkPack" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid NOT NULL REFERENCES "Project"(id),
  code varchar(100) NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'open'
);

CREATE TABLE "Traveler" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  work_pack_id uuid NOT NULL REFERENCES "WorkPack"(id),
  file_path varchar(512),
  status varchar(30) NOT NULL DEFAULT 'draft'
);

CREATE TABLE "Report" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid NOT NULL REFERENCES "Project"(id),
  type varchar(50) NOT NULL,
  params_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  file_path varchar(512)
);

CREATE TABLE "Dossier" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid NOT NULL REFERENCES "Project"(id),
  config_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  file_path varchar(512)
);

CREATE TABLE "ValidationRuleSet" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  code varchar(100) NOT NULL UNIQUE,
  name varchar(200) NOT NULL,
  applies_to varchar(10) NOT NULL,
  standard varchar(30) NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'active'
);

CREATE TABLE "ValidationRule" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  code varchar(100) NOT NULL UNIQUE,
  name varchar(200) NOT NULL,
  applies_to varchar(10) NOT NULL,
  severity varchar(20) NOT NULL DEFAULT 'error',
  rule_json jsonb NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'active'
);

CREATE TABLE "ValidationRuleSetItem" (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  ruleset_id uuid NOT NULL REFERENCES "ValidationRuleSet"(id),
  rule_id uuid NOT NULL REFERENCES "ValidationRule"(id),
  sort_order integer NOT NULL DEFAULT 0,
  UNIQUE (ruleset_id, rule_id)
);

ALTER TABLE "User"
  ADD CONSTRAINT user_status_check
  CHECK (status IN ('active', 'inactive'));

ALTER TABLE "Role"
  ADD CONSTRAINT role_scope_check
  CHECK (scope IN ('global', 'project'));

ALTER TABLE "Client"
  ADD CONSTRAINT client_status_check
  CHECK (status IN ('active', 'inactive'));

ALTER TABLE "Project"
  ADD CONSTRAINT project_units_check
  CHECK (units IN ('metric', 'imperial')),
  ADD CONSTRAINT project_status_check
  CHECK (status IN ('active', 'closed', 'archived')),
  ADD CONSTRAINT project_standard_set_check
  CHECK (standard_set <@ ARRAY['ASME_IX', 'ISO_15614_1', 'ISO_9606_1', 'ISO_9606_4']);

ALTER TABLE "Document"
  ADD CONSTRAINT document_status_check
  CHECK (status IN ('active', 'archived'));

ALTER TABLE "DocumentRevision"
  ADD CONSTRAINT documentrevision_status_check
  CHECK (status IN ('draft', 'in_review', 'approved', 'superseded', 'archived'));

ALTER TABLE "Wps"
  ADD CONSTRAINT wps_status_check
  CHECK (status IN ('draft', 'in_review', 'approved', 'archived')),
  ADD CONSTRAINT wps_standard_check
  CHECK (standard IN ('ASME_IX', 'ISO_15614_1'));

ALTER TABLE "Pqr"
  ADD CONSTRAINT pqr_status_check
  CHECK (status IN ('draft', 'in_review', 'approved', 'archived')),
  ADD CONSTRAINT pqr_standard_check
  CHECK (standard IN ('ASME_IX', 'ISO_15614_1'));

ALTER TABLE "Wpq"
  ADD CONSTRAINT wpq_status_check
  CHECK (status IN ('draft', 'in_review', 'approved', 'archived')),
  ADD CONSTRAINT wpq_standard_check
  CHECK (standard IN ('ASME_IX', 'ISO_9606_1', 'ISO_9606_4'));

ALTER TABLE "WeldMap"
  ADD CONSTRAINT weldmap_status_check
  CHECK (status IN ('active', 'archived'));

ALTER TABLE "Drawing"
  ADD CONSTRAINT drawing_status_check
  CHECK (status IN ('active', 'archived'));

ALTER TABLE "Weld"
  ADD CONSTRAINT weld_status_check
  CHECK (status IN ('planned', 'in_progress', 'completed', 'repair'));

ALTER TABLE "WeldWpsAssignment"
  ADD CONSTRAINT weldwpsassignment_status_check
  CHECK (status IN ('active', 'removed'));

ALTER TABLE "WeldWelderAssignment"
  ADD CONSTRAINT weldwelderassignment_status_check
  CHECK (status IN ('active', 'removed'));

ALTER TABLE "VisualInspection"
  ADD CONSTRAINT visualinspection_stage_check
  CHECK (stage IN ('fit_up', 'during_weld', 'post_weld')),
  ADD CONSTRAINT visualinspection_result_check
  CHECK (result IN ('pass', 'fail', 'repair'));

ALTER TABLE "Report"
  ADD CONSTRAINT report_type_check
  CHECK (type IN ('progress', 'expiry'));

ALTER TABLE "WeldMap"
  ADD CONSTRAINT weldmap_project_drawing_unique
  UNIQUE (project_id, drawing_id);

ALTER TABLE "WeldAttributeCatalog"
  ADD CONSTRAINT weldattributecatalog_data_type_check
  CHECK (data_type IN ('text', 'number', 'enum')),
  ADD CONSTRAINT weldattributecatalog_enum_values_check
  CHECK (
    data_type != 'enum'
    OR (enum_values IS NOT NULL AND jsonb_typeof(enum_values) = 'array')
  ),
  ADD CONSTRAINT weldattributecatalog_status_check
  CHECK (status IN ('active', 'inactive'));

ALTER TABLE "WelderContinuity"
  ADD CONSTRAINT weldercontinuity_status_check
  CHECK (status IN ('in_continuity', 'out_of_continuity'));

ALTER TABLE "Notification"
  ADD CONSTRAINT notification_channel_check
  CHECK (channel IN ('email', 'in_app')),
  ADD CONSTRAINT notification_status_check
  CHECK (status IN ('queued', 'sent', 'failed'));

ALTER TABLE "DocumentApproval"
  ADD CONSTRAINT documentapproval_status_check
  CHECK (status IN ('pending', 'approved', 'rejected'));

ALTER TABLE "NdeRequest"
  ADD CONSTRAINT nderequest_status_check
  CHECK (status IN ('requested', 'scheduled', 'completed')),
  ADD CONSTRAINT nderequest_method_check
  CHECK (method IN ('RT', 'UT', 'MT', 'PT', 'VT'));

ALTER TABLE "NdeResult"
  ADD CONSTRAINT nderesult_result_check
  CHECK (result IN ('pass', 'fail', 'repair'));

ALTER TABLE "PwhtRecord"
  ADD CONSTRAINT pwhtrecord_result_check
  CHECK (result IN ('pass', 'fail'));

ALTER TABLE "PressureTest"
  ADD CONSTRAINT pressuretest_result_check
  CHECK (result IN ('pass', 'fail')),
  ADD CONSTRAINT pressuretest_type_check
  CHECK (test_type IN ('hydro', 'pneumatic'));

ALTER TABLE "ImportJob"
  ADD CONSTRAINT importjob_status_check
  CHECK (status IN ('queued', 'running', 'completed', 'failed')),
  ADD CONSTRAINT importjob_type_check
  CHECK (type IN ('WPS', 'PQR', 'WPQ', 'WELD'));

ALTER TABLE "NumberingRule"
  ADD CONSTRAINT numberingrule_type_check
  CHECK (type IN ('WPS', 'PQR', 'WPQ', 'WELD', 'DRAWING'));

ALTER TABLE "IntegrationEndpoint"
  ADD CONSTRAINT integrationendpoint_status_check
  CHECK (status IN ('active', 'inactive'));

ALTER TABLE "IntegrationEvent"
  ADD CONSTRAINT integrationevent_status_check
  CHECK (status IN ('queued', 'sent', 'failed'));

ALTER TABLE "WorkPack"
  ADD CONSTRAINT workpack_status_check
  CHECK (status IN ('open', 'in_progress', 'closed'));

ALTER TABLE "Traveler"
  ADD CONSTRAINT traveler_status_check
  CHECK (status IN ('draft', 'issued', 'closed'));

ALTER TABLE "WeldMark"
  ADD CONSTRAINT weldmark_geometry_check
  CHECK (
    jsonb_typeof(geometry) = 'object'
    AND geometry ? 'type'
    AND (geometry->>'type') IN ('bbox', 'poly')
  );

ALTER TABLE "ValidationRuleSet"
  ADD CONSTRAINT validationruleset_applies_to_check
  CHECK (applies_to IN ('WPS', 'PQR', 'WPQ')),
  ADD CONSTRAINT validationruleset_standard_check
  CHECK (standard IN ('ASME_IX', 'ISO_15614_1', 'ISO_9606_1', 'ISO_9606_4')),
  ADD CONSTRAINT validationruleset_status_check
  CHECK (status IN ('active', 'inactive'));

ALTER TABLE "ValidationRule"
  ADD CONSTRAINT validationrule_applies_to_check
  CHECK (applies_to IN ('WPS', 'PQR', 'WPQ')),
  ADD CONSTRAINT validationrule_severity_check
  CHECK (severity IN ('error', 'warning', 'info')),
  ADD CONSTRAINT validationrule_status_check
  CHECK (status IN ('active', 'inactive'));

CREATE INDEX project_status_idx ON "Project"(status);
CREATE INDEX project_client_idx ON "Project"(client_id);

CREATE INDEX document_project_idx ON "Document"(project_id);
CREATE INDEX document_type_idx ON "Document"(type);

CREATE INDEX wps_project_idx ON "Wps"(project_id);
CREATE INDEX wps_standard_idx ON "Wps"(standard);
CREATE INDEX pqr_project_idx ON "Pqr"(project_id);
CREATE INDEX pqr_standard_idx ON "Pqr"(standard);

CREATE INDEX wpq_welder_idx ON "Wpq"(welder_id);
CREATE INDEX wpq_standard_idx ON "Wpq"(standard);

CREATE INDEX drawing_project_idx ON "Drawing"(project_id);
CREATE INDEX weld_project_status_idx ON "Weld"(project_id, status);
CREATE INDEX weld_drawing_idx ON "Weld"(drawing_id);

CREATE INDEX weldwpsassignment_weld_idx ON "WeldWpsAssignment"(weld_id);
CREATE INDEX weldwpsassignment_wps_idx ON "WeldWpsAssignment"(wps_id);
CREATE INDEX weldwelderassignment_weld_idx ON "WeldWelderAssignment"(weld_id);
CREATE INDEX weldwelderassignment_welder_idx ON "WeldWelderAssignment"(welder_id);

CREATE UNIQUE INDEX weldercontinuity_welder_unique
  ON "WelderContinuity"(welder_id);

CREATE INDEX notification_project_idx ON "Notification"(project_id);
CREATE INDEX notification_recipient_idx ON "Notification"(recipient_id);

CREATE INDEX documentapproval_revision_idx ON "DocumentApproval"(document_revision_id);
CREATE INDEX audit_event_code_idx ON "AuditEvent"(event_code);
CREATE INDEX nderequest_project_idx ON "NdeRequest"(project_id);
CREATE INDEX nderequest_weld_idx ON "NdeRequest"(weld_id);
CREATE INDEX importjob_status_idx ON "ImportJob"(status);
CREATE INDEX numberingrule_project_idx ON "NumberingRule"(project_id);
CREATE INDEX workpack_project_idx ON "WorkPack"(project_id);

CREATE INDEX integrationevent_status_idx ON "IntegrationEvent"(status);
CREATE INDEX integrationevent_integration_idx ON "IntegrationEvent"(integration_id);

CREATE INDEX weldmark_weldmap_idx ON "WeldMark"(weld_map_id);

CREATE INDEX weldattribute_weld_idx ON "WeldAttribute"(weld_id);

CREATE INDEX visualinspection_weld_stage_idx
  ON "VisualInspection"(weld_id, stage);

CREATE INDEX continuitylog_welder_date_idx
  ON "ContinuityLog"(welder_id, date);

CREATE INDEX validationruleset_standard_idx
  ON "ValidationRuleSet"(standard);

CREATE INDEX validationrule_applies_to_idx
  ON "ValidationRule"(applies_to);
