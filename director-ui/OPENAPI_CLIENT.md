# OpenAPI Client Generation

This document explains how to generate and use the TypeScript API client from the backend OpenAPI specification.

## Overview

Instead of duplicating types between backend (Python/Pydantic) and frontend (TypeScript), we automatically generate TypeScript types and API client functions from the backend's OpenAPI/Swagger specification.

**Benefits:**
- ✅ No code duplication between backend and frontend
- ✅ Type safety across the full stack
- ✅ Automatic updates when backend changes
- ✅ Auto-completion and IntelliSense in IDE
- ✅ Consistent API client with proper error handling

## Quick Start

```bash
# 1. Install git hooks (one-time setup)
cd director-ui/frontend
bash scripts/install-hooks.sh

# 2. Start backend (must be running on port 10101)
cd ../
uv run python -m api.app

# 3. Generate TypeScript client (or let pre-commit hook do it automatically)
cd frontend
npm run generate-api

# 4. Use in components
import { FilmService, type FilmShot } from '@/api/generated';
const shots = await FilmService.listShots();
```

## Pre-Commit Hook (Automatic Regeneration)

A pre-commit hook **automatically regenerates** the TypeScript client when you commit backend changes:

**Installation (one-time):**
```bash
cd director-ui/frontend
bash scripts/install-hooks.sh
```

**How it works:**
1. You modify backend API files (`director-ui/src/api/` or `director-ui/src/data/models.py`)
2. You commit your changes: `git commit -m "add new endpoint"`
3. Hook detects backend changes and auto-regenerates client
4. Generated files are automatically staged and included in your commit

**Benefits:**
- ✅ Never forget to regenerate client after backend changes
- ✅ Frontend types always in sync with backend
- ✅ Committed generated files work without backend running
- ✅ CI/CD can build frontend without backend dependency

## Usage Examples

### Before (Manual Types - Duplicated)

```typescript
// ❌ Manually duplicated types
export interface FilmShot {
  id: string;
  prompt: string;
  // ...
}

const response = await fetch('/api/film/shots');
const shots: FilmShot[] = await response.json();
```

### After (Generated Types - Single Source of Truth)

```typescript
// ✅ Import from generated client
import { FilmService, type FilmShot } from '@/api/generated';

const shots: FilmShot[] = await FilmService.listShots();
```

## Generated Client Structure

```
frontend/src/api/generated/
├── index.ts              # Main exports
├── types.ts              # TypeScript types (FilmShot, ShotReview, etc.)
├── services/             # API service functions
│   ├── FilmService.ts
│   ├── AudioService.ts
│   └── StyleService.ts
└── core/                 # HTTP client config
```

## Regeneration Workflow

### Automatic (Recommended) - Pre-Commit Hook

If you've installed the pre-commit hook, regeneration is **automatic**:

```bash
# 1. Modify backend API
vim director-ui/src/api/routers/film_shots.py

# 2. Commit (hook auto-regenerates and stages client)
git add director-ui/src/api/routers/film_shots.py
git commit -m "feat: add new endpoint"

# ✅ Generated client is automatically updated and included in commit!
```

### Manual - When Hook Not Installed

If you haven't installed the hook or need to regenerate manually:

```bash
# 1. Start backend
cd director-ui
uv run python -m api.app

# 2. Generate client
cd frontend
npm run generate-api

# 3. Commit generated files
git add src/api/generated/
git commit -m "chore: regenerate API client"
```

### When Backend Isn't Running

The pre-commit hook gracefully handles this:
```
⚠️  Backend not running at http://localhost:10101
   Generated API client may be out of sync!

   To regenerate client:
   1. Start backend: cd director-ui && uv run python -m api.app
   2. Regenerate: cd director-ui/frontend && npm run generate-api
   3. Commit generated files

Continue commit without regenerating? (y/N):
```

You can:
- Type `N` to abort and regenerate first (recommended)
- Type `y` to commit anyway (not recommended, causes drift)

## Integration with React Query

```typescript
import { useQuery } from '@tanstack/react-query';
import { FilmService } from '@/api/generated';

function useShots(filmProjectId: string) {
  return useQuery({
    queryKey: ['shots', filmProjectId],
    queryFn: () => FilmService.listFilmShots({ filmProjectId })
  });
}
```

## Best Practices

1. **Regenerate after backend changes** - `npm run generate-api`
2. **Commit generated files** - Other developers need them
3. **Never edit generated files** - Will be overwritten
4. **Use React Query** - Better caching and state management
5. **Use TypeScript strict mode** - Catch type errors early

## Troubleshooting

### Backend not reachable
Make sure backend is running: `cd director-ui && uv run python -m api.app`

### Types not found
Regenerate client: `cd frontend && npm run generate-api`

### Import errors
Use correct import path: `import { type FilmShot } from '@/api/generated'`

## Migration Guide

**Step 1:** Find manual type definitions
```bash
grep -r "export interface FilmShot" src/
```

**Step 2:** Replace with generated types
```typescript
// ❌ Before
import { FilmShot } from '../types/film';

// ✅ After
import { type FilmShot } from '@/api/generated';
```

**Step 3:** Replace manual API calls
```typescript
// ❌ Before
const response = await fetch('/api/film/shots');

// ✅ After
import { FilmService } from '@/api/generated';
const shots = await FilmService.listShots();
```

## References

- [@hey-api/openapi-ts Documentation](https://heyapi.dev/)
- [FastAPI OpenAPI](https://fastapi.tiangolo.com/tutorial/metadata/)
- [TanStack Query](https://tanstack.com/query/latest)
