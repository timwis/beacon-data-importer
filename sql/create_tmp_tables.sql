DROP TABLE IF EXISTS tmp_original_triage_needs;
CREATE TABLE tmp_original_triage_needs (
  nhs_number text NOT NULL,
  category text NOT NULL,
  name text NOT NULL,
  created_at date NOT NULL,
  updated_at date NOT NULL,
  completed_on date
);

DROP TABLE IF EXISTS tmp_original_triage_notes;
CREATE TABLE tmp_original_triage_notes (
  nhs_number text NOT NULL,
  category text NOT NULL,
  body text NOT NULL,
  created_at date NOT NULL,
  updated_at date NOT NULL,
  import_data jsonb
);

DROP TABLE IF EXISTS tmp_identified_needs;
CREATE TABLE tmp_identified_needs (
  nhs_number text NOT NULL,
  category text NOT NULL,
  name text,
  created_at date NOT NULL,
  updated_at date NOT NULL,
  completed_on date,
  supplemental_data jsonb,
  user_id bigint,
  start_on date
);

DROP TABLE IF EXISTS tmp_contact_profile_updates;
CREATE TABLE tmp_contact_profile_updates (
  nhs_number text NOT NULL,
  additional_info text,
  delivery_details text,
  dietary_details text,
  has_covid_symptoms boolean
);
