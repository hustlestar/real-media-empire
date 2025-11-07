# Media Empire - Complete Restructuring Plan

## Current Problems
1. Root directory has 12+ documentation files (swamp)
2. "pdf-link-youtube-to-anything-tg-bot" - unclear, too long name
3. Test files scattered in root
4. No clear organization

## Proposed New Structure

```
media-empire/
├── README.md                          # Main readme
├── pyproject.toml                     # Python dependencies
├── uv.lock                           # Lock file
│
├── docs/                              # ALL documentation here
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── film-generation/
│   │   ├── README.md
│   │   ├── QUICKSTART.md
│   │   └── API.md
│   ├── pptx-generation/
│   │   ├── README.md
│   │   ├── USAGE.md
│   │   └── API.md
│   ├── scenario-generation/
│   │   ├── README.md
│   │   └── IMPLEMENTATION.md
│   ├── publishing/
│   │   └── PLATFORMS.md
│   └── migration/
│       └── UV_MIGRATION.md
│
├── director-ui/                       # Renamed from pdf-link-youtube-to-anything-tg-bot
│   ├── README.md
│   ├── backend/                       # FastAPI backend
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── routers/
│   │   │   │   │   ├── projects.py
│   │   │   │   │   ├── assets.py
│   │   │   │   │   ├── characters.py
│   │   │   │   │   ├── publishing.py
│   │   │   │   │   ├── accounts.py
│   │   │   │   │   └── workflows.py
│   │   │   │   ├── schemas/
│   │   │   │   └── app.py
│   │   │   ├── services/
│   │   │   │   ├── film_service.py
│   │   │   │   ├── asset_service.py
│   │   │   │   ├── publishing_service.py
│   │   │   │   └── character_service.py
│   │   │   ├── models/              # SQLAlchemy models
│   │   │   ├── core/                 # Core utilities
│   │   │   └── main.py
│   │   ├── alembic/                  # Database migrations
│   │   ├── pyproject.toml
│   │   └── .env.example
│   │
│   └── frontend/                      # React frontend
│       ├── src/
│       │   ├── pages/
│       │   │   ├── Dashboard.tsx
│       │   │   ├── Projects.tsx
│       │   │   ├── Assets.tsx
│       │   │   ├── Characters.tsx
│       │   │   ├── Publishing.tsx
│       │   │   └── Workflows.tsx
│       │   ├── components/
│       │   │   ├── ui/              # Reusable UI components
│       │   │   ├── AssetCard.tsx
│       │   │   ├── ProjectCard.tsx
│       │   │   ├── CharacterCard.tsx
│       │   │   └── PublishQueue.tsx
│       │   ├── hooks/
│       │   ├── api/                  # Generated API client
│       │   └── App.tsx
│       ├── package.json
│       └── vite.config.ts
│
├── src/                               # Core Python codebase
│   ├── features/                      # NEW: Feature-based organization
│   │   ├── film/
│   │   │   ├── generator.py
│   │   │   ├── cache.py
│   │   │   ├── cost_tracker.py
│   │   │   ├── metadata.py
│   │   │   ├── prompts/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── cinematic_styles.py
│   │   │   │   ├── shot_types.py
│   │   │   │   └── builder.py
│   │   │   └── providers/
│   │   ├── publishing/
│   │   │   ├── manager.py
│   │   │   ├── queue.py
│   │   │   ├── platforms/
│   │   │   │   ├── base.py
│   │   │   │   ├── youtube.py
│   │   │   │   ├── tiktok.py
│   │   │   │   ├── instagram.py
│   │   │   │   ├── facebook.py
│   │   │   │   └── linkedin.py
│   │   │   └── adapters/
│   │   │       └── upload_post.py
│   │   ├── accounts/
│   │   │   ├── manager.py
│   │   │   ├── models.py
│   │   │   └── storage.py
│   │   ├── content_library/
│   │   │   ├── manager.py
│   │   │   ├── metadata.py
│   │   │   └── states.py
│   │   └── workflows/
│   │       ├── engine.py
│   │       └── templates/
│   │
│   ├── audio/                         # Existing
│   ├── video/                         # Existing
│   ├── image/                         # Existing
│   ├── text/                          # Existing
│   ├── social/                        # Migrate to features/publishing
│   ├── data/                          # Database models
│   └── config.py
│
├── tests/                             # All tests here
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── examples/                          # Example files
│   ├── shots.json
│   ├── workflows/
│   └── prompts/
│
├── scripts/                           # Utility scripts
│   ├── migrate_docs.py
│   └── setup_dev.sh
│
└── data/                              # Data storage
    ├── assets/
    ├── projects/
    ├── cache/
    └── temp/
```

## Migration Steps

### Step 1: Clean Root Directory
```bash
# Move all docs
mkdir -p docs/{film-generation,pptx-generation,scenario-generation,publishing,migration}
mv FILM_GENERATION.md docs/film-generation/README.md
mv PPTX_GENERATION.md docs/pptx-generation/README.md
mv SCENARIO_GENERATION.md docs/scenario-generation/README.md
# ... etc

# Move test files
mv test_*.py tests/

# Remove old files
rm -f environment.yaml flask.yaml airflow.yaml identifier.sqlite
```

### Step 2: Rename Main UI Directory
```bash
mv pdf-link-youtube-to-anything-tg-bot director-ui
```

### Step 3: Integrate Backend with Main Codebase
- Keep director-ui/backend as API server
- Use src/ for core business logic
- director-ui/backend/services/ imports from src/features/

### Step 4: Update All Import Paths
- Update director-ui imports
- Update main src imports
- Update test imports

## Benefits

1. ✅ Clean root directory (3 files instead of 20+)
2. ✅ Clear naming ("director-ui" vs "pdf-link-youtube-to-anything-tg-bot")
3. ✅ Organized documentation
4. ✅ Separation of concerns
5. ✅ Scalable structure
6. ✅ Easy to navigate
