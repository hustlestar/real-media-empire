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
# 1. Start backend (must be running on port 10101)
cd director-ui
uv run python -m api.app

# 2. Generate TypeScript client
cd frontend
npm run generate-api

# 3. Use in components
import { FilmService, type FilmShot } from '@/api/generated';
const shots = await FilmService.listShots();
```

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

**When to regenerate:**
- After adding new API endpoints
- After modifying Pydantic models
- After changing request/response schemas

**How to regenerate:**

```bash
cd director-ui/frontend
npm run generate-api
git add src/api/generated/
git commit -m "chore: regenerate API client"
```

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
