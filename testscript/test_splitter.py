import sqlparse

with open("sql-assets/university_schema_oracle.sql", "r") as f:
    sql_content = f.read()

statements = sqlparse.split(sql_content)
print(statements)

print(f"Found {len(statements)} statements.")
