# Director UI Architecture

## Database Architecture - Unified Async SQLAlchemy

**Status:** ✅ Fully migrated to async SQLAlchemy 2.0

### Overview

The codebase uses **async SQLAlchemy 2.0** throughout for ALL database operations:
- ✅ All routers use `AsyncSession`
- ✅ Uses SQLAlchemy 2.0 `select()` style (not legacy `query()`)
- ✅ Proper async/await with `asyncpg` driver for PostgreSQL
- ✅ Supports SQLite via `aiosqlite` for local development

### Components

**1. Async DAO (`src/data/async_dao.py`)**
```python
from data.async_dao import get_async_db, get_async_engine

# FastAPI dependency
async def my_endpoint(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Model).filter(...))
    instance = result.scalar_one_or_none()
```

**2. All Routers Use Async**
- `workspaces.py` - ✅ Async SQLAlchemy
- `film_shots.py` - ✅ Async SQLAlchemy
- `editing.py` - ✅ Async SQLAlchemy
- `publishing.py` - ✅ Async SQLAlchemy
- `assets.py` - ✅ Async SQLAlchemy
- `characters.py` - ✅ Async SQLAlchemy

**3. Legacy Components (TODO: Migrate)**
- `core/database.py` - Raw asyncpg pool (used by content/processing services)
- `data/dao.py` - Sync SQLAlchemy (DEPRECATED, being phased out)

### DATABASE_URL Configuration

The async DAO automatically converts URLs to async driver format:

**SQLite (Local Development):**
```bash
# What you set in .env:
DATABASE_URL=sqlite:///./mediaempire.db

# Auto-converted to:
DATABASE_URL=sqlite+aiosqlite:///./mediaempire.db
```

**PostgreSQL (Production):**
```bash
# What you set in .env:
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Auto-converted to:
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db

# Or set explicitly:
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
```

### Migration Pattern

**Old (Sync):**
```python
from sqlalchemy.orm import Session
from data.dao import get_db

@router.get("/items")
async def list_items(db: Session = Depends(get_db)):
    items = db.query(Item).filter(Item.active == True).all()
    return items
```

**New (Async):**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from data.async_dao import get_async_db

@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Item).filter(Item.active == True))
    items = result.scalars().all()
    return list(items)
```

### Common Async Patterns

**Get one:**
```python
result = await db.execute(select(Model).filter(Model.id == id))
instance = result.scalar_one_or_none()
```

**Get many:**
```python
result = await db.execute(select(Model).filter(Model.active == True))
instances = result.scalars().all()
return list(instances)  # Convert to list for JSON serialization
```

**Count:**
```python
result = await db.execute(select(func.count()).select_from(Model).filter(...))
count = result.scalar()
```

**Create:**
```python
new_item = Model(name="test", ...)
db.add(new_item)
await db.flush()  # Write to DB
await db.refresh(new_item)  # Reload from DB
return new_item
```

**Update:**
```python
result = await db.execute(select(Model).filter(Model.id == id))
item = result.scalar_one_or_none()
item.name = "updated"
await db.flush()
await db.refresh(item)
return item
```

**Delete:**
```python
result = await db.execute(select(Model).filter(Model.id == id))
item = result.scalar_one_or_none()
await db.delete(item)
```

### Why Async?

1. **Performance**: Non-blocking I/O for database operations
2. **Scalability**: Handle more concurrent requests
3. **Consistency**: Single pattern across entire codebase
4. **Modern**: SQLAlchemy 2.0 best practices
5. **FastAPI Native**: FastAPI is async-first

### Dependencies

- `asyncpg>=0.30.0` - Async PostgreSQL driver
- `aiosqlite>=0.19.0` - Async SQLite driver
- `sqlalchemy>=2.0.0` - ORM with async support
- `psycopg2-binary>=2.9.0` - Sync driver (for migrations/alembic)

### Next Steps

1. Migrate `core/database.py` services to use async SQLAlchemy instead of raw asyncpg
2. Remove deprecated `data/dao.py` sync DAO
3. Update any remaining raw SQL queries to use ORM
