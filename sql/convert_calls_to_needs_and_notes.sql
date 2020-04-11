WITH contacts_map AS (
  SELECT id AS contact_id,
    healthintent_import_data->>'Shielded ID' as shielded_id
  FROM contacts
), inserted_needs AS (
  INSERT INTO needs (contact_id, category, name, created_at, updated_at)
  	SELECT contacts_map.contact_id, 'phone triage', 'Imported call log',
      tmp_calls.latest_attempt_date, tmp_calls.latest_attempt_date
  	FROM tmp_calls
  	JOIN contacts_map
  	  ON contacts_map.shielded_id = tmp_calls.shielded_id
  RETURNING id, contact_id
)
INSERT into notes (need_id, body, category, import_data, created_at, updated_at)
  SELECT inserted_needs.id, tmp_calls.body, 'phone_import',
    tmp_calls.import_data, tmp_calls.latest_attempt_date, tmp_calls.latest_attempt_date
  FROM tmp_calls
  JOIN contacts_map
  	ON contacts_map.shielded_id = tmp_calls.shielded_id
  JOIN inserted_needs
  	ON inserted_needs.contact_id = contacts_map.contact_id
;
