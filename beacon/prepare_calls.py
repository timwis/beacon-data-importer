import click
import petl as etl

from .helpers import serialize_row, parse_date
from .calls_header_map import header_map, rename_map

MSG_ORIGINAL_TRIAGE_NEED = 'Imported from call log spreadsheet'
MSG_CALL_LOG_NOTE = 'Imported call log'

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
    .addfield('completed_on', lambda row: row['created_at'] if is_completed(row) else None) \
    .addfield('category', 'phone triage') \
    .addfield('name', MSG_ORIGINAL_TRIAGE_NEED) \
    .cut('nhs_number',
         'category',
         'name',
         'completed_on',
         'created_at',
         'updated_at')

  call_notes_header = ['nhs_number', 'latest_attempt_date', 'category', 'body']
  call_notes = spreadsheet \
    .selectnotnone('was_contact_made') \
    .rowmapmany(generate_call_notes, header=call_notes_header) \
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
         'import_data').tocsv()

# Impure: Uses global header_map variable
def compose_body(row):
  lines = [f"{value['label']}: {row[key].strip()}"
           for key, value in header_map.items()
           if value['label'] and row[key].strip()]
  return "\n".join(lines)

def is_completed(row):
  completed_values = ['yes', 'no 3 attempts made']
  return row['was_contact_made'].lower() in completed_values

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
