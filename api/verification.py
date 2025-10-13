
import psycopg2
import os
import sqlparse
from typing import Optional
from api.database import get_verification_db_connection


def verify_procedure(sql_content: str | list[str]) -> tuple[bool, Optional[str], list[dict]]:
    """Tries to execute SQL content (string or list of statements) against the default PostgreSQL database."""
    all_results = []
    overall_success = True
    overall_error_message = None

    if isinstance(sql_content, str):
        statements_to_execute = [str(s).strip() for s in sqlparse.parse(sql_content) if str(s).strip()]
    else:
        statements_to_execute = sql_content

    try:
        print("Connecting to the verification database...")
        with get_verification_db_connection() as conn:
            print("Connection successful.")
            with conn.cursor() as cursor:
                print(f"Found {len(statements_to_execute)} statements to execute.")
                for i, statement_str in enumerate(statements_to_execute):
                    statement_result = {
                        'statement': statement_str,
                        'status': 'pending',
                        'error': None
                    }
                    if statement_str:
                        try:
                            print(f"Executing statement {i+1}: {statement_str[:100]}...")
                            cursor.execute(statement_str)
                            statement_result['status'] = 'success'
                        except psycopg2.Error as e:
                            print(f"Error executing statement {i+1}: {e}")
                            statement_result['status'] = 'failed'
                            statement_result['error'] = str(e)
                            overall_success = False
                            if not overall_error_message: # Store the first error as overall error
                                overall_error_message = str(e)
                    all_results.append(statement_result)
                
                if overall_success:
                    print("Committing the transaction...")
                    conn.commit()
                    print("Transaction committed.")
                else:
                    print("Transaction failed, rolling back...")
                    conn.rollback()
                    print("Transaction rolled back.")
        return overall_success, overall_error_message, all_results
    except psycopg2.Error as e:
        print(f"Error connecting or during transaction: {e}")
        # conn is managed by the context manager, so no need to manually rollback or close
        return False, str(e), all_results # Return current results even if connection fails


def verify_procedure_with_creds(sql_content: str | list[str], pg_creds: dict) -> tuple[bool, Optional[str], list[dict]]:
    """Tries to execute SQL content (string or list of statements) against a user-specified PostgreSQL database."""
    conn = None
    all_results = []
    overall_success = True
    overall_error_message = None

    if isinstance(sql_content, str):
        statements_to_execute = [str(s).strip() for s in sqlparse.parse(sql_content) if str(s).strip()]
    else:
        statements_to_execute = sql_content

    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(**pg_creds)
        print("Connection successful.")
        with conn.cursor() as cursor:
            print(f"Found {len(statements_to_execute)} statements to execute.")
            for i, statement_str in enumerate(statements_to_execute):
                statement_result = {
                    'statement': statement_str,
                    'status': 'pending',
                    'error': None
                }
                if statement_str:
                    try:
                        print(f"Executing statement {i+1}: {statement_str[:100]}...")
                        cursor.execute(statement_str)
                        statement_result['status'] = 'success'
                    except psycopg2.Error as e:
                        print(f"Error executing statement {i+1}: {e}")
                        statement_result['status'] = 'failed'
                        statement_result['error'] = str(e)
                        overall_success = False
                        if not overall_error_message: # Store the first error as overall error
                            overall_error_message = str(e)
                all_results.append(statement_result)
            
            if overall_success:
                print("Committing the transaction...")
                conn.commit()
                print("Transaction committed.")
            else:
                print("Transaction failed, rolling back...")
                conn.rollback()
                print("Transaction rolled back.")
        return overall_success, overall_error_message, all_results
    except psycopg2.Error as e:
        print(f"Error connecting or during transaction: {e}")
        if conn:
            conn.rollback()
            print("Transaction rolled back due to connection/transaction error.")
        return False, str(e), all_results # Return current results even if connection fails
    finally:
        if conn:
            conn.close()
            print("Connection closed.")
