#!/bin/sh
set -e

# This script runs during the database initialization.
# It finds the pg_hba.conf file that initdb creates and replaces all
# "trust" authentication methods with "md5" (password).
# This ensures that all connections, even local ones, require a password.

PG_HBA_CONF="/var/lib/postgresql/data/pg_hba.conf"

# Use sed to replace 'trust' with 'md5' everywhere in the file.
# This is a more robust way than replacing the whole file.
sed -i 's/trust/md5/g' "$PG_HBA_CONF"

echo "PostgreSQL authentication method changed to md5."