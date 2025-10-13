import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api import ai_converter

pg_schema_path = '/Users/avannala/Documents/workspace/spf-converter/sql-assests/psql-university-schema.sql'
oracle_schema_path = '/Users/avannala/Documents/workspace/spf-converter/sql-assests/psql-university-schema-oracle.sql'

try:
    with open(pg_schema_path, 'r') as f:
        pg_schema_content = f.read()

    oracle_schema_content = ai_converter.convert_postgres_ddl_to_oracle_ddl(pg_schema_content)

    with open(oracle_schema_path, 'w') as f:
        f.write(oracle_schema_content)
    print(f"Successfully converted PostgreSQL schema to Oracle SQL and saved to {oracle_schema_path}")
except Exception as e:
    print(f"Error during schema conversion: {e}")
    sys.exit(1)