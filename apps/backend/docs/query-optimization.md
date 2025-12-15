# Query Optimization Guide

This document provides guidelines and best practices for writing efficient database queries in the KCardSwap backend.

## Table of Contents

1. [Overview](#overview)
2. [Index Strategy](#index-strategy)
3. [Query Patterns](#query-patterns)
4. [Common Optimizations](#common-optimizations)
5. [Monitoring and Analysis](#monitoring-and-analysis)
6. [Anti-patterns to Avoid](#anti-patterns-to-avoid)

## Overview

KCardSwap uses PostgreSQL with SQLAlchemy ORM. Proper query optimization is essential for:
- **Performance**: Fast response times for API requests
- **Scalability**: Handle increasing user base and data volume
- **Cost**: Efficient database resource usage

### Key Principles

1. **Index appropriately** - Cover common query patterns
2. **Minimize N+1 queries** - Use eager loading
3. **Select only needed columns** - Avoid `SELECT *`
4. **Use pagination** - Limit result sets
5. **Cache when possible** - Reduce database load

## Index Strategy

### Current Indexes

Based on `alembic/versions/002_add_indexes.py`:

```sql
-- Users
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_email ON users(email);

-- Cards
CREATE INDEX idx_cards_owner_id ON cards(owner_id);
CREATE INDEX idx_cards_status ON cards(status);

-- Subscriptions
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);

-- Refresh Tokens
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
```

### When to Add Indexes

✅ **Add indexes for:**
- Foreign key columns (already done)
- Columns in WHERE clauses
- Columns in ORDER BY clauses
- Columns in JOIN conditions
- Columns with high selectivity

❌ **Avoid indexes for:**
- Columns rarely queried
- Columns with low selectivity (e.g., boolean with few distinct values)
- Small tables (< 1000 rows)
- Columns frequently updated (indexes slow down writes)

### Composite Indexes

For queries with multiple conditions:

```python
# Query pattern: Filter by owner and status, order by created_at
SELECT * FROM cards 
WHERE owner_id = ? AND status = 'available'
ORDER BY created_at DESC;

# Optimal index:
CREATE INDEX idx_cards_owner_status_created 
ON cards(owner_id, status, created_at DESC);
```

**Index column order matters:**
1. Equality conditions first (owner_id, status)
2. Range/sort conditions last (created_at)

## Query Patterns

### 1. Simple Lookups

**Efficient:**
```python
# Use indexed column (email)
user = await session.execute(
    select(UserModel).where(UserModel.email == email)
)
user = user.scalar_one_or_none()
```

**Inefficient:**
```python
# Full table scan on non-indexed column
user = await session.execute(
    select(UserModel).where(UserModel.nickname == "Alice")
)
```

### 2. Joins and Relationships

**Efficient (Eager Loading):**
```python
# Load user with profile in one query
result = await session.execute(
    select(UserModel)
    .options(selectinload(UserModel.profile))
    .where(UserModel.id == user_id)
)
user = result.scalar_one()
# Access user.profile without additional query
```

**Inefficient (N+1 Queries):**
```python
# Loads profile separately for each user
users = await session.execute(select(UserModel))
for user in users.scalars():
    # Each access triggers a new query!
    print(user.profile.nickname)
```

### 3. Pagination

**Efficient:**
```python
# Offset pagination with limit
result = await session.execute(
    select(CardModel)
    .where(CardModel.owner_id == user_id)
    .order_by(CardModel.created_at.desc())
    .limit(20)
    .offset(page * 20)
)
cards = result.scalars().all()
```

**Better (Cursor-based):**
```python
# For large datasets, cursor pagination is more efficient
result = await session.execute(
    select(CardModel)
    .where(
        CardModel.owner_id == user_id,
        CardModel.created_at < cursor_timestamp
    )
    .order_by(CardModel.created_at.desc())
    .limit(20)
)
cards = result.scalars().all()
```

### 4. Counting

**Efficient:**
```python
# Use COUNT query instead of loading all records
from sqlalchemy import func

result = await session.execute(
    select(func.count(CardModel.id))
    .where(CardModel.owner_id == user_id)
)
count = result.scalar()
```

**Inefficient:**
```python
# Loads all records into memory
cards = await session.execute(
    select(CardModel).where(CardModel.owner_id == user_id)
)
count = len(cards.scalars().all())  # Slow and memory-intensive!
```

### 5. Filtering with Multiple Conditions

**Efficient (Use indexes):**
```python
# Indexed columns first
result = await session.execute(
    select(CardModel)
    .where(
        CardModel.owner_id == user_id,  # Indexed
        CardModel.status == 'available',  # Indexed
        CardModel.rarity.in_(['rare', 'epic', 'legendary'])  # Not indexed, but small set
    )
)
```

## Common Optimizations

### 1. Select Only Needed Columns

```python
# Instead of loading entire model
result = await session.execute(
    select(UserModel.id, UserModel.email, ProfileModel.nickname)
    .join(ProfileModel)
    .where(UserModel.id == user_id)
)
```

### 2. Bulk Operations

```python
# Efficient: Bulk insert
session.add_all([
    CardModel(owner_id=user_id, ...),
    CardModel(owner_id=user_id, ...),
    # ... more cards
])
await session.commit()

# Inefficient: Individual inserts
for card_data in cards:
    session.add(CardModel(**card_data))
    await session.commit()  # Commit per item is slow!
```

### 3. Use Database Functions

```python
# Let database do the work
from sqlalchemy import func

# Update in database
await session.execute(
    update(CardModel)
    .where(CardModel.owner_id == user_id)
    .values(updated_at=func.now())
)
```

### 4. Avoid OR Conditions

```python
# Less efficient
select(UserModel).where(
    (UserModel.email == email) | (UserModel.google_id == google_id)
)

# More efficient: Use IN or UNION
select(UserModel).where(
    UserModel.email.in_([email1, email2, email3])
)
```

### 5. Use EXISTS for Existence Checks

```python
from sqlalchemy import exists

# Efficient
has_cards = await session.execute(
    select(exists().where(CardModel.owner_id == user_id))
)
has_cards = has_cards.scalar()

# Inefficient
cards = await session.execute(
    select(CardModel).where(CardModel.owner_id == user_id)
)
has_cards = len(cards.scalars().all()) > 0
```

## Monitoring and Analysis

### Enable Query Logging

In development:

```python
# config.py
SQL_ECHO = True  # Log all SQL queries

# Or in engine
engine = create_async_engine(DATABASE_URL, echo=True)
```

### Analyze Query Plans

```python
# Get query SQL
stmt = select(CardModel).where(CardModel.owner_id == user_id)
compiled = stmt.compile(compile_kwargs={"literal_binds": True})
print(compiled)

# Run EXPLAIN in PostgreSQL
# EXPLAIN ANALYZE <query>
```

### Use PostgreSQL EXPLAIN

```sql
-- Analyze query performance
EXPLAIN ANALYZE
SELECT * FROM cards 
WHERE owner_id = 'xxx' AND status = 'available'
ORDER BY created_at DESC
LIMIT 20;
```

Look for:
- **Seq Scan** → Add index
- **High cost** → Optimize query
- **Many rows** → Add WHERE conditions

### Monitor Slow Queries

```python
# Add timing middleware
import time
from starlette.middleware.base import BaseHTTPMiddleware

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        if duration > 1.0:  # Log slow requests
            logger.warning(f"Slow request: {request.url} took {duration:.2f}s")
        return response
```

## Anti-patterns to Avoid

### 1. ❌ Loading All Records

```python
# DON'T: Load all users into memory
users = session.execute(select(UserModel)).scalars().all()
for user in users:
    process(user)

# DO: Process in batches
offset = 0
batch_size = 100
while True:
    users = await session.execute(
        select(UserModel).limit(batch_size).offset(offset)
    )
    batch = users.scalars().all()
    if not batch:
        break
    for user in batch:
        process(user)
    offset += batch_size
```

### 2. ❌ N+1 Query Problem

```python
# DON'T: Separate query for each relationship
users = await session.execute(select(UserModel))
for user in users.scalars():
    # New query for EACH user!
    profile = await session.execute(
        select(ProfileModel).where(ProfileModel.user_id == user.id)
    )

# DO: Use eager loading
users = await session.execute(
    select(UserModel).options(selectinload(UserModel.profile))
)
```

### 3. ❌ SELECT * When Not Needed

```python
# DON'T: Load all columns
users = await session.execute(select(UserModel))

# DO: Select only needed columns
users = await session.execute(
    select(UserModel.id, UserModel.email)
)
```

### 4. ❌ Too Many Joins

```python
# DON'T: Join 5+ tables in one query
# Complex joins become slow
result = await session.execute(
    select(UserModel)
    .join(ProfileModel)
    .join(SubscriptionModel)
    .join(CardModel)
    .join(TradeModel)
)

# DO: Break into multiple queries or use caching
user = await get_user(user_id)
profile = await get_profile(user_id)
cards = await get_user_cards(user_id)
```

### 5. ❌ LIKE Queries Without Indexes

```python
# DON'T: Leading wildcard prevents index usage
users = await session.execute(
    select(UserModel).where(UserModel.email.like("%@example.com"))
)

# DO: Use full-text search or trailing wildcard
users = await session.execute(
    select(UserModel).where(UserModel.email.like("user%"))
)
```

## Performance Targets

### Query Performance Goals

- **Simple lookups**: < 10ms
- **Paginated lists**: < 50ms
- **Complex aggregations**: < 200ms
- **Reports**: < 1s

### When to Optimize

1. **Response time** > 500ms
2. **Database CPU** > 70%
3. **Connection pool** exhausted
4. **User complaints** about slowness

### Optimization Workflow

1. **Identify** slow queries (logging, monitoring)
2. **Analyze** query plan (EXPLAIN ANALYZE)
3. **Add indexes** or rewrite query
4. **Test** performance improvement
5. **Monitor** in production

## Further Resources

- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [SQLAlchemy Performance](https://docs.sqlalchemy.org/en/20/faq/performance.html)
- [Use The Index, Luke!](https://use-the-index-luke.com/)

## Need Help?

- Review this guide
- Check PostgreSQL query plans
- Ask in #backend channel
- Profile queries in development

---

**Remember**: Premature optimization is the root of all evil. Optimize when you have metrics showing a problem!
