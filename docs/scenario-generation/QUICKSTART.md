# Scenario Generation Quick Start

Generate professional cinematic shot definitions from plain text descriptions in 60 seconds!

## Prerequisites

- OpenRouter API key (get from https://openrouter.ai/keys)
- Python with `uv` (already set up if you've completed film setup)

## 30-Second Setup

**1. Get API Key** (1 minute):
- Visit https://openrouter.ai/keys
- Sign up (free $1 credit)
- Click "Create Key"
- Copy the key (starts with `sk-or-v1-`)

**2. Add to `.env`**:
```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**3. Done!** You're ready to generate scenarios.

## First Scenario (30 seconds)

Generate a 5-shot film noir scene:

```bash
cd src
uv run python -m pipelines.scenario_generation \
  --description "A detective enters his dimly lit office on a rainy night. He pours whiskey, finds a mysterious envelope, and studies a cryptic photograph." \
  --output ../my_first_scenario.json \
  --num-shots 5
```

**Expected**:
- Cost: ~$0.002 (under 1 cent!)
- Time: 10-30 seconds
- Output: `my_first_scenario.json` with 5 detailed shots

## What You Get

The system generates a JSON file with professional cinematic shots:

```json
[
  {
    "shot_id": "shot_001",
    "shot_number": 1,
    "shot_type": "wide",
    "enhanced_prompt": "8K cinematic establishing shot, dimly lit detective office interior, film noir style, venetian blinds casting dramatic shadows across worn wooden desk and filing cabinets, rain-streaked window with neon signs visible outside, warm amber desk lamp providing sole light source, cigarette smoke atmosphere, professional color grading with high contrast, shallow depth of field, photorealistic, film grain",
    "negative_prompt": "cartoon, anime, low quality, bright lighting, cheerful, modern, clean",
    "duration": 5,
    "dialogue": null,
    "characters": ["detective"],
    "landscapes": ["office", "interior", "urban"],
    "styles": ["film noir", "cinematic", "dramatic"],
    "mood": "tense",
    "time_of_day": "night"
  },
  // ... 4 more shots
]
```

Notice the LLM added:
- ✅ Technical camera details (8K, film grain, depth of field)
- ✅ Professional lighting specifications
- ✅ Cinematic style guidance
- ✅ Negative prompts to avoid unwanted elements
- ✅ Metadata for organization

## Next Step: Generate the Film

Use your generated shots to create the actual video:

```bash
uv run python -m pipelines.film_generation \
  --film_id "detective_scene" \
  --shots_json_path "../my_first_scenario.json" \
  --budget_limit 1.00
```

**Expected**:
- Cost: ~$0.27 (5 shots × $0.054)
- Time: ~8 minutes
- Output: 5 video clips with audio

## Try Different Styles

### Cyberpunk (Vertical Video)
```bash
uv run python -m pipelines.scenario_generation \
  -d "A hacker in a neon-lit room frantically typing, rain on windows, holographic displays everywhere" \
  -o cyberpunk.json \
  -n 5 \
  --style "cyberpunk, blade runner" \
  --mood "intense" \
  --aspect-ratio 9:16
```

### Nature Documentary
```bash
uv run python -m pipelines.scenario_generation \
  -d "A wolf pack hunting in snowy mountains at dawn" \
  -o nature.json \
  -n 7 \
  --style "documentary, wildlife photography" \
  --mood "majestic"
```

### Cooking Video
```bash
uv run python -m pipelines.scenario_generation \
  -d "Chef prepares fresh pasta from scratch, kneading dough, rolling it thin, cutting perfect ribbons" \
  -o cooking.json \
  -n 10 \
  --style "food photography, commercial" \
  --mood "appetizing"
```

## Model Selection

**Budget Mode** (gemini-pro):
```bash
--model gemini-pro  # ~$0.0005 per 5 shots
```

**Balanced Mode** (claude-3-haiku) - **RECOMMENDED**:
```bash
--model claude-3-haiku  # ~$0.002 per 5 shots
```

**Premium Mode** (claude-3.5-sonnet):
```bash
--model claude-3.5-sonnet  # ~$0.015 per 5 shots
```

## Cost Breakdown

**Complete Film Workflow** (5 shots):

| Step | Cost | Time |
|------|------|------|
| Scenario generation (haiku) | $0.002 | 30s |
| Film generation (budget) | $0.270 | 8 min |
| **Total** | **$0.272** | **8.5 min** |

Scenario generation is only 0.7% of total cost!

## Pro Tips

### 1. Start Cheap, Scale Up
```bash
# Test with cheapest model
--model gemini-pro

# Refine your description, test again
# ...

# Final generation with best quality
--model claude-3-haiku
```

### 2. Be Specific
❌ Bad: "A car chase"
✅ Good: "High-speed car chase through city at night, tires screeching, close-ups of driver's face, rearview mirror shows pursuers, final jump over river"

### 3. Include Sensory Details
- Lighting (golden hour, harsh shadows, neon glow)
- Sounds (thunder, whispers, sirens)
- Weather (rain, fog, snow)
- Atmosphere (tense, dreamy, chaotic)

### 4. Specify Shot Count
- **3-5 shots**: Quick scene
- **7-10 shots**: Complete sequence
- **12-15 shots**: Complex action

More shots = better coverage but higher cost (both LLM and film generation)

## Common Commands

**List available models**:
```bash
uv run python -m pipelines.scenario_generation --list-models
```

**Generate with style**:
```bash
uv run python -m pipelines.scenario_generation \
  -d "Your description" \
  -o output.json \
  --style "film noir" \
  --mood "tense"
```

**Vertical video (TikTok/Instagram)**:
```bash
--aspect-ratio 9:16
```

**Square video (Instagram posts)**:
```bash
--aspect-ratio 1:1
```

## Example Scenarios

See `examples/example_scenarios.txt` for 10+ pre-written scenarios:
- Film noir detective
- Cyberpunk street market
- Victorian tea party
- Mountain climbing
- Horror hospital
- Cooking show
- Beach romance
- Car chase
- Product launch
- Fantasy temple

Each includes full description and suggested settings.

## Full Workflow Example

**From idea to finished film in 10 minutes:**

```bash
cd src

# Step 1: Generate shots from description (~30 seconds, $0.002)
uv run python -m pipelines.scenario_generation \
  --description "A lone astronaut discovers alien artifacts on Mars" \
  --output mars_discovery.json \
  --num-shots 7 \
  --style "sci-fi, cinematic realism" \
  --model claude-3-haiku

# Step 2: Review/edit mars_discovery.json if needed

# Step 3: Generate the film (~9 minutes, $0.38)
uv run python -m pipelines.film_generation \
  --film_id mars_discovery \
  --shots_json_path ../mars_discovery.json \
  --budget_limit 1.00

# Done! Check E:/FILM_GALLERY/mars_discovery/
```

## Troubleshooting

**"Missing OPENROUTER_API_KEY"**
- Check `.env` file has the key
- No quotes needed: `OPENROUTER_API_KEY=sk-or-v1-...`
- Restart shell after editing `.env`

**"Rate limit exceeded"**
- Wait 1 minute
- You're on free tier (upgrade at openrouter.ai)

**Shots are too generic**
- Add more detail to description
- Try claude-3.5-sonnet for more creativity
- Specify camera angles, lighting, atmosphere

**JSON parse error**
- Try again (random variation may fix it)
- Try claude-3-haiku (more reliable JSON)

## What's Next?

1. **Try the examples**: Use scenarios from `examples/example_scenarios.txt`
2. **Experiment with models**: Compare gemini-pro vs claude-haiku vs claude-sonnet
3. **Combine workflows**: Generate → Review → Refine → Film
4. **Create your style**: Develop your own cinematography preferences

## Cost Estimates

**Content Creator** (10 films/month, 5 shots each):
- Scenario: 10 × $0.002 = $0.02
- Film: 10 × $0.27 = $2.70
- **Total: $2.72/month**

**Agency** (100 films/month, 7 shots each):
- Scenario: 100 × $0.003 = $0.30
- Film: 100 × $0.38 = $38.00
- **Total: $38.30/month**

Scenario generation is negligible compared to film generation!

## Learn More

- **Full Docs**: [SCENARIO_GENERATION.md](SCENARIO_GENERATION.md)
- **Film Generation**: [FILM_GENERATION.md](FILM_GENERATION.md)
- **Examples**: [examples/example_scenarios.txt](examples/example_scenarios.txt)

---

**Ready to create?** Start with one of the example scenarios and see what the AI generates!
