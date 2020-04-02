import json
import datetime

import click
import petl as etl

def concat_phone_fields(row):
  fields_to_concat = []

  if row['Phone No.'].isdigit():
    fields_to_concat.append(row['Phone No.'])
  
  if row['Additona Phone Nuumbers (LBC Sources)']:
    fields_to_concat.append(row['Additona Phone Nuumbers (LBC Sources)'])

  return ' '.join(fields_to_concat)

@click.command()
@click.argument('file_path')
def convert(file_path):
  table = etl.fromcsv(file_path)
  header = table.fieldnames()
  now = datetime.datetime.now().isoformat()

  table \
    .addfield('nhs_import_data', lambda row: json.dumps(dict(zip(header, row)))) \
    .addfield('telephone', concat_phone_fields) \
    .addfield('created_at', now) \
    .addfield('updated_at', now) \
    .cut('First Names', 'Last Name', 'Address',
         'Post Code', 'telephone', 'created_at',
         'updated_at', 'nhs_import_data') \
    .rename({'First Names': 'first_name',
             'Last Name': 'surname',
             'Address': 'address',
             'Post Code': 'postcode'}) \
    .tocsv()

if __name__ == '__main__':
  convert()
