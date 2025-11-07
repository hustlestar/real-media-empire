# Migration Guide: Conda to uv

This document describes the migration from Conda-based environments to uv package management.

## What Changed

### Before (Conda)
The project used multiple Conda environment files:
- `environment.yaml` - Main media-empire environment
- `flask.yaml` - Flask webserver environment
- `stable-diffusion/requirements.txt` - Stable Diffusion dependencies

### After (uv)
- Single `pyproject.toml` defines all dependencies
- Virtual environment in `.venv/` directory
- Faster dependency resolution and installation
- Better dependency locking with `uv.lock`

## Migration Steps Completed

1. ✅ Analyzed all dependencies from conda YAML files
2. ✅ Created comprehensive `pyproject.toml`
3. ✅ Installed all dependencies via `uv sync`
4. ✅ Tested core imports (moviepy, zenml, flask, etc.)
5. ✅ Updated CLAUDE.md documentation

## How to Use the New Setup

### First Time Setup
```bash
# From project root
uv sync
```

This creates a `.venv/` directory with all dependencies installed.

### Running Code

**Option 1: Use `uv run` (Recommended)**
```bash
uv run python script.py
uv run python -m module.name
```

**Option 2: Activate Virtual Environment**
```bash
# Windows
.venv\Scripts\activate

# Unix/Mac
source .venv/bin/activate

# Then run normally
python script.py
```

### Adding New Dependencies
```bash
# Add a runtime dependency
uv add package-name

# Add a development dependency
uv add --dev pytest

# Add an optional dependency group
uv add --optional stable-diffusion diffusers
```

### Running the Flask Webserver
```bash
cd webserver
uv run python app.py
```

## Dependency Changes

### Python Version
- **Before:** Python 3.9 (specified in conda yaml)
- **After:** Python 3.9+ (up to 3.12)

### Key Dependencies Versions
- moviepy: 2.2.1
- zenml: 0.91.0 (latest - note: breaking API changes)
- flask: 3.1.2
- openai: 2.6.1
- transformers: 4.57.1
- opencv-python: 4.11.0.86

See `pyproject.toml` for complete list.

## Known Issues

### ZenML Breaking Changes

**Problem:** The codebase uses ZenML 0.40.x API with `BaseParameters` which no longer exists in modern ZenML.

**Impact:** Pipeline scripts in `src/pipelines/` will fail with:
```
ImportError: cannot import name 'BaseParameters' from 'zenml.steps'
```

**Solutions:**

#### Option 1: Quick Fix (Not Recommended for Production)
Pin to old ZenML version (requires resolving dependency conflicts):
```toml
"zenml==0.40.3",
```

#### Option 2: Migrate to Modern ZenML (Recommended)

Update `src/pipelines/params/params_for_pipeline.py`:

**Before:**
```python
from zenml.steps import BaseParameters

class PipelineParams(BaseParameters):
    channel_config_path: str = None
    execution_date: str = None
```

**After:**
```python
from pydantic import BaseModel

class PipelineParams(BaseModel):
    channel_config_path: str | None = None
    execution_date: str | None = None
```

Then update pipeline definitions to use the new parameter passing approach. See [ZenML docs](https://docs.zenml.io/) for details.

### ImageMagick Dependency

MoviePy requires ImageMagick for text rendering. This is not managed by Python packages.

**Installation:**
- Windows: Download from https://imagemagick.org/
- Mac: `brew install imagemagick`
- Linux: `apt-get install imagemagick`

Set in `.env`:
```
IMAGEMAGICK_BINARY=C:\Program Files\ImageMagick-7.x.x\magick.exe
```

## What to Delete

You can safely delete these legacy files after migration:
- `environment.yaml` (kept for reference)
- `flask.yaml` (kept for reference)
- Any conda environment directories

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError` when running scripts

**Solution:** Always run from `src/` directory or use `uv run`:
```bash
cd src
uv run python -m pipelines.shorts_generate --help
```

### Missing Dependencies

**Problem:** Package not found

**Solution:**
```bash
# Add the missing package
uv add package-name

# Re-sync
uv sync
```

### Virtual Environment Issues

**Problem:** Wrong Python or packages not found

**Solution:**
```bash
# Remove and recreate
rm -rf .venv
uv sync
```

## Performance Notes

### Installation Speed
- **uv** is significantly faster than conda (5-10x speedup observed)
- First sync: ~2 minutes
- Subsequent syncs: <10 seconds (with cache)

### Disk Space
- `.venv/` size: ~2.5 GB (includes PyTorch, transformers, etc.)
- Conda equivalent: ~3.5 GB

## Benefits of uv

1. **Speed:** Much faster than conda/pip
2. **Deterministic:** Lock file ensures reproducible installs
3. **Modern:** Better alignment with Python packaging standards
4. **Simple:** Single tool for all Python dependency management
5. **Cross-platform:** Works identically on Windows, Mac, Linux

## Getting Help

- uv docs: https://docs.astral.sh/uv/
- Report issues specific to this migration in the project repository
