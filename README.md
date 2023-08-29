# House of Plants

Monitoring the health of plants for Liverpool Natural History Museum

## Setup - Local

- Clone repo
- Activate venv
- Run `pip install -r requirements.txt`
- Create .env file, containing environment variables
- Create a local database with psql
- Run the schema file with psql to create tables in the local db
- Run pipeline.py to manually run once

## Setup - Cloud

As above with a few differences:

- Terraform apply to create cloud resources
- Use cron to run main.py / pipeline.py / sh script every minute
- Run schema file to set up tables on cloud db

## Assumptions we've made

- Sunlight refers to the level of sunlight the plant wants
- Information about the plant itself is not expected to change

### Extract

### Transform

### Load

### Visualisations
