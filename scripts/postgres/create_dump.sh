#!/bin/bash

# Load environment variables
source .env

# Ensure dumps directory exists
if [ ! -d scripts/postgres/dumps ]; then
    mkdir -p scripts/postgres/dumps
fi

# Prompt for dump name
read -p "Create unique name of db_dump: " name_of_db_dump

# Run pg_dump using environment variables

docker compose exec \
    -e PGPASSWORD="$POSTGRES_PASSWORD" \
    "$DB_HOST" \
    pg_dump \
    --host "$DB_HOST" \
    --port "$DB_PORT" \
    --user "$POSTGRES_USER" \
    --no-password \
    --format=c \
    --large-objects \
    --compress "9" \
    --exclude-table "alembic_version" \
    --verbose \
    --data-only \
    --schema "public" \
    "$POSTGRES_DB" \
    > scripts/postgres/dumps/${name_of_db_dump}.backup
