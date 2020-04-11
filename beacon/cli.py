import json
from datetime import datetime
import pdb

import click
import petl as etl

@click.group()
def main():
  pass

@main.command()
@click.argument('gds_file_path')
@click.argument('healthintent_file_path')
def prepare_contacts(gds_file_path, healthintent_file_path):
  """Extracts core contact fields from gds_file_path, and adds a serialized
     version of the records from each file as json columns."""

  now = datetime.now().isoformat()
  gds_table = etl.fromcsv(gds_file_path)
  gds_header = gds_table.fieldnames()

  gds_table = gds_table \
    .addfield('gds_import_data', serialize_row(gds_header)) \
    .addfield('created_at', now) \
    .addfield('updated_at', now) \
    .addfield('address', concat_address) \
    .rename({'NHSNumber': 'nhs_number',
             'FirstName': 'first_name',
             'MiddleName': 'middle_names',
             'LastName': 'surname',
             'Postcode': 'postcode',
             'DOB': 'date_of_birth',
             'Phone': 'telephone',
             'Mobile': 'mobile'}) \
    .convert('date_of_birth', parse_date) \
    .convert(('telephone', 'mobile'), add_leading_zero_if_missing) \
    .cut('nhs_number',
         'first_name',
         'middle_names',
         'surname',
         'address',
         'postcode',
         'telephone',
         'mobile',
         'date_of_birth',
         'created_at',
         'updated_at',
         'gds_import_data')

  healthintent_table = etl.fromcsv(healthintent_file_path)
  healthintent_header = healthintent_table.fieldnames()

  healthintent_table = healthintent_table \
    .addfield('healthintent_import_data', serialize_row(healthintent_header)) \
    .rename('NHS number', 'nhs_number') \
    .cut('nhs_number', 'healthintent_import_data')

  etl.join(gds_table, healthintent_table, key='nhs_number') \
    .tocsv()

@main.command()
@click.argument('calls_file_path')
def prepare_calls(calls_file_path):
  """Prepares call log records for import into a temporary calls table"""

  # Expected file is in 'windows-1252' file encoding
  calls_table = etl.fromcsv(calls_file_path, encoding='windows-1252')
  calls_header = calls_table.fieldnames()

  calls_table \
    .addfield('import_data', serialize_row(calls_header)) \
    .addfield('body', compose_body(calls_header)) \
    .rename({'Shielded ID': 'shielded_id',
             'Contact attempted (date)': 'latest_attempt_date'}) \
    .convert('latest_attempt_date', parse_date) \
    .cut('shielded_id',
         'latest_attempt_date',
         'body',
         'import_data') \
    .tocsv()

def serialize_row(keys):
  return lambda row: json.dumps(dict(zip(keys, row)))

# Concatenate non-empty address parts with ', ' separator
def concat_address(row):
  parts = [ row['Address1'], row['Address2'],
            row['Address3'], row['Address4'],
            row['Address5'], row['Postcode'] ]
  nonempty_parts = [part for part in parts if part]
  return ', '.join(nonempty_parts)

# '31/01/1980' => '1980-03-31'
def parse_date(value):
  if value == '':
    return None

  input_format = '%d/%m/%Y'
  return datetime.strptime(value, input_format).date()

def add_leading_zero_if_missing(value):
  if value[0] != '0':
    return '0' + value
  else:
    return value

def compose_body(keys):
  keys_to_omit = ['Shielded ID', 'Contact attempted (date)', 'Time', 'import_data']
  return lambda row: "\n".join([f"{key.strip()}: {row[key]}"
                                for key in keys
                                if key not in keys_to_omit and row[key]])

if __name__ == '__main__':
  main()
