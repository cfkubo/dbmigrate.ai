import logging
import ollama
import re
import os
from typing import Optional, List
import json # Moved json import to the top

logging.basicConfig(level=logging.INFO)

def get_running_model_name():
    """
    Returns the name of the first running Ollama model found.
    """
    try:
        models = ollama.ps()["models"]
        if models:
            # Note: ollama.ps() is typically used to show running models,
            # but in older versions or specific setups, it might show all models.
            # Assuming 'models' contains a list of models with 'name' key.
            return models[0]["name"]
        return None
    except Exception as e:
        # It's better to catch the specific exception (e.g., ConnectionError from requests)
        # that ollama might wrap, but a general Exception works for a robust check.
        raise RuntimeError(f"Error communicating with Ollama, is it running? Full error: {e}") from e

# --- FIX APPLIED HERE: Variable initialization moved inside function body ---
# def convert_oracle_to_postgres(oracle_sql: str, suggestions: Optional[List[str]] = None):
#     print("####### Starting conversion using Ollama from convert_oracle_to_postgres def ####### ..." )
#     """Converts an Oracle stored procedure to PostgreSQL syntax using Ollama.

#     Args:
#         oracle_sql: The Oracle stored procedure to convert.
#         suggestions: Optional list of strings with conversion suggestions.
#     """
#     # **FIX: These lines must be inside the function body**
#     model_name = os.getenv("OLLAMA_MODEL_NAME")
#     if not model_name:
#         model_name = get_running_model_name()
#         if not model_name:
#             raise RuntimeError("No Ollama model is currently running. Please run a model to start it.")

#     # Assuming sanitize_sql is available and works as intended
#     # It's good practice to ensure the input is a string before sanitizing
#     oracle_sql = sanitize_sql(str(oracle_sql))

#     prompt = f"""You are an Oracle SQL and Postgres SQL expert agent. Convert the following Oracle stored procedure to PostgreSQL PL/pgSQL syntax.
#     Your response should only be the converted psql code without any comment and characters that are not psql compatible. Do not add comments and only send the psql output and error if encountered Do not include any other text, explanations, or apologies.
#     Important: All SQL keywords in the output must be in lowercase (e.g., `create or replace function`, `language plpgsql`, `begin`, `end`).
#     Pay close attention to the procedure signature. Oracle's `CREATE OR REPLACE PROCEDURE procedure_name AS` must be converted to PostgreSQL's `CREATE OR REPLACE FUNCTION function_name() RETURNS void LANGUAGE plpgsql AS $$`.

#     Oracle SQL:
#     {oracle_sql}

#     {f"Consider the following suggestions for improvement: {' '.join(suggestions)}" if suggestions else ""}

#     PostgreSQL PL/pgSQL:"""

#     try:
#         stream = ollama.generate(model=model_name, prompt=prompt, stream=True)
#         for chunk in stream:
#             yield chunk['response'].lower() # Ensure the output is in lowercase
#             print(chunk['response'], end='', flush=True)  # Print to console as it streams
#     except Exception as e:
#         raise RuntimeError(f"Error communicating with Ollama: {e}") from e


