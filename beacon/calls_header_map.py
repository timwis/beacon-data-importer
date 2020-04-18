header_map = {
  'nhs_number': {
    'original': 'NHSNUMBER',
    'label': None
  },
  'is_consolidation_record': {
    'original': '15/04/20 consolidation record',
    'label': None
  },
  'latest_attempt_date': {
    'original': 'Contact attempted (date)  Format:  06/04/2020',
    'label': None
  },
  'latest_attempt_time': {
    'original': 'Time. Format:  12:40',
    'label': None
  },
  'was_contact_made': {
    'original': 'Contact Sucessful ',
    'label': 'Contact successful'
  },
  'outcome': {
    'original': 'Outcome complete at the end of the call',
    'label': 'Outcome'
  },
  'support_already_getting': {
    'original': 'If no support needed, what support are they getting and who is supporting them eg Govt food parcels/Age Uk/Other VCS, family member, friends, neighbours). If support need is likely to change eg resident would like a call back to check in with them - selec',
    'label': 'If no support needed, what support are they getting'
  },
  'food_requirements_priority': {
    'original': 'Food Requirements Priority ',
    'label': 'Food requirements priority'
  },
  'book_weekly_food_delivery': {
    'original': 'Book weekly food delivery  yes/no',
    'label': 'Book weekly food delivery'
  },
  'callback_date': {
    'original': "Date to call resident back.  Add date below - 6 days from today's date (avoid weekend dates) format: 12/04/20",
    'label': 'Date to call resident back'
  },
  'household_count': {
    'original': 'how many people in household? Basic number and if relevant eg baby, children',
    'label': 'How many people in household'
  },
  'dietary_requirements': {
    'original': 'Do you have any special dietary requirements and notes? Eg special requirements - allergies, standard, vegetarian, vegan, baby, religious - halal  ',
    'label': 'Special dietary requirements'
  },
  'food_notes_or_needs': {
    'original': 'Additional food notes  or essential items needed',
    'label': 'Additional food notes or essential items needed'
  },
  'delivery_contact': {
    'original': 'Delivery contact details if different? Eg if someone needs to let deliverer in. Contact name and number',
    'label': 'Delivery contact details'
  },
  'delivery_details': {
    'original': "Any special delivery information - any times you cannot do/access?  Eg how to get to block/house/intercome/doorbell doesn't work - times to avoid eg when taking medication",
    'label': 'Any special delivery information'
  },
  'has_covid_symptoms': {
    'original': 'Are you or anyone in your home showing any symptoms of COVID-19?',
    'label': 'Are you or anyone in your home showing any symptoms of COVID-19?'
  },
  'addl_adult_social_care': {
    'original': 'Additional Support: Adult Social Care.  Complete if you or resident have concerns and want follow up action.',
    'label': 'Additional support: Adult Social Care'
  },
  'addl_children_services': {
    'original': 'Additional Support: Children Services Complete if you or resident have concerns and want follow up action.',
    'label': 'Additional support: Children Services'
  },
  'addl_safeguarding': {
    'original': 'Additional Support: Safeguarding Complete if you or resident have concerns and want follow up action.',
    'label': 'Additional support: Safeguarding'
  },
  'addl_medical_appt_transport': {
    'original': 'Additional Support: Medical appointment Transport. ',
    'label': 'Additional support: Medical appointment transport'
  },
  'addl_financial': {
    'original': 'Additional Support: Financial guidance/ information. Complete if you or resident have concerns and want follow up action.',
    'label': 'Additional support: Financial guidance/information'
  },
  'addl_shopping': {
    'original': 'Additional Support: Additional Shopping needs',
    'label': 'Additional support: Additional shopping needs'
  },
  'addl_referrals': {
    'original': 'Additional Support: Other referrals (eg concerns for neighbour/friend)',
    'label': 'Additional support: Other referrals (eg concerns for neighbour/friend)'
  },
  'addl_misc_other1': {
    'original': 'Additional Support: Miscellaneous Other',
    'label': 'Additional support: Miscellaneous other'
  },
  'addl_misc_other2': {
    'original': 'Additional Support: Miscellaneous Other2',
    'label': 'Additional support: Miscellaneous other 2'
  },
  'notes': {
    'original': 'Notes: Please add any helpful information from resident here',
    'label': 'Notes'
  },
  'was_told_about_support_line': {
    'original': 'Have you told resident about the 24/7 Camden Council Covid 19 support line and website?                         Call:  020 7974 4444 extension 9  and www.camden.gov.uk/covid-19',
    'label': 'Told resident about support line and website'
  }
}

rename_map = { value['original']: key for key, value in header_map.items() }
