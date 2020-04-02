# Beacon data importer
Convert person data to a CSV format that can easily be imported
to Beacon's database.

## Usage
With Python 3 and [Pipenv][pipenv] installed:

1. Clone this repository and run `pipenv install` within it.
2. Run `pipenv shell` to activate a local environment shell.
3. Run the script using `python bin/cli.py`

```
Usage: cli.py [OPTIONS] FILE_PATH

Options:
  --help                   Show this message and exit.
```

Basic example:

```
python bin/cli.py people.xlsx > contacts.csv
```