def convert_ddl(source_ddl: str, source_db_type: str, target_db_type: str, suggestions: Optional[List[str]] = None):
    print(f"####### Starting conversion from {source_db_type} to {target_db_type} using Ollama ####### ...")
    """Converts a block of SQL (DDL, DML, or PL/SQL) from a source to a target database syntax.

    Args:
        source_ddl: The source SQL block to convert.
        source_db_type: The source database type (e.g., 'oracle', 'mysql').
        target_db_type: The target database type (e.g., 'postgres').
        suggestions: Optional list of strings with conversion suggestions.
    """
    # --- Model Setup ---
    model_name = os.getenv("OLLAMA_MODEL_NAME")
    if not model_name:
        model_name = get_running_model_name()
        if not model_name:
            raise RuntimeError("No Ollama model is currently running. Please run a model to start it.")

    # --- Prompt Selection ---
    prompts = {
        ("oracle", "postgres"): f"""
            you are an oracle sql and postgresql expert. your sole task is to accurately convert the provided oracle sql (which may be ddl, dml, or pl/sql) into equivalent, idiomatic postgresql syntax.

            your output must consist of **only** the converted psql code. do not include any comments, explanations, apologies, leading text, or anything that is not valid postgresql.

            pay special attention to these common conversions:
            1. handle `uuidd`, `to_date`, `nvl`, `sysdate`, and other built-in function differences.
            2. convert oracle's `create or replace procedure` or `create or replace function` syntax to postgres' `create or replace function...language plpgsql as $$` structure.
            3. replace oracle data types (e.g., `varchar2`, `number`) with their postgres equivalents (e.g., `varchar`, `numeric` or `int`).


            oracle sql to convert:
            {source_ddl}

            {f"additional conversion notes/suggestions: {' '.join(suggestions)}" if suggestions else ""}

            postgresql result:
        """,
        ("mysql", "postgres"): f"""
            you are a mysql and postgresql expert. your sole task is to accurately convert the provided mysql sql (which may be ddl, dml, or stored procedures) into equivalent, idiomatic postgresql syntax.

            your output must consist of **only** the converted psql code. do not include any comments, explanations, apologies, leading text, or anything that is not valid postgresql.

            pay special attention to these common conversions:
            1. handle `auto_increment` by using `serial` or `bigserial` columns in postgres.
            2. convert mysql data types (e.g., `datetime`, `tinyint`, `double`) to their postgres equivalents (e.g., `timestamp`, `smallint`, `double precision`).
            3. replace mysql-specific functions like `now()` or `ifnull()` with their postgres counterparts (`current_timestamp`, `coalesce`).
            4. correctly handle backticks for identifiers in mysql, which are not standard in postgres (use double quotes if needed, or nothing if not required).
            5. convert `create procedure` or `create function` syntax, paying attention to `delimiter` changes and the function body.

            mysql sql to convert:
            {source_ddl}

            {f"additional conversion notes/suggestions: {' '.join(suggestions)}" if suggestions else ""}

            postgresql result:
        """,
        ("sqlserver", "postgres"): f"""
            you are a sql server (t-sql) and postgresql expert. your sole task is to accurately convert the provided t-sql (which may be ddl, dml, or stored procedures) into equivalent, idiomatic postgresql syntax.

            your output must consist of **only** the converted psql code. do not include any comments, explanations, apologies, leading text, or anything that is not valid postgresql.

            pay special attention to these common conversions:
            1. handle `identity` columns by using `serial` or `bigserial` columns in postgres.
            2. convert sql server data types (e.g., `datetime2`, `bit`, `money`) to their postgres equivalents (e.g., `timestamp`, `boolean`, `numeric`).
            3. replace sql server-specific functions like `getdate()` or `isnull()` with their postgres counterparts (`current_timestamp`, `coalesce`).
            4. correctly handle `[]` for identifiers in sql server, which are not standard in postgres (use double quotes if needed, or nothing if not required).
            5. convert `create procedure` or `create function` syntax, paying attention to the function body and the use of `@@` variables.

            t-sql to convert:
            {source_ddl}

            {f"additional conversion notes/suggestions: {' '.join(suggestions)}" if suggestions else ""}

            postgresql result:
        """,
        ("teradata", "postgres"): f"""
            you are a teradata and greenplum/postgresql expert. your sole task is to accurately convert the provided teradata sql (which may be ddl, dml, or macros) into equivalent, idiomatic postgresql syntax suitable for greenplum.

            your output must consist of **only** the converted psql code. do not include any comments, explanations, apologies, leading text, or anything that is not valid postgresql.

            pay special attention to these common conversions:
            1. handle teradata's `set` tables, which enforce unique rows, and `multiset` tables. greenplum does not have a direct `set` equivalent, so note this or convert to a table with a unique index.
            2. convert teradata data types (e.g., `char`, `decimal`, `byteint`) to their postgres equivalents (e.g., `char`, `numeric`, `smallint`).
            3. replace teradata-specific functions like `index` or `substr` with their postgres counterparts (`strpos`, `substring`).
            4. handle teradata's `bt` and `et` for transactions, which is different from postgres's `begin` and `commit`.
            5. convert teradata macros to postgresql functions.

            teradata sql to convert:
            {source_ddl}

            {f"additional conversion notes/suggestions: {' '.join(suggestions)}" if suggestions else ""}

            postgresql result:
        """,
        ("db2", "postgres"): f"""
            you are an ibm db2 and postgresql expert. your sole task is to accurately convert the provided db2 sql (which may be ddl, dml, or sql pl) into equivalent, idiomatic postgresql syntax.

            your output must consist of **only** the converted psql code. do not include any comments, explanations, apologies, leading text, or anything that is not valid postgresql.

            pay special attention to these common conversions:
            1. handle db2's `generated by default as identity` columns by using `serial` or `bigserial` columns in postgres.
            2. convert db2 data types (e.g., `varchar`, `decimal`, `timestamp`) to their postgres equivalents.
            3. replace db2-specific functions and registers like `current date` or `coalesce` with their postgres counterparts (`current_date`, `coalesce`).
            4. convert db2 stored procedures to postgresql functions, paying close attention to the declaration of variables and the overall block structure.

            db2 sql to convert:
            {source_ddl}

            {f"additional conversion notes/suggestions: {' '.join(suggestions)}" if suggestions else ""}

            postgresql result:
        """
    }

    prompt = prompts.get((source_db_type.lower(), target_db_type.lower()))
    if not prompt:
        raise ValueError(f"Conversion from {source_db_type} to {target_db_type} is not supported.")

    # We convert the prompt to lowercase here primarily to set the *tone* # and *style* for the LLM, but we don't rely on it for enforcement.
    prompt = prompt.strip().lower()

    # --- Ollama Generation and Lowercase Enforcement ---
    try:
        stream = ollama.generate(model=model_name, prompt=prompt, stream=True)
        for chunk in stream:
            # THIS IS WHERE THE CRITICAL ENFORCEMENT HAPPENS
            response_text = chunk['response'].lower()
            yield response_text
            print(response_text, end='', flush=True)  # Print to console as it streams
    except Exception as e:
        raise RuntimeError(f"error communicating with ollama: {e}") from e




