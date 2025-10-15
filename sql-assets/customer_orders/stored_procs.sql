-- Stored Procedures for Customer Orders (CO) Schema
ALTER SESSION SET CURRENT_SCHEMA = CO; 

-- Procedure to add a new customer
CREATE OR REPLACE PROCEDURE add_customer (
    p_email_address IN VARCHAR2,
    p_full_name     IN VARCHAR2
) AS
BEGIN
    INSERT INTO customers (email_address, full_name)
    VALUES (p_email_address, p_full_name);
    COMMIT;
END add_customer;
/

-- Procedure to get orders for a specific customer
CREATE OR REPLACE PROCEDURE get_customer_orders (
    p_customer_id IN INTEGER
) AS
    CURSOR c_orders IS
        SELECT order_id, order_tms, order_status, store_id
        FROM orders
        WHERE customer_id = p_customer_id
        ORDER BY order_tms DESC;
BEGIN
    FOR order_rec IN c_orders LOOP
        DBMS_OUTPUT.PUT_LINE(
            'Order ID: ' || order_rec.order_id ||
            ', Status: ' || order_rec.order_status ||
            ', Date: ' || TO_CHAR(order_rec.order_tms, 'YYYY-MM-DD HH24:MI:SS')
        );
    END LOOP;
END get_customer_orders;
/

-- Procedure to create a new order
-- This is a simplified version. A real-world scenario would be more complex
-- and might involve a temporary shopping cart table.
CREATE OR REPLACE PROCEDURE create_order (
    p_customer_id IN INTEGER,
    p_store_id    IN INTEGER,
    p_order_items IN "SYS"."ODCINUMBERLIST" -- Array of product_ids
) AS
    v_order_id INTEGER;
    v_unit_price products.unit_price%TYPE;
BEGIN
    -- Insert into orders table
    INSERT INTO orders (order_tms, customer_id, order_status, store_id)
    VALUES (CURRENT_TIMESTAMP, p_customer_id, 'OPEN', p_store_id)
    RETURNING order_id INTO v_order_id;

    -- Loop through items and add them to order_items
    FOR i IN 1..p_order_items.COUNT LOOP
        -- Get product unit price
        SELECT unit_price INTO v_unit_price
        FROM products
        WHERE product_id = p_order_items(i);

        -- Insert into order_items
        INSERT INTO order_items (order_id, line_item_id, product_id, unit_price, quantity)
        VALUES (v_order_id, i, p_order_items(i), v_unit_price, 1); -- Assuming quantity of 1 for simplicity
    END LOOP;

    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Created Order ID: ' || v_order_id);
END create_order;
/

-- Procedure to update the status of an order
CREATE OR REPLACE PROCEDURE update_order_status (
    p_order_id    IN INTEGER,
    p_new_status  IN VARCHAR2
) AS
    v_allowed_status BOOLEAN := FALSE;
BEGIN
    -- Validate status
    IF p_new_status IN ('CANCELLED','COMPLETE','OPEN','PAID','REFUNDED','SHIPPED') THEN
        v_allowed_status := TRUE;
    END IF;

    IF v_allowed_status THEN
        UPDATE orders
        SET order_status = p_new_status
        WHERE order_id = p_order_id;
        COMMIT;
    ELSE
        RAISE_APPLICATION_ERROR(-20001, 'Invalid order status: ' || p_new_status);
    END IF;
END update_order_status;
/
