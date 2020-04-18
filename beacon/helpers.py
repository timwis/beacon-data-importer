import json
from datetime import datetime

def serialize_row(keys):
  return lambda row: json.dumps(dict(zip(keys, row)))

# '31/01/1980' => '1980-03-31'
def parse_date(value):
  input_format = '%d/%m/%Y'
  return datetime.strptime(value, input_format)
                 .date().isoformat()
