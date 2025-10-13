-- Successful Conversions --
/
CREATE OR REPLACE FUNCTION emp_period_of_service_year(p_emp_id integer) RETURNS integer AS $$
DECLARE
    v_period_of_service_years integer;
BEGIN
    SELECT EXTRACT(year FROM current_date)::int - EXTRACT(year FROM hire_date)::int
    INTO v_period_of_service_years
    FROM employees
    WHERE employee_id = p_emp_id;
    RETURN v_period_of_service_years;
END;
$$ LANGUAGE plpgsql;
/
CREATE OR REPLACE PROCEDURE get_artist_by_album(p_artist_id text) AS $$
BEGIN
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE cust_invoice_by_year_analyze() AS $$
BEGIN
END;
$$ LANGUAGE plpgsql;
/
CREATE OR REPLACE FUNCTION total_emp_sal_by_years(p_hire_date date, p_current_sal numeric)
RETURNS numeric
LANGUAGE plpgsql
AS $$
DECLARE
    v_years_of_service numeric;
    v_total_sal_by_years numeric;
BEGIN
    SELECT EXTRACT(YEAR FROM current_date) - EXTRACT(YEAR FROM p_hire_date) INTO v_years_of_service;
    v_total_sal_by_years := p_current_sal * v_years_of_service;
    RETURN v_total_sal_by_years;
END;
$$;