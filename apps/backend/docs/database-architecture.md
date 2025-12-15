# Database Architecture Guide

## Overview

KCardSwap backend uses a clean separation between database schema management (migrations) and ORM models, following Domain-Driven Design (DDD) principles.

## Architecture Components

### 1. Database Schema Management (Alembic Migrations)

**Location**: `apps/backend/alembic/versions/`

**Purpose**: Version-controlled database schema changes

**Key Files**:
- `alembic.ini` - Alembic configuration
- `alembic/env.py` - Migration environment setup
- `alembic/versions/001_initial_schema.py` - Initial table creation
- `alembic/versions/002_add_indexes.py` - Index creation

**How to Use**:
```bash
# Apply migrations
poetry run alembic upgrade head

# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Rollback one version
poetry run alembic downgrade -1
```

**Important**: ALL schema changes MUST go through Alembic migrations. Never use ORM `create_all()` in production.

### 2. ORM Models (Infrastructure Layer)

**Location**: `app/infrastructure/database/models.py`

**Purpose**: SQLAlchemy ORM models for database persistence

**Current Models**:
- `UserModel` - User accounts
- `ProfileModel` - User profiles
- `RefreshTokenModel` - JWT refresh tokens

**Characteristics**:
- Framework-dependent (SQLAlchemy)
- Used by repositories for data access
- Match the database schema defined in migrations
- Include relationships and lazy loading configurations

### 3. Domain Entities (Domain Layer)

**Location**: `app/domain/entities/`

**Purpose**: Pure business logic entities

**Current Entities**:
- `User` - Core user business logic
- `Profile` - Profile business logic

**Characteristics**:
- Framework-independent (pure Python)
- Contain business validation and rules
- No database/ORM dependencies
- Converted to/from ORM models by repositories

### 4. Database Connection

**Location**: `app/infrastructure/database/connection.py`

**Purpose**: Database connection pooling and session management

**Key Functions**:
- `engine` - SQLAlchemy async engine
- `get_db_session()` - FastAPI dependency for database sessions
- `get_db()` - Context manager for database sessions
- `init_db()` - **Deprecated** (kept for backward compatibility only)

**Important Note**: The `init_db()` function no longer creates tables. It's kept only for backward compatibility. All tables are created by Alembic migrations.

## Removed Components

### ❌ `app/db/` (Deleted)
- **Reason**: Redundant, replaced by `app/infrastructure/database/`
- **Previous Use**: Old database connection location
- **Status**: Completely removed

### ❌ `app/models/` (Deleted)
- **Reason**: Violates DDD architecture
- **Previous Use**: Generic models location
- **Replacement**: 
  - Domain entities → `app/domain/entities/`
  - ORM models → `app/infrastructure/database/models.py`
- **Status**: Completely removed

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Schema Definition (Single Source of Truth)              │
│     Location: alembic/versions/001_initial_schema.py        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Database Tables (PostgreSQL)                            │
│     Created by: alembic upgrade head                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. ORM Models (Infrastructure Layer)                       │
│     Location: app/infrastructure/database/models.py         │
│     Purpose: Database access and persistence                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Repositories (Infrastructure Layer)                     │
│     Location: app/infrastructure/repositories/              │
│     Purpose: Convert ORM ↔ Domain Entities                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Domain Entities (Domain Layer)                          │
│     Location: app/domain/entities/                          │
│     Purpose: Business logic (framework-independent)         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Use Cases (Application Layer)                           │
│     Location: app/application/use_cases/                    │
│     Purpose: Orchestrate business operations                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  7. API Routers (Presentation Layer)                        │
│     Location: app/presentation/routers/                     │
│     Purpose: HTTP endpoints and request/response handling   │
└─────────────────────────────────────────────────────────────┘
```

## Best Practices

### ✅ DO:
1. **Use Alembic for all schema changes**
   - Create migration: `alembic revision -m "description"`
   - Apply migrations: `alembic upgrade head`

2. **Keep ORM models synchronized with migrations**
   - ORM models should match the database schema
   - Use migrations as single source of truth

3. **Use repositories to convert between layers**
   - ORM Model → Domain Entity in repositories
   - Domain Entity → ORM Model in repositories

4. **Keep domain entities pure**
   - No SQLAlchemy imports in domain layer
   - No framework dependencies

### ❌ DON'T:
1. **Never use `Base.metadata.create_all()` in production**
   - This bypasses version control
   - Use Alembic migrations instead

2. **Don't put business logic in ORM models**
   - ORM models are for persistence only
   - Business logic belongs in domain entities

3. **Don't access database directly from use cases**
   - Always use repository interfaces
   - Use dependency injection

4. **Don't create ad-hoc database folders**
   - Stick to the established architecture
   - Use `app/infrastructure/database/` only

## Migration Strategy

### Development Workflow
```bash
# 1. Modify ORM models (if needed)
vim app/infrastructure/database/models.py

# 2. Create migration
poetry run alembic revision --autogenerate -m "add cards table"

# 3. Review and edit migration
vim alembic/versions/003_add_cards_table.py

# 4. Test migration upgrade
poetry run alembic upgrade head

# 5. Test migration downgrade
poetry run alembic downgrade -1

# 6. Re-upgrade for development
poetry run alembic upgrade head

# 7. Commit migration to git
git add alembic/versions/003_add_cards_table.py
git commit -m "feat(db): add cards table migration"
```

### Production Deployment
```bash
# Migrations run automatically via Dockerfile
# See apps/backend/Dockerfile line 40-46

# Manual execution (if needed):
poetry run alembic upgrade head
```

## Troubleshooting

### Migration fails to apply
```bash
# Check current version
poetry run alembic current

# Check migration history
poetry run alembic history

# View pending migrations
poetry run alembic heads

# Rollback and retry
poetry run alembic downgrade -1
poetry run alembic upgrade head
```

### ORM model doesn't match database
```bash
# Generate new migration to sync
poetry run alembic revision --autogenerate -m "sync models with db"

# Review the generated migration carefully
# Apply after verification
poetry run alembic upgrade head
```

### Need to add a new table
```bash
# 1. Add ORM model to models.py
# 2. Create migration
poetry run alembic revision --autogenerate -m "add new_table"

# 3. Review migration, add indexes if needed
# 4. Apply migration
poetry run alembic upgrade head
```

## References

- [Database Migrations Guide](./database-migrations.md) - Complete migration workflow
- [Query Optimization Guide](./query-optimization.md) - Performance best practices
- [Project Constitution](../../../.specify/memory/constitution.md) - DDD architecture principles
- [Alembic Documentation](https://alembic.sqlalchemy.org/) - Official Alembic docs
