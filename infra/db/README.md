# Database Infrastructure

This directory contains database initialization scripts and migration files.

## Files

- `init.sql` - Initial database schema creation script

## Usage

The initialization script is automatically executed when the PostgreSQL container starts if the database is empty.

To manually run the script:

```bash
docker exec -i kcardswap-db psql -U kcardswap -d kcardswap < infra/db/init.sql
```

## Schema Overview

The database includes the following core tables:

- `users` - User authentication and basic info
- `profiles` - Extended user profile information
- `subscriptions` - User subscription/membership plans
- `cards` - Trading cards owned by users

All tables include automatic `updated_at` timestamp updates via triggers.
