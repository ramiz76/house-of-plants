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
DATABASE_ENDPOINT=localhost | <AWS RDS endpoint address>
DATABASE_PASSWORD=XXXXXXXXXXX
ACCESS_KEY_ID=XXXXXXXXXXX
SECRET_ACCESS_KEY=XXXXXXXXXXX
BUCKET_NAME=<house-of-plants-long-term-storage>
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

## Database Schema

Star schema, with sensor_result as our fact table, storing each sensor reading from the API, and dimension tables containing info on plants and botanists from the museum.

<img src="/screenshots/Database_Schema_Screenshot.png" width="900" height="500" alt="Screenshot of Database Schema Diagram">

## Assumptions Made

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

The extract script extracts from the LMNH sensor API endpoint:

```
https://data-eng-plants-api.herokuapp.com/plants/{ID}
```

targeting IDs 0 through 50 - It is assumed that there are only 50 plants and that no plants will be added this week.

If the API returns a json response with an error, then the CSV file records that error so that we can do analysis on numbers and types of errors, and which endpoint these errors more frequently occur on.

## Transform

Some of the data was not recorded correctly in the API from the sensors, which meant that this data needed to be corrected with the transform script.

**Temperature**
Temperature that was too high was deleted as it was considered an outlier. Since the museum was in the UK, Liverpool, the temperature was decided to be deleted if it was below -10 and above 39 degrees Celcius.

**Last watered**
If last watered time in some data from sensors was later than the recording taken time - it was considered incorrect data and voided.

**Email and phone number**
Email and phone numbers were verified using Regex expressions to make sure the data is getting valid phone numbers and emails.

**Scientific name**
Scientific name extracted with extract.py was processed as a list even though none of the values turned out to be lists of values but always contained 0-1 scientific name. For that reason, the data was transformed to not include the list formatting when displaying the data.

**Recording taken**
Recording taken had missing time for the errors and some other received data. However, as noticed from manual tests, when the API is called, the recording taken was at the same time as the call itself. For that reason, it was decided that using cache with dataframe processing, those times would be replaced with the times from the previously processed data which _might_ cause some seconds to be slightly off on the recording taken but would show the recording taken time correct to the minute, rather than having the recorded time as empty.

**Soil Moisture**
Since moisture was said to be as a percentage - all data with moisture above 100 or below 0 was removed and assumed as incorrectly recorded data.

**Phone Numbers**
Some of the phone numbers were in the correct phone number format but instead of containing dashes ("-"), they had "." which were changed to be dashes and assumed to be correct.

## Load

Data is loaded in two formats, short term and long term.

#### Short Term

Data is pulled from the API once a minute by extract and transform. The short term load script also runs every minute, inserting the data created by extract and load into a Postgres database hosted on AWS's RDS.
This data remains on the database for roughly 24 hours before being pulled into long term storage.

#### Long Term

The long term load script runs every 3 hours, pulling all data older than 24 hours from the short term database (and deleting it there).

This data is appended to a csv file containing all data older than 24 hours, which is saved to an S3 bucket.

Each time the script is run (using an EventBridge scheduler), the existing file is downloaded from the S3 bucket (if a file doesnt exist, a blank file is made), then this file is combined with the newly retrieved 24hr old data file. This new file then replaces the old file on the S3 bucket.

## Visualisations

We use two visualisation tools for this repo, tableau for the short term data, streamlit for long term.

#### Short Term

Below are some screenshots of our tableau dashboard.


|                                                  Data on All Plants                                                   |                                         Data on just plants from the US                                          |
| :-------------------------------------------------------------------------------------------------------------------: | :--------------------------------------------------------------------------------------------------------------: |
| <img src="/screenshots/Tableau_Country_Stats.png" width="500" height="300" alt="Dashboard overview with country map"> | <img src="/screenshots/Tableau_US_Stats.png" width="500" height="300" alt="Dashboard overview with country map"> |

##### Hovering Gives More Information

|                                                  Soil Moisture by Hour                                                |                                         Plants Cared For by Botanist                                          |
| :-------------------------------------------------------------------------------------------------------------------: | :--------------------------------------------------------------------------------------------------------------: |
| <img src="/screenshots/Tableau_Soil_Moisture.png" width="500" height="260"> | <img src="/screenshots/Tableau_Botanist_Info.png" width="500" height="200"> |


#### Long Term

Run

```
streamlit run dashboard/dasboard-streamlit.py
```

to start streamlit dashboard. Ensure the streamlit script is targetting your long term data file, either on the s3 bucket or a version of it you've downloaded.

Below are screenshots from our latest run of the long term load code.

Plants By Region | Standard Deviation Temp By Region
:-------------------------:|:-------------------------:
<img src="/screenshots/Streamlit_Plants_By_Country.jpg" width="500" height="300" alt="Screenshot of Streamlit Plants By Country"> | <img src="/screenshots/Streamlit_Standard_Deviation.png" width="500" height="300" alt="Screenshot of Streamlit Standard Deviation Temp By Country">

|                                                   Mean Temp By Region                                                   |                                                    Median Temp By Region                                                    |
| :---------------------------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------: |
| <img src="/screenshots/Streamlit_Mean.png" width="500" height="300" alt="Screenshot of Streamlit Mean Temp By Country"> | <img src="/screenshots/Streamlit_Median.png" width="500" height="300" alt="Screenshot of Streamlit Median Temp By Country"> |

