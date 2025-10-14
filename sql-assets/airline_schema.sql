-- Oracle SQL Schema for an Airline Database
-- Change the current schema for the session to 'arul'


-- Countries Table
CREATE TABLE Countries (
    country_id NUMBER(2) PRIMARY KEY,
    country_name VARCHAR2(100) NOT NULL
);
/
-- Airports Table
CREATE TABLE Airports (
    airport_id NUMBER(3) PRIMARY KEY,
    airport_name NUMBER(100) NOT NULL,
    city VARCHAR2(100) NOT NULL,
    country_id NUMBER(2) NOT NULL,
    CONSTRAINT fk_airports_country FOREIGN KEY (country_id) REFERENCES Countries(country_id)
);
/
-- Airlines Table
CREATE TABLE Airlines (
    airline_id NUMBER PRIMARY KEY,
    airline_name VARCHAR2(100) NOT NULL,
    iata_code VARCHAR2(2) UNIQUE
);
/
-- Aircraft Table
CREATE TABLE Aircraft (
    aircraft_id NUMBER PRIMARY KEY,
    airline_id NUMBER NOT NULL,
    model VARCHAR2(100) NOT NULL,
    capacity NUMBER NOT NULL,
    CONSTRAINT fk_aircraft_airline FOREIGN KEY (airline_id) REFERENCES Airlines(airline_id)
);
/
-- Flights Table
CREATE TABLE Flights (
    flight_id NUMBER PRIMARY KEY,
    flight_number VARCHAR2(10) NOT NULL,
    airline_id NUMBER NOT NULL,
    aircraft_id NUMBER NOT NULL,
    departure_airport_id NUMBER(3) NOT NULL,
    arrival_airport_id NUMBER(3) NOT NULL,
    departure_time TIMESTAMP NOT NULL,
    arrival_time TIMESTAMP NOT NULL,
    status VARCHAR2(20) DEFAULT 'Scheduled' NOT NULL,
    CONSTRAINT fk_flights_airline FOREIGN KEY (airline_id) REFERENCES Airlines(airline_id),
    CONSTRAINT fk_flights_aircraft FOREIGN KEY (aircraft_id) REFERENCES Aircraft(aircraft_id),
    CONSTRAINT fk_flights_dep_airport FOREIGN KEY (departure_airport_id) REFERENCES Airports(airport_id),
    CONSTRAINT fk_flights_arr_airport FOREIGN KEY (arrival_airport_id) REFERENCES Airports(airport_id)
);
/
-- Passengers Table
CREATE TABLE Passengers (
    passenger_id NUMBER PRIMARY KEY,
    first_name VARCHAR2(100) NOT NULL,
    last_name VARCHAR2(100) NOT NULL,
    email VARCHAR2(100) UNIQUE NOT NULL,
    phone_number VARCHAR2(20),
    passport_number VARCHAR2(20) UNIQUE
);
/
-- Bookings Table
CREATE TABLE Bookings (
    booking_id NUMBER PRIMARY KEY,
    flight_id NUMBER NOT NULL,
    passenger_id NUMBER NOT NULL,
    booking_date DATE DEFAULT SYSDATE NOT NULL,
    seat_number VARCHAR2(4),
    status VARCHAR2(20) DEFAULT 'Confirmed' NOT NULL,
    CONSTRAINT fk_bookings_flight FOREIGN KEY (flight_id) REFERENCES Flights(flight_id),
    CONSTRAINT fk_bookings_passenger FOREIGN KEY (passenger_id) REFERENCES Passengers(passenger_id)
);
/
-- Boarding_Passes Table
CREATE TABLE Boarding_Passes (
    boarding_pass_id NUMBER PRIMARY KEY,
    booking_id NUMBER NOT NULL,
    gate VARCHAR2(5),
    boarding_time TIMESTAMP,
    CONSTRAINT fk_boarding_passes_booking FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id)
);
/
-- Employees Table
CREATE TABLE Employees (
    employee_id NUMBER PRIMARY KEY,
    first_name VARCHAR2(100) NOT NULL,
    last_name VARCHAR2(100) NOT NULL,
    role VARCHAR2(50) NOT NULL -- e.g., 'Pilot', 'Cabin Crew', 'Ground Staff'
);
/
-- Flight_Crew Table
CREATE TABLE Flight_Crew (
    flight_crew_id NUMBER PRIMARY KEY,
    flight_id NUMBER NOT NULL,
    employee_id NUMBER NOT NULL,
    crew_role VARCHAR2(50) NOT NULL, -- e.g., 'Captain', 'First Officer', 'Flight Attendant'
    CONSTRAINT fk_flight_crew_flight FOREIGN KEY (flight_id) REFERENCES Flights(flight_id),
    CONSTRAINT fk_flight_crew_employee FOREIGN KEY (employee_id) REFERENCES Employees(employee_id)
);
/