-- Oracle SQL Insert Statements for Airline Database
-- Countries
INSERT INTO Countries (country_id, country_name) VALUES ('US', 'United States');
INSERT INTO Countries (country_id, country_name) VALUES ('GB', 'United Kingdom');
INSERT INTO Countries (country_id, country_name) VALUES ('JP', 'Japan');

-- Airports
INSERT INTO Airports (airport_id, airport_name, city, country_id) VALUES ('JFK', 'John F. Kennedy International Airport', 'New York', 'US');
INSERT INTO Airports (airport_id, airport_name, city, country_id) VALUES ('LAX', 'Los Angeles International Airport', 'Los Angeles', 'US');
INSERT INTO Airports (airport_id, airport_name, city, country_id) VALUES ('LHR', 'Heathrow Airport', 'London', 'GB');
INSERT INTO Airports (airport_id, airport_name, city, country_id) VALUES ('HND', 'Haneda Airport', 'Tokyo', 'JP');

-- Airlines
INSERT INTO Airlines (airline_id, airline_name, iata_code) VALUES (1, 'American Airlines', 'AA');
INSERT INTO Airlines (airline_id, airline_name, iata_code) VALUES (2, 'British Airways', 'BA');
INSERT INTO Airlines (airline_id, airline_name, iata_code) VALUES (3, 'Japan Airlines', 'JL');

-- Aircraft
INSERT INTO Aircraft (aircraft_id, airline_id, model, capacity) VALUES (101, 1, 'Boeing 777', 300);
INSERT INTO Aircraft (aircraft_id, airline_id, model, capacity) VALUES (102, 1, 'Airbus A320', 180);
INSERT INTO Aircraft (aircraft_id, airline_id, model, capacity) VALUES (201, 2, 'Boeing 787', 250);
INSERT INTO Aircraft (aircraft_id, airline_id, model, capacity) VALUES (301, 3, 'Airbus A350', 320);

-- Flights
INSERT INTO Flights (flight_id, flight_number, airline_id, aircraft_id, departure_airport_id, arrival_airport_id, departure_time, arrival_time)
VALUES (1001, 'AA100', 1, 101, 'JFK', 'LHR', TO_TIMESTAMP('2025-10-20 20:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2025-10-21 08:00:00', 'YYYY-MM-DD HH24:MI:SS'));
INSERT INTO Flights (flight_id, flight_number, airline_id, aircraft_id, departure_airport_id, arrival_airport_id, departure_time, arrival_time)
VALUES (1002, 'BA282', 2, 201, 'LHR', 'LAX', TO_TIMESTAMP('2025-10-22 11:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2025-10-22 14:00:00', 'YYYY-MM-DD HH24:MI:SS'));
INSERT INTO Flights (flight_id, flight_number, airline_id, aircraft_id, departure_airport_id, arrival_airport_id, departure_time, arrival_time)
VALUES (1003, 'JL005', 3, 301, 'HND', 'JFK', TO_TIMESTAMP('2025-10-25 10:30:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2025-10-25 09:30:00', 'YYYY-MM-DD HH24:MI:SS'));

-- Passengers
INSERT INTO Passengers (passenger_id, first_name, last_name, email, passport_number) VALUES (1, 'John', 'Smith', 'john.smith@example.com', 'A12345678');
INSERT INTO Passengers (passenger_id, first_name, last_name, email, passport_number) VALUES (2, 'Jane', 'Doe', 'jane.doe@example.com', 'B87654321');

-- Bookings
INSERT INTO Bookings (booking_id, flight_id, passenger_id, seat_number) VALUES (1, 1001, 1, '12A');
INSERT INTO Bookings (booking_id, flight_id, passenger_id, seat_number) VALUES (2, 1002, 2, '22B');

-- Employees
INSERT INTO Employees (employee_id, first_name, last_name, role) VALUES (10, 'William', 'Turner', 'Pilot');
INSERT INTO Employees (employee_id, first_name, last_name, role) VALUES (11, 'Elizabeth', 'Swann', 'Pilot');
INSERT INTO Employees (employee_id, first_name, last_name, role) VALUES (20, 'Jack', 'Sparrow', 'Cabin Crew');

-- Flight Crew
INSERT INTO Flight_Crew (flight_crew_id, flight_id, employee_id, crew_role) VALUES (1, 1001, 10, 'Captain');
INSERT INTO Flight_Crew (flight_crew_id, flight_id, employee_id, crew_role) VALUES (2, 1001, 11, 'First Officer');
INSERT INTO Flight_Crew (flight_crew_id, flight_id, employee_id, crew_role) VALUES (3, 1001, 20, 'Flight Attendant');

COMMIT;
