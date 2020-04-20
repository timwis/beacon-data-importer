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
heroku pg:psql --app <app-name> --command "\COPY contacts (nhs_number, first_name, middle_names, surname, address, postcode, telephone, mobile, date_of_birth, created_at, updated_at, gds_import_data) FROM contacts.csv DELIMITER ',' CSV HEADER"
```

## Call logs

Prepare the data for import using the `beacon` CLI tool.

```bash
beacon prepare-calls --food-needs-user USER --complex-needs-user USER --simple-needs-user USER --output-dir ./output calls.csv
```

Create the temporary loading tables.

```bash
heroku pg:psql --app <app-name> --file sql/create_tmp_tables.sql
```

Load prepared files into the temporary loading tables.

```bash
heroku pg:psql --app <app-name> --command "\COPY tmp_original_triage_needs (nhs_number, category, name, created_at, updated_at, completed_on) FROM original_triage_needs.csv DELIMITER ',' CSV HEADER"
heroku pg:psql --app <app-name> --command "\COPY tmp_original_triage_notes (nhs_number, category, body, created_at, updated_at, import_data) FROM original_triage_notes.csv DELIMITER ',' CSV HEADER"
heroku pg:psql --app <app-name> --command "\COPY tmp_identified_needs (nhs_number, category, name, created_at, updated_at, completed_on, supplemental_data, user_id) FROM food_needs.csv DELIMITER ',' CSV HEADER"
heroku pg:psql --app <app-name> --command "\COPY tmp_identified_needs (nhs_number, category, name, created_at, updated_at, start_on) FROM callback_needs.csv DELIMITER ',' CSV HEADER"
heroku pg:psql --app <app-name> --command "\COPY tmp_identified_needs (nhs_number, category, name, created_at, updated_at, user_id) FROM remaining_needs.csv DELIMITER ',' CSV HEADER"
heroku pg:psql --app <app-name> --command "\COPY tmp_contact_profile_updates (nhs_number, additional_info, delivery_details, dietary_details, has_covid_symptoms) FROM contact_profile_updates.csv DELIMITER ',' CSV HEADER"
```

You can verify it's been loaded in via the psql tool. Use `\q` to quit.

> Note: run export PAGER="less -S" first to support horizontal scrolling.

```bash
heroku pg:psql --app <app-name>
=> select * from tmp_original_triage_needs;
```

Import the data from the temporary loading tables into the application tables.

```bash
heroku pg:psql --app <app-name> --file sql/import_original_triage_needs_and_notes.sql
heroku pg:psql --app <app-name> --file sql/import_identified_needs.sql
heroku pg:psql --app <app-name> --file sql/import_contact_profile_updates.sql
```

Remove the temporary calls table you created.

```bash
heroku pg:psql --app <app-name> --command "DROP TABLE tmp_original_triage_needs, tmp_original_triage_notes, tmp_identified_needs, tmp_contact_profile_updates"
```

[csvlook]: https://csvkit.readthedocs.io/en/latest/scripts/csvlook.html
