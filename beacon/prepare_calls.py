import re
import json
from datetime import date, datetime, timedelta
from functools import partial
from os.path import join

import click
import petl as etl

from .helpers import serialize_row, parse_date
from .calls_header_map import header_map, rename_map

MSG_ORIGINAL_TRIAGE_NEED = '[Import]: Imported from call log spreadsheet'
MSG_CALL_LOG_NOTE = '[Import]: Imported call log'
MSG_GENERIC_NEED = '[Import]: Need created automatically from imported call log'
MSG_CALLBACK_NEED = '[Import]: Callback need created automatically because the imported call log had a food need or callback date specified'
MSG_CLOSED_FOOD_NEED = '[Import]: Marked completed because priority 1 and 2 food needs were all met by the time the call log was imported'
MSG_OTHER_NEED = '[Import]: Need created automatically because the imported call log had an "Other referral" or filled in "Additional support"'

@click.command()
@click.argument('calls_file_path')
@click.option('-o', '--output-dir', 'output_dir', required=True,
              type=click.Path(exists=True, file_okay=False, writable=True))
@click.option('-fnu', '--food-needs-user', 'food_needs_user', required=True, type=int)
@click.option('-cnu', '--complex-needs-user', 'complex_needs_user', required=True, type=int)
@click.option('-snu', '--simple-needs-user', 'simple_needs_user', required=True, type=int)
@click.option('-clru', '--call-log-review-user', 'call_log_review_user', required=True, type=int)
def prepare_calls(calls_file_path, output_dir, food_needs_user,
                  complex_needs_user, simple_needs_user, call_log_review_user):
  """Prepares call log records for import"""

  # Expected file is in 'windows-1252' file encoding
  spreadsheet = (
    etl.fromcsv(calls_file_path, encoding='windows-1252')
    .rename(rename_map)
    .select(lambda row: row['latest_attempt_date'])
    .addfield('import_data', partial(serialize_row, keys=header_map.keys()))
    .convert('latest_attempt_date', parse_date)
    .addfield('created_at', lambda row: row['latest_attempt_date'])
    .addfield('updated_at', lambda row: row['latest_attempt_date'])
  )

  needs_fields = ['nhs_number', 'category', 'name', 'created_at', 'updated_at']
  notes_fields = ['nhs_number', 'category', 'body', 'created_at', 'updated_at']

  original_triage_needs = (
    spreadsheet
    .addfield('category', 'phone triage')
    .addfield('name', MSG_ORIGINAL_TRIAGE_NEED)
    .addfield('completed_on', determine_triage_completion)
    .cut(*needs_fields, 'completed_on')
  )

  generated_header = ['nhs_number', 'created_at', 'updated_at', 'category']
  original_triage_call_notes = (
    spreadsheet
    .selectnotnone('was_contact_made')
    .rowmapmany(generate_call_notes, header=generated_header)
    .addfield('body', MSG_CALL_LOG_NOTE)
    .cut(*notes_fields)
  )

  original_triage_import_notes = (
    spreadsheet
    .addfield('category', 'phone_import')
    .addfield('body', partial(compose_body, fields=header_map))
    .cut(*notes_fields, 'import_data')
  )

  food_needs = (
    spreadsheet
    .select(needs_food)
    .addfield('category', 'groceries and cooked meals')
    .convert('food_priority', parse_food_priority)
    .addfield('supplemental_data', construct_supplemental_data)
    .addfield('completed_on', determine_food_completion)
    .addfield('user_id', food_needs_user)
    .addfield('name', partial(compose_food_need_desc, fields=header_map))
    .cut(*needs_fields, 'completed_on', 'supplemental_data', 'user_id')
  )

  callback_needs = (
    spreadsheet
    .convert('callback_date', parse_callback_date)
    .select(needs_callback)
    .addfield('category', 'phone triage')
    .addfield('name', partial(compose_callback_need_desc, fields=header_map))
    .addfield('start_on', determine_callback_start_date)
    .cut(*needs_fields, 'start_on')
  )

  prescription_needs = (
    spreadsheet
    .select(lambda row: row['addl_medication_prescriptions'])
    .addfield('category', 'prescription pickups')
    .addfield('name', partial(compose_other_need_desc, fields=header_map))
    .addfield('user_id', simple_needs_user)
    .cut(*needs_fields, 'user_id')
  )

  mental_wellbeing_needs = (
    spreadsheet
    .select(lambda row: row['addl_mental_wellbeing'])
    .addfield('category', 'physical and mental wellbeing')
    .addfield('name', partial(compose_other_need_desc, fields=header_map))
    .addfield('user_id', complex_needs_user)
    .cut(*needs_fields, 'user_id')
  )

  financial_needs = (
    spreadsheet
    .select(lambda row: row['addl_financial'])
    .addfield('category', 'financial support')
    .addfield('name', partial(compose_other_need_desc, fields=header_map))
    .addfield('user_id', complex_needs_user)
    .cut(*needs_fields, 'user_id')
  )

  other_needs = (
    spreadsheet
    .select(needs_other_support)
    .addfield('category', 'other')
    .addfield('name', partial(compose_other_need_desc, fields=header_map))
    .addfield('user_id', partial(determine_other_need_user,
                                 complex_needs_user=complex_needs_user,
                                 simple_needs_user=simple_needs_user,
                                 call_log_review_user=call_log_review_user))
    .cut(*needs_fields, 'user_id')
  )

  # TODO: prefix with [Import]
  contact_profile_updates = (
    spreadsheet
    .addfield('additional_info', partial(compose_additional_info, fields=header_map))
    .addfield('delivery_details', partial(compose_delivery_details, fields=header_map))
    .addfield('dietary_details', compose_dietary_details)
    .convert('has_covid_symptoms', parse_covid_symptoms)
    .cut('nhs_number',
         'additional_info',
         'delivery_details',
         'dietary_details',
         'has_covid_symptoms')
  )

  # TODO: Improve implementation and readability of QA bits (currently loads all tables into memory)
  # TODO: Consider adding stats to output somewhere for additional QA
  lookups = {
    'original_triage_needs': original_triage_needs.dictlookupone('nhs_number'),
    'original_triage_call_notes': original_triage_call_notes.dictlookup('nhs_number'), # returns list
    'food_needs': food_needs.dictlookupone('nhs_number'),
    'callback_needs': callback_needs.dictlookupone('nhs_number'),
    'remaining_needs': etl.cat(prescription_needs,
                               mental_wellbeing_needs,
                               financial_needs,
                               other_needs).dictlookup('nhs_number') # returns list
  }
  quality_assurance = (
    spreadsheet
    .addfield('call_log', partial(compose_body, fields=header_map))
    .addfield('original_triage_status', partial(qa_original_triage_status, lookups['original_triage_needs']))
    .addfield('original_triage_call_notes', partial(qa_original_triage_call_notes, lookups['original_triage_call_notes']))
    .addfield('food_need', partial(qa_food_need, lookups['food_needs']))
    .addfield('callback_need', partial(qa_callback_need, lookups['callback_needs']))
    .addfield('remaining_needs', partial(qa_remaining_needs, lookups['remaining_needs']))
    .cut('nhs_number',
         'latest_attempt_date',
         'original_triage_status',
         'original_triage_call_notes',
         'food_need',
         'callback_need',
         'remaining_needs',
         'call_log')
  )

  # Write files
  quality_assurance.tocsv(join(output_dir, 'quality_assurance.csv'))
  contact_profile_updates.tocsv(join(output_dir, 'contact_profile_updates.csv'))
  original_triage_needs.tocsv(join(output_dir, 'original_triage_needs.csv'))

  etl.cat(original_triage_import_notes, original_triage_call_notes) \
     .tocsv(join(output_dir, 'original_triage_notes.csv'))

  # psql copy meta command hangs when importing fully combined needs file
  food_needs.tocsv(join(output_dir, 'food_needs.csv'))
  callback_needs.tocsv(join(output_dir, 'callback_needs.csv'))

  etl.cat(prescription_needs,
          mental_wellbeing_needs,
          financial_needs,
          other_needs) \
     .tocsv(join(output_dir, 'remaining_needs.csv'))

