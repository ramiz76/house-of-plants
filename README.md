# House of Plants

Monitoring the health of plants for Liverpool Natural History Museum

## Setup - Local

1. Clone this repo.
2. Activate a new virtual environment.
3. Run `pip install -r requirements.txt`
4. Create .env file, containing environment variables:

```
DATABASE_NAME=<plants>
DATABASE_USERNAME=<your username>
DATABASE_ENDPOINT=localhost
DATABASE_PASSWORD=XXXXXXXXXXX
```

5. Create a local database with psql with the name you chose in your .env, e.g. plants.
6. Run the schema file with psql to create the tables and initial data in the local database.
7. Run `python pipeline.py` to manually run the pipeline from start to finish, once.

8. (optionally) set up a cron task to run pipeline.py on a schedule.

## Setup - Cloud

Cloud resources are created on AWS using Terraform.
As above with a few differences:

- Terraform apply to create cloud resources.
- Environment file should contain the address of the database on the cloud.
- Run schema file to set up tables on cloud db.
- Use scp or similar to transfer the streamlit app to EC2.
- Start streamlit app to view visualisations online.
- TODO - document any parts of the cloud setup that are manual

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

## Extract

The extract script extracts from the following URL : "https://data-eng-plants-api.herokuapp.com/plants/ID".
It is assumed that there are only 50 plants and that no plants can be added.
The extract script reaches every endpoint with the ID from 0 to 50.

If the API returns a json response with an error, then the CSV file records that error.

## Transform

**Phone Numbers**
Assuming that the phone numbers extracted that contain '.' in the middle of the numbers are phone numbers and these dots are replaced with dashes.

## Load

Data is loaded in two formats, short term and long term.

#### Short Term

Data is pulled from the API once a minute by extract and transform. The short term load script also runs every minute, inserting the data created by extract and load into a Postgres database hosted on AWS's RDS.
This data remains on the database for roughly 24 hours before being pulled into long term storage.

#### Long Term

The long term load script runs every X hours, pulling all data older than 24 hours from the short term database (and deleting it there)

This data is appended to a csv file containing all data older than 24 hours, which is saved to an S3 bucket.

## Visualisations

We use two visualisation tools for this repo, tableau for the short term data, streamlit for long term.

#### Short Term

Below are some screenshots of our tableau dashboard.

#### Long Term

As mentioned in cloud setup, once Streamlit is up and running, you will be able to view visualisations of all the long term data.
