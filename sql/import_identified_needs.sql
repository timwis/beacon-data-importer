WITH contacts_map AS (
  SELECT id AS contact_id,
         nhs_number
  FROM contacts
)
INSERT INTO needs (contact_id,
                   category,
                   name,
                   created_at,
                   updated_at,
                   completed_on,
                   supplemental_data,
                   user_id,
                   start_on)
  SELECT contacts_map.contact_id,
          tmp_needs.category,
          tmp_needs.name,
          tmp_needs.created_at,
          tmp_needs.updated_at,
          tmp_needs.completed_on,
          tmp_needs.supplemental_data,
          tmp_needs.user_id,
          tmp_needs.start_on
  FROM tmp_identified_needs AS tmp_needs
  JOIN contacts_map
    ON contacts_map.nhs_number = tmp_needs.nhs_number
;
