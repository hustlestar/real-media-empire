# Database Setup for Director UI

The Director UI backend requires a PostgreSQL database to function. You have two options:

## Option 1: Using Docker (Recommended)

The project includes a `docker-compose.yml` that sets up everything you need:

```bash
cd director-ui
docker compose up -d postgres
```

This will:
- Start PostgreSQL 15 on port 5432
- Create database: `pdf_link_youtube_to_anything_tg_bot`
- Create user: `botuser` / password: `botpass`

The `.env` file should have:
```
DATABASE_URL=postgresql://botuser:botpass@localhost:5432/pdf_link_youtube_to_anything_tg_bot
```

## Option 2: Using Local PostgreSQL

If you have PostgreSQL installed locally:

1. Create the database and user:
```sql
CREATE USER botuser WITH PASSWORD 'botpass';
CREATE DATABASE pdf_link_youtube_to_anything_tg_bot OWNER botuser;
```

2. Update your `.env` file:
```
DATABASE_URL=postgresql://botuser:botpass@localhost:5432/pdf_link_youtube_to_anything_tg_bot
```

## Running Migrations

Once the database is running, apply migrations:

```bash
cd director-ui
uv run alembic upgrade head
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `API_CORS_ORIGINS` - CORS origins (use `*` for development)
- `API_HOST` - API host (default: 0.0.0.0)
- `API_PORT` - API port (default: 8000)

## Troubleshooting

### Error: "password authentication failed for user"

This means either:
1. PostgreSQL isn't running - Start it with `docker compose up postgres`
2. Wrong credentials in `.env` - Check DATABASE_URL matches docker-compose.yml
3. Database doesn't exist - Recreate with `docker compose down -v && docker compose up postgres`

### Error: "CORS policy blocked"

Add to your `.env`:
```
API_CORS_ORIGINS=*
```

Or for production, specify exact origins:
```
API_CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```
