#!/bin/bash

set -e

# Variables
BASE_DIR="/home/zerabruck/Desktop/portableodoo (copy)"
PG_BIN="$BASE_DIR/postgres/bin"
PG_DATA="$BASE_DIR/postgres/data"
DB_PORT=5435
DB_USER="odoo_user"
DB_PASSWORD="odoopassword1234"
DB_NAME="odoo"

echo "Setting up directories and permissions..."
mkdir -p "$PG_DATA"
chmod 700 "$PG_DATA"
chown -R "$(whoami):$(whoami)" "$BASE_DIR"

echo "Initializing PostgreSQL database cluster..."
"$PG_BIN/initdb" -D "$PG_DATA"

echo "Configuring PostgreSQL..."
echo "port = $DB_PORT" >> "$PG_DATA/postgresql.conf"
echo "listen_addresses = 'localhost'" >> "$PG_DATA/postgresql.conf"

echo "Starting PostgreSQL server..."
"$PG_BIN/pg_ctl" start -D "$PG_DATA" -o "-p $DB_PORT" -w

echo "Creating  user"

"$PG_BIN/psql" -p $DB_PORT -d postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
"$PG_BIN/psql" -p $DB_PORT -U zerabruck -d postgres -c "ALTER USER $DB_USER CREATEDB;"

# Create the database again


echo "PostgreSQL setup completed!"
