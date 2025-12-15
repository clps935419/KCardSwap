# Database Migrations Guide

This guide explains how to work with database migrations in the KCardSwap backend using Alembic.

## Overview

KCardSwap uses **Alembic** for database schema management following the "Migrations First" principle:

- **All schema changes** must be managed through Alembic migrations
- **infra/db/init.sql** only contains database-level setup (extensions, users, permissions)
- **Migrations are version controlled** and tracked in Git
- **Schema is consistent** across development, testing, and production environments

## Table of Contents

1. [Migration Strategy](#migration-strategy)
2. [Creating Migrations](#creating-migrations)
3. [Running Migrations](#running-migrations)
4. [Rolling Back Migrations](#rolling-back-migrations)
5. [Testing Migrations](#testing-migrations)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Migration Strategy

### Why Alembic?

- **Version Control**: Every schema change is tracked with a unique revision ID
- **Reversible**: All migrations support upgrade and downgrade operations
- **Team Collaboration**: No merge conflicts between SQL files and ORM models
- **Environment Consistency**: Same schema across dev/test/prod
- **Complex Changes**: Support for data migrations, not just DDL

### Directory Structure

```
apps/backend/
├── alembic/
│   ├── versions/          # Migration scripts
│   │   ├── 001_initial_schema.py
│   │   ├── 002_add_indexes.py
│   │   └── ...
│   ├── env.py            # Alembic environment configuration
│   └── script.py.mako    # Template for new migrations
├── alembic.ini           # Alembic configuration
└── app/
    └── infrastructure/
        └── database/
            └── models.py  # SQLAlchemy ORM models
```

## Creating Migrations

### Auto-generate from ORM Models

When you modify SQLAlchemy models, generate a migration automatically:

```bash
cd apps/backend

# Create a new migration based on model changes
poetry run alembic revision --autogenerate -m "add user preferences table"
```

Alembic will:
1. Compare ORM models with current database schema
2. Generate upgrade() and downgrade() functions
3. Create a new file in `alembic/versions/`

**⚠️ Always review auto-generated migrations!** They may not catch:
- Column renames (will appear as drop + add)
- Data type changes requiring data migration
- Complex constraints

### Create Empty Migration

For data migrations or complex schema changes:

```bash
poetry run alembic revision -m "migrate user data to new format"
```

Edit the generated file to add your custom logic:

```python
def upgrade() -> None:
    # Add your upgrade logic
    op.execute("""
        UPDATE users 
        SET preferences = jsonb_build_object('theme', 'light')
        WHERE preferences IS NULL
    """)

def downgrade() -> None:
    # Add your downgrade logic
    op.execute("UPDATE users SET preferences = NULL")
```

## Running Migrations

### Local Development

```bash
cd apps/backend

# Check current migration status
poetry run alembic current

# View migration history
poetry run alembic history --verbose

# Upgrade to latest version
poetry run alembic upgrade head

# Upgrade by one version
poetry run alembic upgrade +1

# Upgrade to specific revision
poetry run alembic upgrade <revision_id>
```

### Docker Environment

Migrations run automatically when the backend container starts (see `Dockerfile`):

```bash
# Start services (migrations run automatically)
docker compose up -d

# Or manually run migrations in container
docker compose exec backend alembic upgrade head
```

### CI/CD Pipeline

Migrations are validated in GitHub Actions:

1. **Upgrade test**: `alembic upgrade head`
2. **Downgrade test**: `alembic downgrade base`
3. **Re-upgrade**: `alembic upgrade head` (for running tests)

See `.github/workflows/backend-ci.yml` for details.

## Rolling Back Migrations

### Downgrade Operations

```bash
# Downgrade by one version
poetry run alembic downgrade -1

# Downgrade to specific revision
poetry run alembic downgrade <revision_id>

# Downgrade to base (remove all migrations)
poetry run alembic downgrade base
```

### Important Notes

- **Test downgrades locally** before deploying
- **Data loss** may occur if migration drops columns/tables
- **Backup production database** before downgrading
- **Coordinate with team** when downgrading in shared environments

## Testing Migrations

### Manual Testing

```bash
# 1. Start fresh database
docker compose down -v
docker compose up -d db

# 2. Run migrations
cd apps/backend
export DATABASE_URL="postgresql://kcardswap:kcardswap@localhost:5432/kcardswap"
poetry run alembic upgrade head

# 3. Verify schema
psql $DATABASE_URL -c "\dt"  # List tables
psql $DATABASE_URL -c "\d users"  # Describe table

# 4. Test downgrade
poetry run alembic downgrade base

# 5. Verify cleanup
psql $DATABASE_URL -c "\dt"  # Should be empty (except alembic_version)

# 6. Re-upgrade
poetry run alembic upgrade head
```

### Integration Tests

Test fixtures automatically run migrations (see `tests/conftest.py`):

```python
@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as postgres:
        database_url = postgres.get_connection_url()
        
        # Run migrations before tests
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        command.upgrade(alembic_cfg, "head")
        
        yield postgres
```

## Best Practices

### 1. One Logical Change Per Migration

✅ Good:
```
001_create_users_table.py
002_add_user_indexes.py
003_add_profiles_table.py
```

❌ Bad:
```
001_add_everything.py  # Too much in one migration
```

### 2. Descriptive Migration Names

✅ Good:
```bash
alembic revision -m "add email verification fields to users"
alembic revision -m "create indexes for cards table"
```

❌ Bad:
```bash
alembic revision -m "fix"
alembic revision -m "update db"
```

### 3. Always Provide Downgrade

Every migration must have a working `downgrade()`:

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('verified', sa.Boolean(), default=False))

def downgrade() -> None:
    op.drop_column('users', 'verified')
```

### 4. Test Both Upgrade and Downgrade

```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Re-upgrade
alembic upgrade head
```

### 5. Handle Data Migrations Carefully

When changing data types or restructuring:

```python
def upgrade() -> None:
    # 1. Add new column
    op.add_column('users', sa.Column('new_field', sa.String(100)))
    
    # 2. Migrate data
    op.execute("UPDATE users SET new_field = CAST(old_field AS VARCHAR)")
    
    # 3. Drop old column
    op.drop_column('users', 'old_field')
```

### 6. Use Transactions

Migrations run in transactions by default. For PostgreSQL:

```python
# For operations that can't run in transaction (like CREATE INDEX CONCURRENTLY)
def upgrade() -> None:
    # This migration must run outside transaction
    op.execute("CREATE INDEX CONCURRENTLY idx_cards_created_at ON cards(created_at)")

def downgrade() -> None:
    op.drop_index('idx_cards_created_at', table_name='cards')
```

### 7. Keep Models and Migrations in Sync

After creating a migration:
1. Review the generated SQL
2. Test upgrade and downgrade
3. Commit both model changes and migration together

## Troubleshooting

### Error: "Can't locate revision"

```bash
# Check current database revision
poetry run alembic current

# Check available revisions
poetry run alembic history

# If database is out of sync, stamp to specific revision
poetry run alembic stamp <revision_id>
```

### Error: "Target database is not up to date"

```bash
# Upgrade database first
poetry run alembic upgrade head
```

### Error: "Migration already exists"

Check `alembic_version` table:

```sql
SELECT * FROM alembic_version;

-- If stuck, manually update:
UPDATE alembic_version SET version_num = '<correct_revision>';
```

### Merge Conflicts in Migration Files

```bash
# 1. Keep both migrations, update down_revision
# 2. Create a merge migration
poetry run alembic merge -m "merge branches" <rev1> <rev2>
```

### Fresh Start (Development Only)

```bash
# ⚠️ WARNING: Destroys all data!
docker compose down -v
docker compose up -d db
poetry run alembic upgrade head
```

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Getting Help

- Check this guide first
- Review existing migrations in `alembic/versions/`
- Ask team members in #backend channel
- Create an issue in the repository

---

**Remember**: Migrations are code. Review them carefully, test thoroughly, and commit them with your changes!
