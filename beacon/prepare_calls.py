import click
import petl as etl

from .helpers import serialize_row, parse_date

@click.command()
@click.argument('calls_file_path')
def prepare_calls(calls_file_path):
  """Prepares call log records for import into a temporary calls table"""

  # Expected file is in 'windows-1252' file encoding
  calls_table = etl.fromcsv(calls_file_path, encoding='windows-1252')
  original_calls_header = calls_table.fieldnames()

  calls_table = calls_table \
    .addfield('import_data', serialize_row(original_calls_header)) \
    .rename({'NHSNUMBER': 'nhs_number',
             'Contact attempted (date)  Format:  06/04/2020': 'latest_attempt_date',
             'If no support needed, what support are they getting and who is supporting them eg Govt food parcels/Age Uk/Other VCS, family member, friends, neighbours). If support need is likely to change eg resident would like a call back to check in with them - selec': 'If no support needed, what support are they getting',
             "Date to call resident back.  Add date below - 6 days from today's date (avoid weekend dates) format: 12/04/20": 'Date to call resident back',
             'how many people in household? Basic number and if relevant eg baby, children': 'How many people in household? Basic number and if relevant eg baby, children',
             'Do you have any special dietary requirements and notes? Eg special requirements - allergies, standard, vegetarian, vegan, baby, religious - halal  ': 'Do you have any special dietary requirements and notes?',
             'Delivery contact details if different? Eg if someone needs to let deliverer in. Contact name and number': 'Delivery contact details if different?',
             "Any special delivery information - any times you cannot do/access?  Eg how to get to block/house/intercome/doorbell doesn't work - times to avoid eg when taking medication": 'Any special delivery information - any times you cannot do/access?',
             'Have you told resident about the 24/7 Camden Council Covid 19 support line and website?                         Call:  020 7974 4444 extension 9  and www.camden.gov.uk/covid-19': 'Have you told resident about the 24/7 Camden Council Covid 19 support line and website?'
             }) \

  revised_calls_header = calls_table.fieldnames()

  calls_table \
    .addfield('body', compose_body(revised_calls_header)) \
    .select(has_non_empty_latest_attempt_date) \
    .convert('latest_attempt_date', parse_date) \
    .cut('nhs_number',
         'latest_attempt_date',
         'body',
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

def has_non_empty_latest_attempt_date(row):
  return row['latest_attempt_date']
