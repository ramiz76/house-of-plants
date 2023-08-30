"""Pipeline script that combines all the extract, transform and load scripts"""

from extract import extract_and_create_csv
from transform import transform_script

if __name__ == "__main__":

    extract_and_create_csv()
    transform_script()
