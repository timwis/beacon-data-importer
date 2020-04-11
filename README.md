# Beacon data importer
Convert person data to a CSV format that can easily be imported
to Beacon's database.

## Installation

Ensure you have Python 3.7+ installed on your machine.

```
pip3 install "git+https://github.com/timwis/beacon-data-importer#egg=beacon-data-importer"
```

## Usage
```
Usage: beacon [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  prepare-calls     Prepares call log records for import into a temporary...
  prepare-contacts  Extracts core contact fields from gds_file_path, and...
```

Basic example:

```
python cli.py prepare-contacts gds.csv healthintent.csv > contacts.csv

python cli.py prepare-calls calls.csv > clean-calls.csv
```

To preview the data, pass it to [csvlook][csvlook] and less:

```
python cli.py prepare-calls calls.csv | csvlook --no-inference | less --chop-long-lines
```

## Loading data

First, login to heroku by copying the URL from the following command into your browser.
```
heroku auth:login
```

Next, create the `tmp_calls` table.
```
heroku pg:psql --app <app-name> --file sql/create_tmp_calls_table.sql
```

Next, load `clean-calls.csv` into that table.
```
heroku pg:psql --app <app-name> --command "\COPY tmp_calls FROM clean-calls.csv DELIMITER ',' CSV HEADER"
```

You can verify it's been loaded in via the psql tool.

> Note: run export PAGER="less -S" first to support horizontal scrolling.
```
heroku pg:psql --app <app-name>
=> select * from tmp_calls;
```

[csvlook]: https://csvkit.readthedocs.io/en/latest/scripts/csvlook.html
