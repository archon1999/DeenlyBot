#!/bin/sh
set -eu

# Dedicated application login. PostgreSQL's administrative account is not given
# to Django, the bot or the worker. Values are passed as quoted psql variables.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres \
  -v app_user="$APP_DB_USER" -v app_db="$APP_DB_NAME" \
  -v app_password="$(cat /run/secrets/postgres_password)" <<'SQL'
CREATE ROLE :"app_user" LOGIN PASSWORD :'app_password' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE DATABASE :"app_db" OWNER :"app_user";
SQL