def compare_schemas_with_ollama_ai(oracle_ddl: str, postgres_ddl: str, data_migration_mode: bool = False) -> tuple[bool, list[str]]:
    """Compares Oracle and PostgreSQL DDLs for migration compatibility using Ollama.

    Args:
        oracle_ddl: The Oracle DDL string.
        postgres_ddl: The PostgreSQL DDL string.
        data_migration_mode: If True, only checks column name compatibility (ignoring case).

    Returns:
        A tuple: (is_compatible: bool, issues: list[str])
    """

    # ... (docstring and initial checks remain the same) ...

    model_name = os.getenv("OLLAMA_MODEL_NAME")
    if not model_name:
        model_name = get_running_model_name()
        if not model_name:
            raise RuntimeError("No Ollama model is currently running. Please run a model to start it.")

    # Optional: Sanitize DDLs before sending to AI, though not strictly required
    # oracle_ddl = sanitize_sql(str(oracle_ddl))
    # postgres_ddl = sanitize_sql(str(postgres_ddl))

    if data_migration_mode:
        prompt = f"""You are an expert in Oracle SQL and PostgreSQL PL/pgSQL. Your task is to compare two database table DDLs, one from Oracle and one from PostgreSQL, and determine if they are compatible for data migration. For data migration, we are only concerned with the compatibility of column names.

        Provide your response in a JSON format with two keys:
        - "is_compatible": boolean (true if compatible, false otherwise)
        - "issues": array of strings (list any identified incompatibilities or differences in column names, ignoring case, or an empty array if compatible)

        Oracle DDL:
        {oracle_ddl}

        PostgreSQL DDL:
        {postgres_ddl}

        JSON Response:
        """
    else:
        # ALL the prompt text must be inside the triple quotes (f-string)
        prompt = f"""You are an expert in Oracle SQL and PostgreSQL PL/pgSQL. Your task is to compare two database table DDLs, one from Oracle and one from PostgreSQL, and determine if they are compatible for migration.

        Consider the following aspects for compatibility:
        - Data types (e.g., NUMBER vs INTEGER/NUMERIC, VARCHAR2 vs VARCHAR, DATE vs TIMESTAMP)
        - Constraints (e.g., PRIMARY KEY, UNIQUE, NOT NULL, FOREIGN KEY)
        - Default values
        - Column order (less critical but note if different)
        - Any Oracle-specific features that do not have a direct PostgreSQL equivalent.

        Provide your response in a JSON format with two keys:
        - "is_compatible": boolean (true if compatible, false otherwise)
        - "issues": array of strings (list any identified incompatibilities or differences, or an empty array if compatible)

        Oracle DDL:
        {oracle_ddl}

        PostgreSQL DDL:
        {postgres_ddl}

        JSON Response:
        """

    try:
        full_response = ""
        stream = ollama.generate(model=model_name, prompt=prompt, stream=True)
        for chunk in stream:
            full_response += chunk['response']

        # Attempt to parse the JSON response

        # Extract JSON from markdown code block if present
        json_match = re.search(r"```json\n([\s\S]*?)\n```", full_response)
        if json_match:
            json_string = json_match.group(1).strip() # .strip() to remove leading/trailing whitespace
        else:
            json_string = full_response.strip() # Assume it's pure JSON if no markdown block

        try:
            ai_response = json.loads(json_string)
            is_compatible = ai_response.get("is_compatible", False)
            # Default for issues is an empty list if not present, which is better than a hardcoded error message
            issues = ai_response.get("issues", [])

            if not isinstance(issues, list):
                # If 'issues' is not a list (e.g., a string describing an error), wrap it.
                issues = [str(issues)]

            # Additional check if 'is_compatible' is present and is a boolean
            if not isinstance(is_compatible, bool):
                 logging.warning(f"AI response 'is_compatible' was not a boolean: {is_compatible}. Defaulting to False.")
                 is_compatible = False
                 if not issues: # Add an issue if the primary flag is broken and no other issues were found
                    issues = ["AI response 'is_compatible' field was not a boolean."]

            return is_compatible, issues

        except json.JSONDecodeError as json_err:
            logging.error(f"Ollama AI response was not valid JSON: {full_response}. Error: {json_err}")
            return False, [f"AI response was not valid JSON. Raw response: {full_response[:200]}..."]

    except Exception as e:
        logging.error(f"Error communicating with Ollama for schema comparison: {e}")
        return False, [f"Error communicating with Ollama: {e}"]
