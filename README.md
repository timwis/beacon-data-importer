# Beacon data importer
Convert person data to a CSV format that can easily be imported
to Beacon's database.

## Usage
With Python 3 and [Pipenv][pipenv] installed:

1. Clone this repository and run `pipenv install` within it.
2. Run `pipenv shell` to activate a local environment shell.
3. Run the script using `python cli.py`

```
Usage: cli.py [OPTIONS] GDS_FILE_PATH HEALTHINTENT_FILE_PATH

  Extract core contact fields from gds_file_path, and add a serialized
  version of the records from each file as json columns

Options:
  --help                   Show this message and exit.
```

Basic example:

```
python cli.py data/gds.csv data/healthintent.csv > contacts.csv
```