def compose_body(row, fields, prefix_lines=None):
  lines = [f"{value['label']}: {row[key].strip()}"
          for key, value in fields.items()
          if value['label'] and row[key] and row[key].strip()]

  if prefix_lines:
    lines = prefix_lines + lines

  return '\n'.join(lines)

def compose_generic_need_desc(row, fields):
  return compose_body(row, fields, prefix_lines=[MSG_GENERIC_NEED])

def compose_other_need_desc(row, fields):
  return compose_body(row, fields, prefix_lines=[MSG_OTHER_NEED])

def compose_callback_need_desc(row, fields):
  return compose_body(row, fields, prefix_lines=[MSG_CALLBACK_NEED])

def compose_food_need_desc(row, fields):
  prefix_lines = [MSG_GENERIC_NEED]

  if row['completed_on']:
    prefix_lines.append(MSG_CLOSED_FOOD_NEED)

  return compose_body(row, fields, prefix_lines=prefix_lines)

def compose_additional_info(row, fields):
  relevant_fields = ['household_count', 'support_already_geting', 'notes']
  return compose_body(row, pluck(fields, relevant_fields))

def compose_delivery_details(row, fields):
  relevant_fields = ['delivery_contact', 'delivery_special_info']
  return compose_body(row, pluck(fields, relevant_fields))

def compose_dietary_details(row):
  if not row['dietary_requirements'].lower().strip() == 'no':
    return row['dietary_requirements']

