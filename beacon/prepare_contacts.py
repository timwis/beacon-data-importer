from datetime import datetime

import click
import petl as etl

from .helpers import serialize_row, parse_date

@click.command()
@click.argument('gds_file_path')
def prepare_contacts(gds_file_path):
  """Extracts core contact fields from gds_file_path, and adds a serialized
     version of the records from as a json column."""

  now = datetime.now().isoformat()
  gds_table = etl.fromcsv(gds_file_path)
  gds_header = gds_table.fieldnames()

  gds_table \
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
         'gds_import_data') \
    .tocsv()

# Concatenate non-empty address parts with ', ' separator
def concat_address(row):
  parts = [ row['Address1'], row['Address2'],
            row['Address3'], row['Address4'],
            row['Address5'], row['Postcode'] ]
  nonempty_parts = [part for part in parts if part]
  return ', '.join(nonempty_parts)
