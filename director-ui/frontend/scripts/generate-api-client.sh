#!/bin/bash
set -e

echo "🚀 Generating API client from OpenAPI spec..."

# Check if API is running
if ! curl -s http://localhost:8000/api/health > /dev/null; then
    echo "❌ API server not running on http://localhost:8000"
    echo "   Start it with: cd director-ui && uv run uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000"
    exit 1
fi

echo "✓ API server is running"

# Download OpenAPI spec
echo "📥 Downloading OpenAPI spec..."
curl -s http://localhost:8000/openapi.json -o openapi.json

if [ ! -f openapi.json ]; then
    echo "❌ Failed to download openapi.json"
    exit 1
fi

echo "✓ OpenAPI spec downloaded ($(wc -c < openapi.json) bytes)"

# Generate TypeScript client
echo "⚙️  Generating TypeScript client..."
npx @hey-api/openapi-ts \
  --input openapi.json \
  --output src/api

echo ""
echo "✅ API client generated successfully!"
echo "   📁 Types: src/api/types.gen.ts"
echo "   📁 Services: src/api/services.gen.ts"
echo "   📁 Client: src/api/client.ts"
echo ""