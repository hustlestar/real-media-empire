# API Client Generation Process

This document describes how to regenerate the TypeScript API client for the frontend.

## Overview

The frontend uses `@hey-api/openapi-ts` to generate a TypeScript client from the OpenAPI specification exposed by the FastAPI backend.

## Prerequisites

1. **Backend must be running** on `http://localhost:8000`
   ```bash
   cd director-ui
   uv run uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend dependencies must be installed**
   ```bash
   cd director-ui/frontend
   npm install
   ```

## Generation Methods

### Method 1: Using the npm script (Recommended)

```bash
cd director-ui/frontend
npm run generate-api
```

This will:
- Check if the backend is running
- Download the OpenAPI spec from `http://localhost:8000/openapi.json`
- Generate TypeScript types and SDK in `src/api/`

### Method 2: Manual generation

```bash
cd director-ui/frontend

# Download OpenAPI spec
curl -s http://localhost:8000/openapi.json -o openapi.json

# Generate TypeScript client
npx @hey-api/openapi-ts --input openapi.json --output src/api
```

### Method 3: During build

The client is automatically generated during the build process:

```bash
cd director-ui/frontend
npm run build
```

## Generated Files

The generation creates the following files in `frontend/src/api/`:

- **`sdk.gen.ts`** - Main SDK with all API functions
- **`types.gen.ts`** - TypeScript type definitions for all models
- **`client.gen.ts`** - HTTP client configuration
- **`index.ts`** - Entry point for exports
- **`client/`** - Client utilities
- **`core/`** - Core HTTP handling

## Configuration

The OpenAPI client generation is configured in `frontend/package.json`:

```json
{
  "scripts": {
    "generate-api": "bash scripts/generate-api-client.sh"
  }
}
```

The generation script is located at `frontend/scripts/generate-api-client.sh`.

## Usage in Frontend Code

### Import generated functions

```typescript
import { getTagsApiV1TagsGet } from '@/api/sdk.gen'
import type { Tag } from '@/api/types.gen'
```

### Using with React Query

```typescript
import { useQuery } from '@tanstack/react-query'
import { listContentApiV1ContentGet } from '@/api/sdk.gen'

export const useContentList = (page = 1, pageSize = 20) => {
  return useQuery({
    queryKey: ['content', page, pageSize],
    queryFn: async () => {
      const response = await listContentApiV1ContentGet({
        query: { page, page_size: pageSize },
      })
      return response.data
    },
  })
}
```

## When to Regenerate

You should regenerate the API client when:

1. **Backend API changes** - New endpoints, modified request/response models, or changed parameters
2. **After pulling changes** - If other developers have modified the backend
3. **Before building for production** - Ensure the client is up-to-date

## Troubleshooting

### "API server not running" error

Make sure the backend is running on port 8000:

```bash
cd director-ui
uv run uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

### Import errors after generation

1. Restart the Vite dev server
2. Clear browser cache
3. Check that `@/api/sdk.gen` path alias is configured in `vite.config.ts`

### TypeScript errors

If you see type mismatches:

1. Regenerate the client to match the current backend
2. Check that both frontend and backend are using the same data models
3. Update frontend code to match new type definitions

## API Endpoint Configuration

The backend API is configured to:
- Run on port 8000
- Serve OpenAPI spec at `/openapi.json`
- Include CORS headers for frontend development

To change the backend port, update:
1. Backend uvicorn command
2. Frontend generation script at `frontend/scripts/generate-api-client.sh`
3. Frontend API base URL configuration (if applicable)

## CI/CD Integration

For continuous integration:

```bash
# In your CI pipeline
cd director-ui/frontend

# Start backend in background
cd ../
uv run uvicorn src.api.app:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 5

# Generate API client
cd frontend
npm run generate-api

# Build frontend
npm run build

# Kill backend
kill $BACKEND_PID
```
