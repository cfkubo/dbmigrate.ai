-- GRANT ALTER ANY SESSION TO SYSTEM;

-- SELECT DBMS_METADATA.GET_DDL('TABLE', AIRLINE, 'DEMOARUL')
-- FROM all_tables
-- WHERE owner = 'DEMOARUL';


-- Oracle Stored Procedures for the Airline Database
-- Procedure to book a flight for a passenger
CREATE OR REPLACE PROCEDURE Book_Flight (
    p_flight_id IN NUMBER,
    p_passenger_id IN NUMBER,
    p_seat_number IN VARCHAR2
)
AS
    v_booking_id NUMBER;
BEGIN
    -- Check if the flight exists
    SELECT flight_id INTO v_booking_id FROM Flights WHERE flight_id = p_flight_id;

    -- Check if the passenger exists
    SELECT passenger_id INTO v_booking_id FROM Passengers WHERE passenger_id = p_passenger_id;

    -- Create the booking
    INSERT INTO Bookings (flight_id, passenger_id, seat_number)
    VALUES (p_flight_id, p_passenger_id, p_seat_number);

    COMMIT;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('Error: Invalid flight ID or passenger ID.');
        ROLLBACK;
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('An unexpected error occurred: ' || SQLERRM);
        ROLLBACK;
END Book_Flight;
/

-- Procedure to get the flight schedule for a given route
CREATE OR REPLACE PROCEDURE Get_Flight_Schedule (
    p_departure_airport IN CHAR,
    p_arrival_airport IN CHAR
)
AS
    CURSOR c_flights IS
        SELECT flight_number, departure_time, arrival_time, status
        FROM Flights
        WHERE departure_airport_id = p_departure_airport
          AND arrival_airport_id = p_arrival_airport
          AND status = 'Scheduled';
BEGIN
    DBMS_OUTPUT.PUT_LINE('Flight Schedule from ' || p_departure_airport || ' to ' || p_arrival_airport);
    DBMS_OUTPUT.PUT_LINE('--------------------------------------------------');
    FOR r_flight IN c_flights LOOP
        DBMS_OUTPUT.PUT_LINE(
            'Flight: ' || r_flight.flight_number ||
            ', Departs: ' || TO_CHAR(r_flight.departure_time, 'YYYY-MM-DD HH24:MI') ||
            ', Arrives: ' || TO_CHAR(r_flight.arrival_time, 'YYYY-MM-DD HH24:MI')
        );
    END LOOP;
    DBMS_OUTPUT.PUT_LINE('--------------------------------------------------');
END Get_Flight_Schedule;
/

-- Procedure to assign crew to a flight
CREATE OR REPLACE PROCEDURE Assign_Crew_To_Flight (
    p_flight_id IN NUMBER,
    p_employee_id IN NUMBER,
    p_crew_role IN VARCHAR2
)
AS
BEGIN
    INSERT INTO Flight_Crew (flight_id, employee_id, crew_role)
    VALUES (p_flight_id, p_employee_id, p_crew_role);

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Error assigning crew: ' || SQLERRM);
        ROLLBACK;
END Assign_Crew_To_Flight;
/
