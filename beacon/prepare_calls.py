import click
import petl as etl

from .helpers import serialize_row, parse_date

MSG_ORIGINAL_TRIAGE_NEED = 'Imported from call log spreadsheet'
MSG_CALL_LOG_NOTE = 'Imported call log'

@click.command()
@click.argument('calls_file_path')
@click.option('--needs-output', 'needs_output_file_path')
@click.option('--notes-output', 'notes_output_file_path')
def prepare_calls(calls_file_path, needs_output_file_path, notes_output_file_path):
  """Prepares call log records for import into a temporary calls table"""

  # Expected file is in 'windows-1252' file encoding
  spreadsheet = etl.fromcsv(calls_file_path, encoding='windows-1252')
  trimmed_header = [col.strip() for col in spreadsheet.fieldnames()]

  spreadsheet = spreadsheet \
    .setheader(trimmed_header) \
    .addfield('import_data', serialize_row(trimmed_header)) \
    .rename({'NHSNUMBER': 'nhs_number',
             'Contact attempted (date)  Format:  06/04/2020': 'latest_attempt_date',
             'If no support needed, what support are they getting and who is supporting them eg Govt food parcels/Age Uk/Other VCS, family member, friends, neighbours). If support need is likely to change eg resident would like a call back to check in with them - selec': 'If no support needed, what support are they getting',
             "Date to call resident back.  Add date below - 6 days from today's date (avoid weekend dates) format: 12/04/20": 'Date to call resident back',
             'how many people in household? Basic number and if relevant eg baby, children': 'How many people in household?',
             'Do you have any special dietary requirements and notes? Eg special requirements - allergies, standard, vegetarian, vegan, baby, religious - halal': 'Do you have any special dietary requirements and notes?',
             'Delivery contact details if different? Eg if someone needs to let deliverer in. Contact name and number': 'Delivery contact details if different?',
             "Any special delivery information - any times you cannot do/access?  Eg how to get to block/house/intercome/doorbell doesn't work - times to avoid eg when taking medication": 'Any special delivery information - any times you cannot do/access?',
             'Have you told resident about the 24/7 Camden Council Covid 19 support line and website?                         Call:  020 7974 4444 extension 9  and www.camden.gov.uk/covid-19': 'Have you told resident about the 24/7 Camden Council Covid 19 support line and website?'
             }) \
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
    .selectnotnone('Contact Sucessful') \
    .rowmapmany(generate_call_notes, header=call_notes_header) \
    .rename({'latest_attempt_date': 'created_at'}) \
    .addfield('updated_at', lambda row: row['created_at']) \
    .cut('nhs_number',
         'category',
         'body',
         'created_at',
         'updated_at')

  revised_header = spreadsheet.fieldnames()
  import_notes = spreadsheet \
    .addfield('body', compose_body(revised_header)) \
    .rename({'latest_attempt_date': 'created_at'}) \
    .addfield('updated_at', lambda row: row['created_at']) \
    .addfield('category', 'phone_import') \
    .cut('nhs_number',
         'category',
         'body',
         'created_at',
         'updated_at',
         'import_data') \
    .tocsv()

def compose_body(keys):
  keys_to_omit = [
    'nhs_number',
    'latest_attempt_date',
    'Time. Format:  12:40',
    '15/04/20 consolidation record',
    'import_data'
  ]
  return lambda row: "\n".join([f"{key.strip()}: {row[key].strip()}"
                                  for key in keys
                                  if key not in keys_to_omit and row[key].strip()])

def is_completed(row):
  completed_values = ['yes', 'no 3 attempts made']
  return row['Contact Sucessful'].lower() in completed_values

def generate_call_notes(row):
  summary_field = row['Contact Sucessful'].lower()

  if summary_field == 'yes':
    category = 'phone_success'
    count = 1
  elif summary_field == 'no -1 attempt made' \
    or summary_field == 'invalid phone numbers':
    category = 'phone_failure'
    count = 1
  elif summary_field == 'no 2 attempts made':
    category = 'phone_failure'
    count = 2
  elif summary_field == 'no 3 attempts made':
    category = 'phone_failure'
    count = 3

  for x in range(count):
    yield [
      row['nhs_number'],
      row['latest_attempt_date'],
      category,
      MSG_CALL_LOG_NOTE
    ]
