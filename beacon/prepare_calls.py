import re
import json

import click
import petl as etl

from .helpers import serialize_row, parse_date
from .calls_header_map import header_map, rename_map

MSG_ORIGINAL_TRIAGE_NEED = '[Import]: Imported from call log spreadsheet'
MSG_CALL_LOG_NOTE = '[Import]: Imported call log'
MSG_IDENTIFIED_NEED = '[Import]: Need identified automatically from imported call log'
MSG_CLOSED_FOOD_NEED = '[Import]: Marked completed because priority 1 and 2 food needs were all met by the time of data import'

@click.command()
@click.argument('calls_file_path')
@click.option('--needs-output', 'needs_output_file_path')
@click.option('--notes-output', 'notes_output_file_path')
def prepare_calls(calls_file_path, needs_output_file_path, notes_output_file_path):
  """Prepares call log records for import into a temporary calls table"""

  # Expected file is in 'windows-1252' file encoding
  spreadsheet = etl.fromcsv(calls_file_path, encoding='windows-1252') \
    .rename(rename_map) \
    .addfield('import_data', serialize_row(header_map.keys())) \
    .selectnotnone('latest_attempt_date') \
    .convert('latest_attempt_date', parse_date)

  original_triage_needs = spreadsheet \
    .rename({'latest_attempt_date': 'created_at'}) \
    .addfield('updated_at', lambda row: row['created_at']) \
    .addfield('completed_on', determine_triage_completion) \
    .addfield('category', 'phone triage') \
    .addfield('name', MSG_ORIGINAL_TRIAGE_NEED) \
    .cut('nhs_number',
         'category',
         'name',
         'completed_on',
         'created_at',
         'updated_at')

  # TODO: infer voicemail notes from outcome field
  generated_header = ['nhs_number', 'latest_attempt_date', 'category', 'body']
  call_notes = spreadsheet \
    .selectnotnone('was_contact_made') \
    .rowmapmany(generate_call_notes, header=generated_header) \
    .rename({'latest_attempt_date': 'created_at'}) \
    .addfield('updated_at', lambda row: row['created_at']) \
    .cut('nhs_number',
         'category',
         'body',
         'created_at',
         'updated_at')

  import_notes = spreadsheet \
    .addfield('body', compose_body) \
    .rename({'latest_attempt_date': 'created_at'}) \
    .addfield('updated_at', lambda row: row['created_at']) \
    .addfield('category', 'phone_import') \
    .cut('nhs_number',
         'category',
         'body',
         'created_at',
         'updated_at',
         'import_data')

  identified_food_needs = spreadsheet \
    .rename({'latest_attempt_date': 'created_at'}) \
    .addfield('updated_at', lambda row: row['created_at']) \
    .selectin('outcome', ['Food referral', 'Food and Other referral']) \
    .addfield('category', 'groceries and cooked meals') \
    .convert('food_priority', parse_food_priority) \
    .addfield('supplemental_data', construct_supplemental_data) \
    .addfield('completed_on', determine_food_completion) \
    .addfield('name', compose_food_need_name) \
    .cut('nhs_number',
         'category',
         'name',
         'completed_on',
         'supplemental_data',
         'created_at',
         'updated_at')

# Impure: Uses global header_map variable
def compose_body(row):
  lines = [f"{value['label']}: {row[key].strip()}"
           for key, value in header_map.items()
           if value['label'] and row[key].strip()]
  return "\n".join(lines)

def determine_triage_completion(row):
  completed_values = ['yes', 'no 3 attempts made']
  return row['created_at'] if row['was_contact_made'].lower() in completed_values else None

def generate_call_notes(row):
  was_contact_made = row['was_contact_made'].lower()

  if was_contact_made == 'yes':
    category = 'phone_success'
    count = 1
  elif was_contact_made == 'no -1 attempt made' \
    or was_contact_made == 'invalid phone numbers':
    category = 'phone_failure'
    count = 1
  elif was_contact_made == 'no 2 attempts made':
    category = 'phone_failure'
    count = 2
  elif was_contact_made == 'no 3 attempts made':
    category = 'phone_failure'
    count = 3

  for x in range(count):
    yield [
      row['nhs_number'],
      row['latest_attempt_date'],
      category,
      MSG_CALL_LOG_NOTE
    ]

def parse_food_priority(value):
  return re.search(r'priority (\d)', value, re.IGNORECASE) \
           .group(1)

def determine_food_completion(row):
  return row['created_at'] if row['food_priority'] in ['1', '2'] else None

# TODO: Add food_service_type, if possible
def construct_supplemental_data(row):
  keys = ['food_priority']
  supplemental_data = { key: row[key] for key in keys if row[key] }
  return json.dumps(supplemental_data) if len(supplemental_data) else None

# needs.name is used as a description in the app
def compose_food_need_name(row):
  lines = [MSG_IDENTIFIED_NEED]
  if row['completed_on']:
    lines.append(MSG_CLOSED_FOOD_NEED)
  lines.append(compose_body(row))
  return "\n".join(lines)
