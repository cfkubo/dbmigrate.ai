#!/usr/bin/env bash
set -euo pipefail

# gini.sh - load customer_orders schema files into an Oracle container
# Usage: ORACLE_CONTAINER=oracle-free ORACLE_USER=SYSTEM ORACLE_PWD=password \
#        ORACLE_SERVICE=FREE ./gini.sh

ORACLE_CONTAINER=${ORACLE_CONTAINER:-oracle-free}
ORACLE_USER=${ORACLE_USER:-SYSTEM}
ORACLE_PWD=${ORACLE_PWD:-password}
ORACLE_HOST=${ORACLE_HOST:-localhost}
ORACLE_PORT=${ORACLE_PORT:-1521}
ORACLE_SERVICE=${ORACLE_SERVICE:-FREE}

SQL_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Using container: $ORACLE_CONTAINER"
echo "Connecting as: $ORACLE_USER@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE}"

# Check docker is available
if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found in PATH" >&2
  exit 2
fi

# Check container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${ORACLE_CONTAINER}$"; then
  echo "Container '${ORACLE_CONTAINER}' is not running. Start it first." >&2
  exit 3
fi

# Helper: run sqlplus in the container and feed a file
run_sqlfile() {
  local file=$1
  if [ ! -f "$file" ]; then
    echo "SQL file not found: $file" >&2
    return 1
  fi
  echo "---- Executing: $(basename "$file") ----"

  local conn_string="${ORACLE_USER}/${ORACLE_PWD}@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE}"

  if [ "$(basename "$file")" = "co_install.sql" ]; then
    # Create a temporary file that contains responses followed by the SQL script
    tmpfile=$(mktemp)
    printf '%s\n%s\n%s\n' "$ORACLE_PWD" "" "YES" > "$tmpfile"
    cat "$file" >> "$tmpfile"
  # Use a pseudo-TTY so sqlplus ACCEPT ... HIDE reads the piped input correctly
  docker exec -i -t "$ORACLE_CONTAINER" bash -lc "sqlplus -s ${conn_string} @-" < "$tmpfile"
    rm -f "$tmpfile"
  else
    docker exec -i "$ORACLE_CONTAINER" bash -lc "sqlplus -s ${conn_string} @-" < "$file"
  fi
}

# Files to run (order matters)
# Run only the installer script - it calls @@co_create.sql and @@co_populate.sql
files=(
  "${SQL_DIR}/co_install.sql"
  "${SQL_DIR}/co_create.sql"
  "${SQL_DIR}/co_populate.sql"
)

for f in "${files[@]}"; do
  if ! run_sqlfile "$f"; then
    echo "Failed to run $f" >&2
    exit 4
  fi
done

echo "Done. Customer orders schema loaded."
