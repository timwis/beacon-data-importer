# Beacon data importer
Convert person data to a CSV format that can easily be imported
to Beacon's database.

## Installation

Ensure you have Python 3.7+ installed on your machine.

```
pip3 install "git+https://github.com/timwis/beacon-data-importer#egg=beacon-data-importer"
```

## Usage

```bash
Usage: beacon [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  prepare-calls     Prepares call log records for import into a temporary...
  prepare-contacts  Extracts core contact fields from gds_file_path, and...
```

> Tip: To preview the data, pass it to [csvlook][csvlook] and less:
>
> ```
> beacon <cmd> <file> | csvlook --no-inference | less --chop-long-lines
> # aka:
> beacon <cmd> <file> | csvlook -I | less -S
> ```

## Authentication

We'll use the heroku CLI to interact with the database. Login to heroku by copying the URL from the following command into your browser.

```bash
heroku auth:login
```

## Contacts

Prepare the data for import using the `beacon` CLI tool.

```bash
beacon prepare-contacts gds.csv healthintent.csv > contacts.csv
```

Load `contacts.csv` into the `contacts` table, which should already be created by the application's migrations.

```bash
heroku pg:psql --app <app-name> --command "\COPY contacts (nhs_number, first_name, middle_names, surname, address, postcode, telephone, mobile, date_of_birth, created_at, updated_at, gds_import_data, healthintent_import_data) FROM contacts.csv DELIMITER ',' CSV HEADER"
```

## Call logs

Prepare the data for import using the `beacon` CLI tool.

```bash
beacon prepare-calls calls.csv > clean-calls.csv
```

Create the `tmp_calls` table.

```bash
heroku pg:psql --app <app-name> --file sql/create_tmp_calls_table.sql
```

Load `clean-calls.csv` into that table.

```bash
heroku pg:psql --app <app-name> --command "\COPY tmp_calls (shielded_id, latest_attempt_date, body, import_data) FROM clean-calls.csv DELIMITER ',' CSV HEADER"
```

You can verify it's been loaded in via the psql tool. Use `\q` to quit.

> Note: run export PAGER="less -S" first to support horizontal scrolling.

```bash
heroku pg:psql --app <app-name>
=> select * from tmp_calls;
```

Convert the imported calls to needs and notes records.

```bash
heroku pg:psql --app <app-name> --file sql/convert_calls_to_needs_and_notes.sql
```

Remove the temporary calls table you created.

```bash
heroku pg:psql --app <app-name> --command "DROP TABLE tmp_calls"
```

[csvlook]: https://csvkit.readthedocs.io/en/latest/scripts/csvlook.html
