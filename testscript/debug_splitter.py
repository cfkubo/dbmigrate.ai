
import re
import os

SQL_ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'sql-assets')
SQL_FILE = os.path.join(SQL_ASSETS_DIR, 'airline_schema.sql')

def debug_sql_splitter():
    """
    Reads the specific SQL file and tests a regex-based splitting strategy.
    """
    print(f"--- Debugging SQL Splitter on {os.path.basename(SQL_FILE)} ---")
    
    if not os.path.exists(SQL_FILE):
        print(f"ERROR: File not found at {SQL_FILE}")
        return

    with open(SQL_FILE, 'r') as f:
        sql_content = f.read()

    # Split by the Oracle '/' delimiter for PL/SQL blocks
    # The regex looks for a newline, then a slash, then optional whitespace, then a newline or end of string.
    blocks = re.split(r'\n/\s*(?:\n|$)', sql_content)
    
    # Filter out any empty statements
    non_empty_statements = [stmt.strip() for stmt in blocks if stmt.strip()]
    
    print(f"Found {len(non_empty_statements)} non-empty statements.")
    print("--------------------------------------------------")
    
    for i, stmt in enumerate(non_empty_statements):
        print(f"--- Statement {i+1} ---")
        print(stmt)
        print("------------------------")

if __name__ == "__main__":
    debug_sql_splitter()
