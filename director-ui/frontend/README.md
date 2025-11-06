# Content Processing Frontend

Modern React + TypeScript frontend for the Content Processing API with auto-generated type-safe API client.

## ✅ Completed Setup

- [x] Vite + React + TypeScript project initialized
- [x] OpenAPI TypeScript client generation configured
- [x] Tailwind CSS setup with CSS variables
- [x] Path aliases configured (`@/` → `src/`)
- [x] React Query (TanStack Query) configured
- [x] React Router v6 setup
- [x] Utility libraries (clsx, tailwind-merge, class-variance-authority)
- [x] API client auto-generation script
- [x] Base App structure with routing

## 🚀 Getting Started

### Prerequisites

- API server running on `http://localhost:10000`
- Node.js 18+ installed

### Installation & Development

```bash
# Install dependencies (already done)
npm install

# Generate API client from running backend
npm run generate-api

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Building for Production

```bash
# Generate API client + build
npm run build

# Preview production build
npm run preview
```

## 📁 Project Structure

```
src/
├── api/                    # Auto-generated API client (gitignored)
│   ├── client.gen.ts      # HTTP client
│   ├── types.gen.ts       # TypeScript types from Pydantic schemas
│   ├── sdk.gen.ts         # API service functions
│   └── index.ts
├── lib/
│   ├── api-config.ts      # API client configuration
│   └── utils.ts           # Utility functions (cn, etc.)
├── pages/                 # Page components (TODO)
│   ├── ContentPage.tsx
│   └── JobsPage.tsx
├── components/            # Reusable components (TODO)
│   ├── ui/               # shadcn/ui components
│   ├── content/          # Content-related components
│   ├── processing/       # Job-related components
│   └── layout/           # Layout components
├── hooks/                # Custom hooks (TODO)
├── App.tsx               # Main app with routing
├── main.tsx              # Entry point
└── index.css             # Global styles
```

## 🔧 API Client Generation

The API client is auto-generated from the OpenAPI spec:

```bash
# Regenerate API client (run when backend API changes)
npm run generate-api
```

This script:
1. Checks if API server is running
2. Downloads `openapi.json` from `http://localhost:10000/openapi.json`
3. Generates TypeScript client in `src/api/`

**Note**: `src/api/` is gitignored - it's generated on-demand.

## 📝 Next Steps (TODO)

### 1. Create Page Components

Create `src/pages/ContentPage.tsx` and `src/pages/JobsPage.tsx` with basic layouts.

### 2. Create React Query Hooks

Example `src/hooks/useContent.ts`:
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  listContent,
  createContentFromUrl,
  getContentById
} from '@/api/sdk.gen'

export const useContentList = (page = 1, pageSize = 20) => {
  return useQuery({
    queryKey: ['content', page, pageSize],
    queryFn: () => listContent({ query: { page, page_size: pageSize } }),
  })
}

export const useCreateContentFromUrl = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createContentFromUrl,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content'] })
    },
  })
}
```

### 3. Install shadcn/ui Components

```bash
# Initialize shadcn/ui (use defaults)
npx shadcn-ui@latest init

# Install needed components
npx shadcn-ui@latest add button card table dialog form input select
npx shadcn-ui@latest add badge tabs textarea label toast
npx shadcn-ui@latest add dropdown-menu alert-dialog skeleton
```

### 4. Build Content Management UI

**ContentPage.tsx** should include:
- Table/grid showing all content items
- "Add Content" button → dialog/form
- Filters (source type: PDF/YouTube/Web)
- Pagination
- Actions (view, create job, delete)

### 5. Build Job Management UI

**JobsPage.tsx** should include:
- Table showing all processing jobs
- Status badges (pending/processing/completed/failed)
- Filters (status, processing type)
- "Create Job" button
- View results, retry failed jobs

### 6. Add Layout & Navigation

Create `src/components/layout/Layout.tsx` with:
- Sidebar navigation
- Header with app title
- Main content area
- Responsive hamburger menu

## 🎨 Styling

- **Tailwind CSS** for utility-first styling
- **CSS Variables** for theming (light/dark mode ready)
- **shadcn/ui** for pre-built accessible components

## 🔍 Type Safety

All API types are auto-generated from the FastAPI backend:

```typescript
import type {
  ContentResponse,
  ContentCreateFromURL,
  JobResponse,
  JobCreate
} from '@/api/types.gen'

// Fully typed with IntelliSense!
const content: ContentResponse = {
  id: '...',
  content_hash: '...',
  source_type: 'youtube',  // TypeScript knows valid values
  // ...
}
```

## 🚦 Environment Variables

Create `.env` file:

```bash
VITE_API_URL=http://localhost:10000/api
```

## 📦 Dependencies

### Runtime
- **React 19** - UI library
- **React Router v6** - Client-side routing
- **TanStack Query** - Server state management
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **date-fns** - Date formatting

### Development
- **TypeScript** - Type safety
- **Vite** - Build tool
- **@hey-api/openapi-ts** - API client generator
- **Tailwind CSS** - Styling utilities

## 🔗 API Endpoints

The frontend consumes these API endpoints:

### Content
- `POST /api/v1/content/from-url` - Create from URL
- `POST /api/v1/content/upload` - Upload PDF
- `GET /api/v1/content` - List content (paginated)
- `GET /api/v1/content/{id}` - Get content
- `GET /api/v1/content/{id}/text` - Get with extracted text
- `DELETE /api/v1/content/{id}` - Delete content

### Processing
- `POST /api/v1/processing/jobs` - Create job
- `GET /api/v1/processing/jobs` - List jobs (paginated)
- `GET /api/v1/processing/jobs/{id}` - Get job
- `GET /api/v1/processing/jobs/{id}/result` - Get job with result
- `POST /api/v1/processing/jobs/{id}/retry` - Retry job

## 📚 Documentation

- API documentation: `http://localhost:10000/docs` (Swagger UI)
- Generated types: `src/api/types.gen.ts`
- Generated services: `src/api/sdk.gen.ts`
