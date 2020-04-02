import json

import click
import petl as etl
import openpyxl

@click.command()
@click.argument('file_path')
def convert(file_path):
  table = etl.fromxlsx(file_path, read_only=True).head()
  header = table.header()

  table \
    .addfield('imported_data', lambda row: json.dumps(dict(zip(header, row)))) \
    .cut('Name ', 'Phone', 'Mobile', 'Email', 'Address', 'imported_data') \
    .rename({'Name ': 'full_name',
             'Phone': 'telephone',
             'Mobile': 'mobile',
             'Email': 'email',
             'Address': 'address'}) \
    .convert('full_name', lambda value: value.title()) \
    .tocsv()

if __name__ == '__main__':
  convert()
