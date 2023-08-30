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

## Assumptions made

- No two plants have the same origin latitude but different longitude or vice versa (Using each as a unique constraint in the schema)
- Sunlight refers to the level of sunlight the plant wants
- Information about the plant itself is not expected to change
- We have noticed some botanists have multiple phone numbers - we're still assuming they only have one email
- The following information will always exist (assumption made from manual tests):
  - plant_name
  - api_id
  - longitude
  - latitude
  - country
  - continent
  - botanist_name
  - email
  - phone

### Extract

The extract script extracts from the following URL : "https://data-eng-plants-api.herokuapp.com/plants/ID".
It is assumed that there are only 50 plants and that no plants can be added.
The extract script reaches every endpoint with the ID from 0 to 50.

If the API returns a json response with an error, then the CSV file records that error.

### Transform

**Phone Numbers**
Assuming that the phone numbers extracted that contain '.' in the middle of the numbers are phone numbers and these dots are replaced with dashes.

### Load

### Visualisations
