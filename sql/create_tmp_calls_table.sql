CREATE TABLE tmp_calls (
  nhs_number text NOT NULL,
  latest_attempt_date date,
  body text,
  import_data jsonb NOT NULL
);
