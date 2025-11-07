# OpenAPI Client Generation

Auto-generate TypeScript client from backend OpenAPI specification to eliminate code duplication.

## Quick Start

```bash
# 1. Install git hooks (one-time setup)
cd director-ui/frontend
bash scripts/install-hooks.sh

# 2. Start backend (must be running on port 8000)
cd ../
uv run uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# 3. Generate TypeScript client
cd frontend
npm run generate-api

# 4. Use in components
import { getFilmShotsApiFilmShotsGet, type FilmShot } from '@/api/sdk.gen';
const response = await getFilmShotsApiFilmShotsGet();
```

## Benefits

- ✅ No code duplication between backend and frontend
- ✅ Type safety across the full stack
- ✅ Automatic updates when backend changes
- ✅ Auto-completion and IntelliSense in IDE
- ✅ Consistent API client with proper error handling

## Pre-Commit Hook (Automatic)

A pre-commit hook **automatically regenerates** the TypeScript client when you commit backend changes.

**Installation:**
```bash
cd director-ui/frontend
bash scripts/install-hooks.sh
```

**How it works:**
1. Modify backend API files (`src/api/` or `src/data/models.py`)
2. Commit your changes: `git commit -m "add new endpoint"`
3. Hook detects backend changes and auto-regenerates client
4. Generated files are automatically staged and included in commit

**When backend isn't running:**
```
⚠️  Backend not running at http://localhost:8000
   Generated API client may be out of sync!

   Continue commit anyway? Use --no-verify to skip this check.
```

## Manual Generation

```bash
cd director-ui/frontend

# Method 1: Using npm script (recommended)
npm run generate-api

# Method 2: Direct command
curl -s http://localhost:8000/openapi.json -o openapi.json
npx @hey-api/openapi-ts --input openapi.json --output src/api
```

## Generated Files

Located in `frontend/src/api/`:

- **`sdk.gen.ts`** - Main SDK with all API functions
- **`types.gen.ts`** - TypeScript type definitions for all models
- **`client.gen.ts`** - HTTP client configuration
- **`index.ts`** - Entry point for exports
- **`client/`** - Client utilities
- **`core/`** - Core HTTP handling

## Usage Examples

### Basic API Call

```typescript
import { getFilmShotsApiFilmShotsGet } from '@/api/sdk.gen';
import type { FilmShot } from '@/api/types.gen';

// Fetch film shots
const response = await getFilmShotsApiFilmShotsGet({
  query: { film_id: 'abc123' }
});
const shots: FilmShot[] = response.data;
```

### With React Query

```typescript
import { useQuery } from '@tanstack/react-query';
import { getFilmShotsApiFilmShotsGet } from '@/api/sdk.gen';

export const useFilmShots = (filmId: string) => {
  return useQuery({
    queryKey: ['film-shots', filmId],
    queryFn: async () => {
      const response = await getFilmShotsApiFilmShotsGet({
        query: { film_id: filmId }
      });
      return response.data;
    }
  });
};
```

## When to Regenerate

Regenerate the client when:

1. Backend API changes (new endpoints, modified models)
2. After pulling changes from git
3. Before building for production

## Troubleshooting

### Backend not running

Start the backend:
```bash
cd director-ui
uv run uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

### Import errors after generation

1. Restart Vite dev server
2. Clear browser cache
3. Verify `@/api` path alias in `vite.config.ts`

### Type mismatches

1. Regenerate client: `npm run generate-api`
2. Check backend and frontend are using same models
3. Update frontend code to match new types

## CI/CD Integration

```bash
# Start backend in background
cd director-ui
uv run uvicorn src.api.app:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend
sleep 5

# Generate client
cd frontend
npm run generate-api

# Build frontend
npm run build

# Cleanup
kill $BACKEND_PID
```

## Configuration

Backend port is configured in:
- Backend command: `--port 8000`
- Frontend script: `frontend/scripts/generate-api-client.sh`
- OpenAPI endpoint: `http://localhost:8000/openapi.json`

To change the port, update all three locations.
