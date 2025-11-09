# Setting Up API Keys for Character Image Generation

## Current Issue

The backend is not running, which is why you're not seeing logs for image generation requests from the UI.

## Root Cause

The `.env` file in `director-ui/` currently has **placeholder values**:
```
FAL_API_KEY=your_fal_api_key_here
REPLICATE_API_TOKEN=your_replicate_api_token_here
```

These need to be replaced with your actual API keys.

## Setup Steps

### 1. Add Your Real API Keys to `.env`

Edit `director-ui/.env` and replace the placeholder values:

```bash
# Image Generation Providers (for Character Generation)
# REQUIRED: FAL.ai for FLUX models (flux-pro, flux-dev, flux-schnell)
FAL_API_KEY=fal-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# REQUIRED: Replicate for SDXL and other models
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Where to find your keys:**
- FAL API Key: https://fal.ai/dashboard (format: `fal-...`)
- Replicate Token: https://replicate.com/account/api-tokens (format: `r8_...`)

### 2. Add Other Required Environment Variables

The backend also needs these to start:

```bash
# Required Settings
TELEGRAM_BOT_TOKEN=your_bot_token_here  # Or use a dummy value if not using Telegram
DATABASE_URL=postgresql://user:password@localhost:5432/director_ui
```

For local development, you can use:
```bash
DATABASE_URL=postgresql://botuser:botpass@localhost:5432/pdf_link_youtube_to_anything_tg_bot
```

### 3. Start the Backend

From the `director-ui/` directory:

**Option A: Start backend and frontend together**
```bash
./start-dev.sh
```

**Option B: Start backend only**
```bash
./start_api.sh
```

Or manually:
```bash
PYTHONPATH=src .venv/bin/python -m api.main
```

### 4. Verify Backend is Running

You should see output like:
```
INFO:     Starting Content Processing API
INFO:     Host: 0.0.0.0
INFO:     Port: 10000
INFO:     Documentation: http://0.0.0.0:10000/docs
...
INFO:     Configuration
INFO:       FAL_API_KEY: fal-****
INFO:       REPLICATE_API_TOKEN: r8_****
```

### 5. Test the API

Open http://localhost:10000/docs to see the API documentation.

Or test with curl:
```bash
curl http://localhost:10000/api/health
```

### 6. Enable Debug Logging (Optional)

To see detailed logs for image generation, change this in `.env`:
```bash
LOG_LEVEL=DEBUG
```

Then restart the backend.

## Expected Logs for Image Generation

Once the backend is running with real API keys, you'll see logs like:

```
================================================================================
CHARACTER IMAGE GENERATION REQUEST
Character ID: abc-123-def
Model: flux-dev
Number of images: 1
Seed: None
Add to character: False
Using model: FLUX.1 Dev (fal)
Cost per image: $0.0250
Generating for character: John Doe (ID: abc-123-def)
Using character consistency prompt
Final prompt (500 chars):
  Character: John Doe (Human)
Physical Attributes:
- Age: 30
...
Starting image generation with FAL provider...
Generating image 1/1 (seed: None)...
✓ Image 1 generated: https://fal.media/files/...
Saving 1 images to assets table...
Saving asset 1/1: John Doe_FLUX.1 Dev_generation_1
✓ Asset saved - ID: xyz, URL: https://fal.media/files/..., Cost: $0.0250
Generation completed successfully!
Total time: 12.34s
Total cost: $0.0250
Generated 1 images
================================================================================
```

## Troubleshooting

**"Port 10000 already in use"**
- Check what's using it: `lsof -i :10000`
- Kill the process or change `API_PORT` in `.env`

**"FAL_API_KEY not set"**
- Make sure you replaced the placeholder in `.env`
- Restart the backend after changing `.env`

**"Database connection failed"**
- Make sure PostgreSQL is running
- Check the `DATABASE_URL` in `.env`
- Or start with Docker: `docker-compose up -d postgres`

**Still no logs appearing**
- Check the backend is actually running: `ps aux | grep api.main`
- Check the frontend is proxying to the right port (should be 10000)
- Open browser DevTools Network tab to see if requests are reaching the backend
