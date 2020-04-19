UPDATE contacts
SET additional_info = COALESCE(tmp_updates.additional_info, contacts.additional_info),
    delivery_details = COALESCE(tmp_updates.delivery_details, contacts.delivery_details),
    dietary_details = COALESCE(tmp_updates.dietary_details, contacts.dietary_details),
    has_covid_symptoms = COALESCE(tmp_updates.has_covid_symptoms, contacts.has_covid_symptoms)
FROM tmp_contact_profile_updates AS tmp_updates
WHERE tmp_updates.nhs_number = contacts.nhs_number;
