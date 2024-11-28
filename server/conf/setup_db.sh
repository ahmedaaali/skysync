#!/bin/bash

DB_NAME="skysync_db"
DB_USER="skysync_ahmed"
DB_PASS="ahmed_password"

psql -U postgres -h localhost -d postgres <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF
