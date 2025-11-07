# Media Empire Shared Library Architecture

## Overview

The `mediaempire-shared` library provides common functionality shared across multiple Media Empire projects (director-ui, main pipeline, etc.).

## Directory Structure

```
mediaempire-shared/
├── src/
│   ├── config.py          # Configuration utilities
│   ├── features/          # Junction/symlink → ../../src/features
│   └── social/            # Junction/symlink → ../../src/social
└── pyproject.toml         # Package configuration
```

## How It Works

The shared library contains the **actual source code** in `mediaempire-shared/src/`. Both the main project and director-ui install it as an **editable dependency** via uv. This ensures:

✅ **Single source of truth** - Code lives in `mediaempire-shared/src/`
✅ **No duplication** - All projects use the same installed package
✅ **Easy maintenance** - Update once, changes reflect immediately (editable install)
✅ **No symlinks** - Real code, not links

## Architecture

```
mediaempire-shared/
└── src/
    ├── features/          # Actual code (NOT a link)
    ├── social/            # Actual code (NOT a link)
    └── config.py

Main Project (media-empire)
└── Installs mediaempire-shared as editable dependency

director-ui/
└── Installs mediaempire-shared as editable dependency
```

## Installing the Shared Library

The shared library is installed as an editable package in dependent projects.

### In Main Project (media-empire)

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "mediaempire-shared",
    # ... other dependencies
]

[tool.uv.sources]
mediaempire-shared = { path = "mediaempire-shared", editable = true }
```

Then install:

```bash
uv sync
```

### In director-ui

Add to `director-ui/pyproject.toml`:

```toml
[tool.uv.sources]
mediaempire-shared = { path = "../mediaempire-shared", editable = true }

[project]
dependencies = [
    "mediaempire-shared",
    # ... other dependencies
]
```

Then install:

```bash
cd director-ui
uv sync
```

### Verification

```bash
cd director-ui
uv run python -c "from features.film.prompts.builder import CinematicPromptBuilder; print('✓ Shared library works!')"
```

## What's Included

### `features/`

Shared feature modules:
- **`features/film/`** - Film generation system
  - Prompt builders for cinematic AI prompts
  - Shot types, lighting, emotions catalogs
  - Provider integrations (Minimax, Kling, Runway, FAL, Replicate)
- **`features/publishing/`** - Multi-platform publishing
  - YouTube, TikTok, Instagram integration
  - Metadata management
  - Upload queue handling

### `social/`

Social media platform integrations:
- **`social/you_tube.py`** - YouTube API wrapper (`YouTubeUploader` class)
- OAuth2 credential management
- Video upload, metadata, thumbnail handling

## Adding New Shared Code

### Step 1: Add to Main Project

Place new shared code in the main `src/` directory:

```
src/
├── features/
│   └── your_new_feature/
│       ├── __init__.py
│       └── core.py
```

### Step 2: Update Shared Library Config

Edit `mediaempire-shared/pyproject.toml`:

```toml
[tool.hatch.build.targets.wheel]
packages = [
    "src/features",
    "src/social",
    "src/config.py",
    # Add new modules here if needed
]
```

### Step 3: Use in Dependent Projects

```python
# In director-ui or other projects
from features.your_new_feature import something
```

## Dependencies

The shared library has minimal dependencies to avoid conflicts:

```toml
dependencies = [
    "pydantic>=2.0.0",
    "openai>=1.0.0",
    "python-dotenv>=1.0.0",
    "requests>=2.31.0",
    "Pillow>=10.0.0",
    "google-auth-oauthlib>=1.0.0",
    "google-api-python-client>=2.0.0",
]
```

Dependent projects can add additional dependencies as needed.

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'features'`

**Solutions**:
1. Check junctions/symlinks exist:
   ```bash
   ls -la mediaempire-shared/src/
   ```
2. Reinstall shared library:
   ```bash
   cd director-ui
   uv sync --reinstall-package mediaempire-shared
   ```
3. Verify Python path includes shared library:
   ```bash
   uv run python -c "import sys; print('\n'.join(sys.path))"
   ```

### Broken Junctions on Windows

**Problem**: Junctions show as files instead of directories

**Solution**: Recreate junctions:
```powershell
cd mediaempire-shared/src
Remove-Item features, social -Force
New-Item -ItemType Junction -Path features -Target '..\..\src\features'
New-Item -ItemType Junction -Path social -Target '..\..\src\social'
```

### Code Changes Not Reflecting

**Problem**: Changes to shared code don't appear in dependent project

**Solutions**:
1. Check if editable install is active:
   ```bash
   uv pip show mediaempire-shared
   ```
   Should show `Editable project location: ...`

2. Restart application/server
3. Clear Python cache:
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} +
   ```

## Best Practices

1. **Only add truly shared code** - If it's specific to one project, keep it there
2. **Minimize dependencies** - Shared library should have few dependencies to avoid conflicts
3. **Version carefully** - Changes affect all dependent projects
4. **Test across projects** - Verify changes work in all dependent projects
5. **Document breaking changes** - Communicate API changes to all users

## Migration from Duplicated Code

If you find duplicated code:

1. **Identify the canonical version** - Usually the most complete/tested
2. **Move to main `src/`** - Place in appropriate directory
3. **Update imports** - Change all dependent projects
4. **Test thoroughly** - Verify functionality in all projects
5. **Remove duplicates** - Delete old versions

## CI/CD Considerations

### Testing

```bash
# Test shared library in isolation
cd mediaempire-shared
uv run python -m pytest tests/

# Test in dependent project
cd director-ui
uv run python -m pytest tests/
```

### Docker

When building Docker images, ensure junctions/symlinks are resolved:

```dockerfile
# Copy entire project structure including symlinks
COPY --chown=user:user . /app

# Or copy each directory explicitly
COPY --chown=user:user src/ /app/src/
COPY --chown=user:user mediaempire-shared/ /app/mediaempire-shared/
```

## Future Enhancements

- [ ] Publish to private PyPI for versioned distribution
- [ ] Add integration tests for cross-project compatibility
- [ ] Create GitHub Actions workflow for testing shared library changes
- [ ] Add pre-commit hooks to prevent breaking changes
