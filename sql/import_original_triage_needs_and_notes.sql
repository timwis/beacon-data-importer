WITH contacts_map AS (
  SELECT id AS contact_id,
         nhs_number
  FROM contacts
), inserted_needs AS (
  INSERT INTO needs (contact_id,
                     category,
                     name,
                     created_at,
                     updated_at,
                     completed_on)
  	SELECT contacts_map.contact_id,
           tmp_needs.category,
           tmp_needs.name,
           tmp_needs.created_at,
           tmp_needs.updated_at,
           tmp_needs.completed_on
  	FROM tmp_original_triage_needs AS tmp_needs
  	JOIN contacts_map
  	  ON contacts_map.nhs_number = tmp_needs.nhs_number
  RETURNING id, contact_id
)
INSERT into notes (need_id,
                   category,
                   body,
                   created_at,
                   updated_at,
                   import_data)
  SELECT inserted_needs.id,
         tmp_notes.category,
         tmp_notes.body,
         tmp_notes.created_at,
         tmp_notes.updated_at,
         tmp_notes.import_data
  FROM tmp_original_triage_notes AS tmp_notes
  JOIN contacts_map
  	ON contacts_map.nhs_number = tmp_notes.nhs_number
  JOIN inserted_needs
  	ON inserted_needs.contact_id = contacts_map.contact_id
;
