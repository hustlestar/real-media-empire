#!/bin/bash

# Install git hooks for the project
# Run this once after cloning the repository

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Installing git hooks...${NC}"

# Get the root directory
ROOT_DIR=$(git rev-parse --show-toplevel)
GIT_HOOKS_DIR="${ROOT_DIR}/.git/hooks"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create hooks directory if it doesn't exist
mkdir -p "$GIT_HOOKS_DIR"

# Install pre-commit hook
echo -e "${BLUE}Installing pre-commit hook...${NC}"
cp "${SCRIPT_DIR}/pre-commit" "${GIT_HOOKS_DIR}/pre-commit"
chmod +x "${GIT_HOOKS_DIR}/pre-commit"
echo -e "${GREEN}✓ Pre-commit hook installed${NC}"

echo ""
echo -e "${GREEN}✅ Git hooks installed successfully!${NC}"
echo ""
echo "The following hooks are now active:"
echo "  • pre-commit: Auto-regenerates TypeScript API client when backend changes"
echo ""
echo "To test the hook:"
echo "  1. Make a change to director-ui/src/api/ or director-ui/src/data/models.py"
echo "  2. Start backend: cd director-ui && uv run python -m api.app"
echo "  3. Commit your changes: git commit -m 'test'"
echo "  4. Hook will auto-regenerate and stage client files"
