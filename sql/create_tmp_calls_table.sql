CREATE TABLE tmp_calls (
  shielded_id text NOT NULL,
  latest_attempt_date date,
  body text,
  import_data jsonb NOT NULL
);
