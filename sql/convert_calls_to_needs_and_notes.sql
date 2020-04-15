WITH contacts_map AS (
  SELECT id AS contact_id, nhs_number
  FROM contacts
), inserted_needs AS (
  INSERT INTO needs (contact_id, category, name, created_at, updated_at)
  	SELECT contacts_map.contact_id, 'phone triage', 'Imported call log',
      tmp_calls.latest_attempt_date, tmp_calls.latest_attempt_date
  	FROM tmp_calls
  	JOIN contacts_map
  	  ON contacts_map.nhs_number = tmp_calls.nhs_number
  RETURNING id, contact_id
)
INSERT into notes (need_id, body, category, import_data, created_at, updated_at)
  SELECT inserted_needs.id, tmp_calls.body, 'phone_import',
    tmp_calls.import_data, tmp_calls.latest_attempt_date, tmp_calls.latest_attempt_date
  FROM tmp_calls
  JOIN contacts_map
  	ON contacts_map.nhs_number = tmp_calls.nhs_number
  JOIN inserted_needs
  	ON inserted_needs.contact_id = contacts_map.contact_id
;
