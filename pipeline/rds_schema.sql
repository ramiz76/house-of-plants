DROP TABLE IF EXISTS sensor_result;
DROP TABLE IF EXISTS plant;
DROP TABLE IF EXISTS origin;
DROP TABLE IF EXISTS botanist;
DROP TABLE IF EXISTS plant_availability;


CREATE TABLE origin(
    origin_id INT GENERATED ALWAYS AS IDENTITY,
    longitude FLOAT UNIQUE,
    latitude FLOAT UNIQUE,
    country TEXT,
    continent TEXT,
    PRIMARY KEY (origin_id)
);


CREATE TABLE plant(
    plant_id INT GENERATED ALWAYS AS IDENTITY,
    origin_id INT,
    api_id INT UNIQUE,
    plant_name TEXT,
    scientific_name TEXT,
    cycle TEXT,
    sunlight TEXT,
    PRIMARY KEY (plant_id),
    FOREIGN KEY (origin_id) REFERENCES origin(origin_id)
);


CREATE TABLE botanist(
    botanist_id INT GENERATED ALWAYS AS IDENTITY,
    name TEXT,
    email TEXT,
    phone TEXT UNIQUE,
    PRIMARY KEY (botanist_id)
);


CREATE TABLE plant_availability(
    availability_id INT GENERATED ALWAYS AS IDENTITY,
    type_of_availability TEXT UNIQUE,
    PRIMARY KEY (availability_id)
);

-- Currently these are the only errors/availability results
INSERT INTO plant_availability (type_of_availability) VALUES ('Available');
INSERT INTO plant_availability (type_of_availability) VALUES ('plant on loan to another museum');
INSERT INTO plant_availability (type_of_availability) VALUES ('plant not found');
INSERT INTO plant_availability (type_of_availability) VALUES ('Timeout: The request could not be completed.');
INSERT INTO plant_availability (type_of_availability) VALUES ('Missing field in data.');
INSERT INTO plant_availability (type_of_availability) VALUES ('Missing soil_moisture reading.');
INSERT INTO plant_availability (type_of_availability) VALUES ('Missing temperature reading.');




CREATE TABLE sensor_result(
    result_id INT GENERATED ALWAYS AS IDENTITY,
    botanist_id INT,
    availability_id INT,
    plant_id INT,
    last_watered TIMESTAMP,
    soil_moisture FLOAT,
    temperature FLOAT,
    recording_taken TIMESTAMP,
    PRIMARY KEY (result_id),
    FOREIGN KEY (botanist_id) REFERENCES botanist(botanist_id),
    FOREIGN KEY (availability_id) REFERENCES plant_availability(availability_id),
    FOREIGN KEY (plant_id) REFERENCES plant(plant_id)
);

