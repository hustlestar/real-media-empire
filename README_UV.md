# Quick Start with uv

This project now uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management.

## First Time Setup

```bash
# Install all dependencies (takes ~2 minutes first time)
uv sync
```

That's it! This creates a `.venv/` directory with all dependencies.

## Running Code

All Python commands should use `uv run`:

```bash
# Run a script
uv run python script.py

# Run a module
uv run python -m module.name

# Example: Start the webserver
cd webserver
uv run python app.py
```

## Common Commands

```bash
# Add a new package
uv add package-name

# Add a dev dependency
uv add --dev pytest

# Re-sync after changes
uv sync

# Activate the virtual environment manually (optional)
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Unix/Mac
```

## Quick Test

```bash
# Verify everything works
uv run python -c "import moviepy, zenml, flask, openai; print('Success!')"
```

## More Information

- **Full migration guide:** See [MIGRATION.md](MIGRATION.md)
- **Project documentation:** See [CLAUDE.md](CLAUDE.md)
- **uv documentation:** https://docs.astral.sh/uv/

## Important Notes

- Virtual environment is in `.venv/` (ignored by git)
- Dependencies defined in `pyproject.toml`
- Lock file `uv.lock` should be committed to git
- The project runs on Python 3.9-3.12
