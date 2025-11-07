# Director UI Frontend

React + TypeScript frontend for the Media Empire Director's Platform.

## Development Setup

```bash
# Install dependencies
npm install

# Generate API client from backend (backend must be running)
npm run generate-api

# Start dev server
npm run dev
```

## API Client Generation

This project uses **auto-generated TypeScript client** from the backend OpenAPI specification.

**Benefits:**
- No type duplication between backend and frontend
- Automatic type safety
- IntelliSense support

**Usage:**
```typescript
import { FilmService, type FilmShot } from '@/api/generated';

const shots = await FilmService.listShots();
```

**Regenerate after backend changes:**
```bash
npm run generate-api
```

See [../OPENAPI_CLIENT.md](../OPENAPI_CLIENT.md) for complete documentation.

## Project Structure

```
src/
├── api/
│   └── generated/      # Auto-generated from backend (DO NOT EDIT)
├── components/
│   ├── video/         # Phase 1: Dailies Room
│   ├── audio/         # Phase 2: Voice Direction
│   ├── timeline/      # Phase 3: Timeline Editor
│   ├── style/         # Phase 4: Visual Style Mixer
│   ├── iteration/     # Phase 5: Iteration Loop
│   └── asset/         # Phase 6: Asset Studio
├── pages/             # Main application pages
├── hooks/             # Custom React hooks
└── utils/             # Utility functions
```

## Build

```bash
# Production build (includes API generation)
npm run build

# Preview production build
npm run preview
```

## Technologies

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **TanStack Query** - Data fetching
- **Lucide React** - Icons
- **@hey-api/openapi-ts** - API client generation
