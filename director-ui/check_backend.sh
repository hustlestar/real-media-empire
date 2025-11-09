#!/bin/bash
# Quick Backend Verification Script
# Run this to check if your backend is properly set up and running

echo "🔍 Director UI Backend Health Check"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "src/api/app.py" ]; then
    echo "❌ ERROR: Not in director-ui directory!"
    echo "   Please run this from: ~/JACK/real-media-empire/director-ui"
    exit 1
fi

echo "✓ In correct directory"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "   Copying from .env.example..."
    cp .env.example .env
    echo "   📝 Please edit .env and add your API keys:"
    echo "      - FAL_API_KEY"
    echo "      - REPLICATE_API_TOKEN"
    echo "      - DATABASE_URL"
    echo "      - TELEGRAM_BOT_TOKEN (or use dummy value)"
    echo ""
else
    echo "✓ .env file exists"

    # Check for placeholder values
    if grep -q "your_fal_api_key_here" .env; then
        echo "⚠️  WARNING: FAL_API_KEY appears to be a placeholder"
        echo "   Update with real key from https://fal.ai/dashboard"
    fi

    if grep -q "your_replicate_api_token_here" .env; then
        echo "⚠️  WARNING: REPLICATE_API_TOKEN appears to be a placeholder"
        echo "   Update with real token from https://replicate.com/account/api-tokens"
    fi
    echo ""
fi

# Check if backend is running
echo "🌐 Checking if backend is running on port 10000..."
if lsof -i :10000 >/dev/null 2>&1; then
    echo "✓ Backend is running on port 10000"
    echo ""

    # Test health endpoint
    echo "🏥 Testing health endpoint..."
    if curl -s http://localhost:10000/api/health >/dev/null 2>&1; then
        echo "✓ Backend health check passed"
        echo "✓ API is responding correctly"
        echo ""
        echo "🎉 Backend is healthy and ready!"
    else
        echo "⚠️  Port 10000 is in use but health check failed"
        echo "   The process might be starting up or misconfigured"
    fi
else
    echo "❌ Backend is NOT running on port 10000"
    echo ""
    echo "📋 To start the backend:"
    echo "   Option 1 (Recommended): ./start-dev.sh"
    echo "   Option 2: ./start_api.sh"
    echo "   Option 3: PYTHONPATH=src uvicorn api.app:app --reload --host 0.0.0.0 --port 10000"
    echo ""
    echo "⚠️  IMPORTANT: Always include PYTHONPATH=src when starting manually!"
fi

echo ""
echo "📊 Process Status:"
# Show any python/uvicorn processes
if ps aux | grep -E "[p]ython.*api|[u]vicorn" >/dev/null 2>&1; then
    echo "Found Python/Uvicorn processes:"
    ps aux | grep -E "[p]ython.*api|[u]vicorn" | head -5
else
    echo "No Python/Uvicorn processes found"
fi

echo ""
echo "🔗 If everything is working, your API should be at:"
echo "   http://localhost:10000/api/health"
echo "   http://localhost:10000/docs (Swagger UI)"
