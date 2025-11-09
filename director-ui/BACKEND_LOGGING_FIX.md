# Fix: Backend Logging Not Appearing for Character Image Generation

## Problem

When making requests from the UI to generate character images, no logs appear in the backend console, even though the backend is running.

## Root Cause

The issue has **two parts**:

### 1. Vite Proxy Not Forwarding Requests

The Vite dev server (port 5173) was returning 500 errors when trying to proxy `/api/*` requests to the backend (port 10000). This means requests never reached the backend.

**Symptoms:**
```
GET http://localhost:5173/api/characters 500 (Internal Server Error)
GET http://localhost:5173/api/workspaces 500 (Internal Server Error)
```

### 2. Backend Started Without Proper Python Path

Running `uvicorn api.app:app` directly from the `director-ui/` directory without setting `PYTHONPATH=src` can cause import errors for relative imports like `from config.settings import BotConfig`.

## Solution

### Step 1: Stop All Running Processes

Kill any existing backend or frontend processes:
```bash
# Kill backend
pkill -f "uvicorn api.app"
pkill -f "api.main"

# Kill frontend
pkill -f "vite"
```

### Step 2: Start Backend with Proper PYTHONPATH

From the `director-ui/` directory:

**Option A: Use the provided startup script (recommended)**
```bash
./start-dev.sh
```

This will:
- Start the backend with `PYTHONPATH=src`
- Wait 2 seconds
- Start the frontend dev server
- Both will run together, and killing the frontend (Ctrl+C) also kills the backend

**Option B: Start backend only**
```bash
cd director-ui
PYTHONPATH=src uv run python -m api.main
```

Or with the startup script:
```bash
./start_api.sh
```

**Option C: Start with uvicorn directly (if you prefer)**
```bash
cd director-ui
PYTHONPATH=src uvicorn api.app:app --reload --host 0.0.0.0 --port 10000
```

⚠️ **Important:** Always include `PYTHONPATH=src` when starting the backend!

### Step 3: Start Frontend (if using Option B or C)

In a separate terminal:
```bash
cd director-ui/frontend
npm run dev
```

### Step 4: Verify Setup

1. **Check backend is running:**
   ```bash
   curl http://localhost:10000/api/health
   ```
   Should return 200 OK

2. **Check frontend proxy:**
   - Open http://localhost:5173 in your browser
   - Open browser DevTools → Network tab
   - Navigate to a page that makes API calls
   - You should see requests to `/api/...` being proxied

3. **Check backend logs:**
   In your backend terminal, you should now see logs for every request:
   ```
   INFO:     127.0.0.1:xxxxx - "GET /api/characters HTTP/1.1" 200 OK
   ```

### Step 5: Test Character Image Generation

1. Navigate to the Character Library page in the UI
2. Create a new character or select an existing one
3. Click "Generate Image"
4. You should now see detailed logs in the backend console:

```
================================================================================
CHARACTER IMAGE GENERATION REQUEST
Character ID: abc-123
Model: flux-dev
Number of images: 1
Using model: FLUX.1 Dev (fal)
Cost per image: $0.0250
Starting image generation with FAL provider...
Generating image 1/1 (seed: None)...
✓ Image 1 generated: https://fal.media/files/...
Saving 1 images to assets table...
✓ Asset saved - ID: xyz, URL: https://..., Cost: $0.0250
Generation completed successfully!
Total time: 12.34s
Total cost: $0.0250
================================================================================
```

## What Changed

### 1. Enhanced Vite Proxy Configuration

Updated `frontend/vite.config.ts` to add better error logging and debugging:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:10000',
      changeOrigin: true,
      secure: false,
      rewrite: (path) => path,
      configure: (proxy, _options) => {
        proxy.on('error', (err, _req, _res) => {
          console.log('proxy error', err);
        });
        proxy.on('proxyReq', (proxyReq, req, _res) => {
          console.log('Sending Request to the Target:', req.method, req.url);
        });
        proxy.on('proxyRes', (proxyRes, req, _res) => {
          console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
        });
      },
    },
  },
}
```

Now you'll see proxy activity in the Vite dev server console:
```
Sending Request to the Target: GET /api/characters
Received Response from the Target: 200 /api/characters
```

### 2. Added Environment Configuration

Created `.env` file with API key placeholders and updated `.env.example` to include `REPLICATE_API_TOKEN`.

Don't forget to add your real API keys to `.env`:
```bash
FAL_API_KEY=fal-your-actual-key
REPLICATE_API_TOKEN=r8_your-actual-token
```

## Troubleshooting

### Still no logs appearing?

1. **Check backend is actually running:**
   ```bash
   ps aux | grep "api.main\|uvicorn"
   curl http://localhost:10000/api/health
   ```

2. **Check Vite proxy in frontend console:**
   - Open browser DevTools → Console
   - Look for "Sending Request to the Target" messages
   - If you see "proxy error", the backend isn't reachable

3. **Check if requests are reaching backend:**
   - Look at the backend console
   - Every request should show: `INFO: 127.0.0.1:xxxxx - "GET /api/... HTTP/1.1" 200 OK`
   - If not appearing, the proxy isn't working

4. **Restart everything:**
   - Kill all processes (backend and frontend)
   - Restart using `./start-dev.sh`
   - Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)

### 500 Errors from Vite proxy?

If you see `500 (Internal Server Error)` for API requests:

1. **Backend not running on port 10000:**
   ```bash
   lsof -i :10000
   # Should show uvicorn or python process
   ```

2. **PYTHONPATH not set:**
   - Always use `PYTHONPATH=src` when starting the backend
   - Or use the provided startup scripts

3. **Database connection failed:**
   - Check `DATABASE_URL` in `.env`
   - Make sure PostgreSQL is running:
     ```bash
     psql $DATABASE_URL -c "SELECT 1"
     ```

### Image generation fails silently?

1. **Check API keys in .env:**
   ```bash
   cd director-ui
   grep "^FAL_API_KEY=" .env
   grep "^REPLICATE_API_TOKEN=" .env
   ```
   These should NOT be placeholder values!

2. **Restart backend after changing .env:**
   - The backend only reads `.env` on startup
   - Kill backend and restart after adding real API keys

3. **Enable DEBUG logging:**
   In `.env`:
   ```bash
   LOG_LEVEL=DEBUG
   ```
   Restart backend to see even more detailed logs.

## Summary

The logging wasn't working because:
1. ❌ The Vite proxy wasn't forwarding requests to the backend
2. ❌ Backend might have been started without `PYTHONPATH=src`
3. ✅ Now fixed with enhanced proxy config and proper startup procedures

Always use the startup scripts or remember to set `PYTHONPATH=src`!