def pluck(dict, keys):
  return { key: value for key, value in dict.items() if key in keys }

def determine_triage_completion(row):
  completed_values = ['yes', 'no 3 attempts made']
  return row['latest_attempt_date'] if row['was_contact_made'].lower() in completed_values else None

def parse_covid_symptoms(value):
  clean_value = value.strip().lower()
  if clean_value == 'yes':
    return True
  elif clean_value == 'no':
    return False
  else:
    return None

def generate_call_notes(row):
  was_contact_made = row['was_contact_made'].lower()
  failure_category = ('phone_message'
    if row['outcome'] == 'Left voicemail'
    else 'phone_failure')

  if was_contact_made == 'yes':
    category = 'phone_success'
    count = 1
  elif (was_contact_made == 'no -1 attempt made'
    or was_contact_made == 'invalid phone numbers'):
    category = failure_category
    count = 1
  elif was_contact_made == 'no 2 attempts made':
    category = failure_category
    count = 2
  elif was_contact_made == 'no 3 attempts made':
    category = failure_category
    count = 3

  for x in range(count):
    yield [
      row['nhs_number'],
      row['created_at'],
      row['updated_at'],
      category
    ]

def parse_food_priority(value):
  return re.search(r'priority (\d)', value, re.IGNORECASE) \
           .group(1)

def determine_food_completion(row):
  return row['latest_attempt_date'] if row['food_priority'] in ['1', '2'] else None

def construct_supplemental_data(row):
  supplemental_data = {
    'food_service_type': 'Grocery delivery'
  }
  if row['food_priority']:
    supplemental_data['food_priority'] = row['food_priority']

  return json.dumps(supplemental_data)

def parse_callback_date(value):
  date_like_string = re.search(r'(\d+[/\.]\d+[/\.]\d+)', value).group(1)
  if date_like_string:
    possible_formats = [
      '%d/%m/%Y',
      '%d.%m.%y'
    ]
    for fmt in possible_formats:
      try:
        return datetime.strptime(date_like_string, fmt) \
                       .date().isoformat()
      except ValueError:
        pass

  return None

def needs_food(row):
  # source data uses trailing space
  return (row['outcome'] in ['Food referral ', 'Food and Other referral']
          or row['food_priority'])

def needs_callback(row):
  return (row['callback_date']
          or needs_food(row)
          or row['book_weekly_food_delivery'] == True
          or row['outcome'] == 'Call back ') # source data uses trailing space

def needs_other_support(row):
  return (row['outcome'] in ['Other referral', 'Food and Other referral']
          or has_complex_other_need(row)
          or has_simple_other_need(row)
          or has_value_in_misc_fields(row))

def has_complex_other_need(row):
  return (row['addl_adult_social_care']
          or row['addl_children_services']
          or row['addl_safeguarding'])

def has_simple_other_need(row):
  return (row['addl_housing_waste']
          or row['addl_medical_appt_transport']
          or row['addl_referrals'])

def has_value_in_misc_fields(row):
  return row['addl_misc_other1'] or row['addl_misc_other2']

def determine_callback_start_date(row):
  return (row['callback_date']
          or date.fromisoformat(row['latest_attempt_date']) + timedelta(days=6))

def determine_other_need_user(row, simple_needs_user, complex_needs_user, call_log_review_user):
  if has_complex_other_need(row):
    return complex_needs_user
  elif has_simple_other_need(row):
    return simple_needs_user
  else:
    return call_log_review_user

def qa_original_triage_status(lookup, row):
  match = lookup.get(row['nhs_number'])
  return 'Completed' if match['completed_on'] else 'To do'

def qa_original_triage_call_notes(lookup, row):
  matches = lookup.get(row['nhs_number']) # returns list
  if matches:
    categories = [ note['category'] for note in matches ]
    return ', '.join(categories)

def qa_food_need(lookup, row):
  match = lookup.get(row['nhs_number'])
  if match:
    status = 'Completed' if match['completed_on'] else 'To do'
    assigned_to = match['user_id']
    priority = (json.loads(match['supplemental_data']).get('food_priority', '')
                if match['supplemental_data']
                else None)

    lines = ['Food need created',
             f'Priority: {priority}',
             f'Status: {status}',
             f'Assigned to: {assigned_to}']

    return '\n'.join(lines)

def qa_callback_need(lookup, row):
  match = lookup.get(row['nhs_number'])
  if match:
    start_on = match['start_on']

    lines = ['Callback need created',
             f'Start on: {start_on}']

    return '\n'.join(lines)

def qa_remaining_needs(lookup, row):
  matches = lookup.get(row['nhs_number']) # returns list
  if matches:
    lines = [f"{need['category'].title()} (Assigned to {need['user_id']})"
            for need in matches]
    return '\n'.join(lines)
