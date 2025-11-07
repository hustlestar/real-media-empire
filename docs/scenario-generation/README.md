## Scenario Generation System

Automatically generate high-quality cinematic shot definitions from text descriptions using Large Language Models via OpenRouter.

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Model Selection](#model-selection)
- [Cost Analysis](#cost-analysis)
- [Examples](#examples)
- [Integration](#integration)
- [Best Practices](#best-practices)

## Overview

The scenario generation system converts natural language scene descriptions into detailed shot-by-shot breakdowns ready for film generation. Instead of manually writing JSON shot definitions, you can describe a scene and let an LLM create professional cinematic shots with:

- Shot types (wide, medium, close-up, extreme close-up)
- Enhanced visual prompts with cinematic details
- Negative prompts to avoid unwanted elements
- Shot durations and sequencing
- Dialogue timing
- Metadata (characters, locations, styles, mood)

### Key Features

✅ **Multiple LLM Options**: Choose from 6 models with different quality/cost tradeoffs
✅ **Cinematic Expertise**: Prompts engineered for film-quality output
✅ **Cost Effective**: Generate 5-shot scenarios for $0.001-0.02
✅ **Flexible Configuration**: Per-pipeline or environment-based model selection
✅ **Seamless Integration**: Outputs directly compatible with film generation pipeline

## How It Works

```
Text Description
    ↓
OpenRouter API (LLM)
    ↓
Structured JSON (shots.json)
    ↓
Film Generation Pipeline
    ↓
Final Video
```

The system uses a carefully crafted prompt that instructs the LLM to think like a cinematographer, considering:
- Shot composition and framing
- Lighting and color grading
- Camera movements
- Emotional beats
- Visual continuity
- Technical specifications (8K, film grain, depth of field)

## Getting Started

### Prerequisites

1. **OpenRouter API Key** (required)
2. **Python environment** with uv

### Installation

Already included in the film generation system! Just need to add your API key.

### Configuration

1. **Get OpenRouter API Key**:
   - Go to https://openrouter.ai/keys
   - Sign up or log in
   - Create a new API key
   - Credits: $1-5 is plenty to start (1000+ scenarios)

2. **Add to `.env`**:
```env
OPENROUTER_API_KEY=sk-or-v1-...your_key_here...

# Optional: Set default model
SCENARIO_DEFAULT_MODEL=claude-3-haiku
```

3. **Verify Setup**:
```bash
cd src
uv run python -m pipelines.scenario_generation --list-models
```

## Usage

### Basic Command

```bash
cd src
uv run python -m pipelines.scenario_generation \
  --description "A detective enters a dimly lit office" \
  --output ../shots.json \
  --num-shots 7
```

### Full Options

```bash
uv run python -m pipelines.scenario_generation \
  --description "Your scene description here" \
  --output path/to/output.json \
  --num-shots 10 \
  --model claude-3-haiku \
  --style "film noir" \
  --mood "tense" \
  --duration 5 \
  --aspect-ratio 16:9
```

### Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--description` | `-d` | Scene description (required) | - |
| `--output` | `-o` | Output JSON path (required) | - |
| `--num-shots` | `-n` | Number of shots to generate | 5 |
| `--model` | `-m` | LLM model to use | claude-3-haiku |
| `--style` | `-s` | Visual style | None |
| `--mood` | - | Emotional mood | None |
| `--duration` | - | Default shot duration (seconds) | 5 |
| `--aspect-ratio` | - | Video aspect ratio | 16:9 |
| `--provider` | - | Provider type | openrouter |
| `--list-models` | - | Show available models | - |

### Output

Generates a `shots.json` file compatible with `film_generation.py`:

```json
[
  {
    "shot_id": "shot_001",
    "shot_number": 1,
    "shot_type": "wide",
    "enhanced_prompt": "8K cinematic establishing shot...",
    "negative_prompt": "cartoon, anime, low quality...",
    "duration": 5,
    "dialogue": null,
    "characters": ["detective"],
    "landscapes": ["office", "interior"],
    "styles": ["film noir", "cinematic"],
    "mood": "tense",
    "time_of_day": "night"
  },
  ...
]
```

## Model Selection

### Available Models

| Model | Quality | Speed | Cost/5 Shots | Best For |
|-------|---------|-------|--------------|----------|
| **claude-3.5-sonnet** | ⭐⭐⭐⭐⭐ | Slow | $0.01-0.02 | Premium productions |
| **claude-3-haiku** | ⭐⭐⭐⭐ | Fast | $0.001-0.002 | Most use cases (RECOMMENDED) |
| **gpt-4-turbo** | ⭐⭐⭐⭐ | Medium | $0.01-0.03 | High quality needs |
| **gpt-3.5-turbo** | ⭐⭐⭐ | Fast | $0.001-0.003 | Quick iterations |
| **llama-3.1-70b** | ⭐⭐⭐ | Medium | $0.0005-0.001 | Open source option |
| **gemini-pro** | ⭐⭐ | Fast | $0.0005-0.001 | Budget testing |

### Model Selection Strategies

**For Testing/Iteration** (gemini-pro):
```bash
--model gemini-pro  # Cheapest, fast feedback
```

**For Production** (claude-3-haiku):
```bash
--model claude-3-haiku  # Best quality/cost balance
```

**For Premium Projects** (claude-3.5-sonnet):
```bash
--model claude-3.5-sonnet  # Highest quality
```

**Environment Default**:
```env
# In .env
SCENARIO_DEFAULT_MODEL=claude-3-haiku
```

Then just omit `--model` flag.

## Cost Analysis

### Typical Costs

**5-Shot Scenario**:
- claude-3.5-sonnet: $0.01-0.02
- claude-3-haiku: $0.001-0.002 ⭐
- gpt-3.5-turbo: $0.001-0.003
- gemini-pro: $0.0005-0.001

**10-Shot Scenario**:
- claude-3-haiku: $0.002-0.004
- gemini-pro: $0.001-0.002

**100 Scenarios** (for content creation business):
- claude-3-haiku: $0.10-0.20
- gemini-pro: $0.05-0.10

### Cost Breakdown

Scenario generation costs depend on:
1. **Input tokens**: Your description length (~800-1000 tokens)
2. **Output tokens**: ~200 tokens per shot generated
3. **Model pricing**: See table above

Example calculation (claude-3-haiku, 5 shots):
- Input: 1000 tokens × $0.25/M = $0.00025
- Output: 1000 tokens × $1.25/M = $0.00125
- **Total: ~$0.0015**

### Full Pipeline Cost

**Scenario → Film** (5 shots, budget mode):
- Scenario generation (haiku): $0.002
- Film generation (Minimax): $0.270
- **Total: $0.272**

The scenario generation is only ~0.7% of total cost!

## Examples

### Example 1: Film Noir Detective

```bash
uv run python -m pipelines.scenario_generation \
  --description "A hard-boiled detective enters his dimly lit office on a rainy night. He pours whiskey, finds a mysterious envelope, and studies a cryptic photograph as thunder rumbles." \
  --output detective_scene.json \
  --num-shots 7 \
  --style "film noir" \
  --mood "tense"
```

**Output**: 7 cinematic shots with classic noir lighting and atmosphere.

### Example 2: Cyberpunk Street Scene

```bash
uv run python -m pipelines.scenario_generation \
  --description "A lone figure walks through a neon-drenched street market. Holographic ads flicker. They stop at a ramen stand, spot a suspicious character, then vanish into the crowd." \
  --output cyberpunk_market.json \
  --num-shots 10 \
  --style "cyberpunk, blade runner aesthetic" \
  --mood "mysterious" \
  --aspect-ratio 9:16
```

**Output**: Vertical format shots perfect for social media.

### Example 3: Nature Documentary

```bash
uv run python -m pipelines.scenario_generation \
  --description "A hiker reaches a mountain summit at dawn. Exhausted but triumphant, they gaze at endless peaks bathed in golden light. Tears of joy stream down their face." \
  --output summit_achievement.json \
  --num-shots 5 \
  --style "documentary, cinematic realism" \
  --mood "triumphant" \
  --model claude-3.5-sonnet
```

**Output**: Emotional, realistic shots with premium quality prompts.

### Example 4: Quick Test

```bash
uv run python -m pipelines.scenario_generation \
  --description "Chef prepares pasta" \
  --output test.json \
  --num-shots 3 \
  --model gemini-pro
```

**Output**: Quick, cheap test of the system.

## Integration

### Scenario → Film Pipeline

**Two-Step Process**:

1. **Generate shots**:
```bash
uv run python -m pipelines.scenario_generation \
  -d "Your scene" \
  -o my_shots.json \
  -n 5
```

2. **Generate film**:
```bash
uv run python -m pipelines.film_generation \
  --film_id my_film \
  --shots_json_path my_shots.json \
  --budget_limit 2.00
```

### Programmatic Usage

```python
import asyncio
from pipelines.tasks.film_tasks import generate_scenario_to_shots

async def main():
    shots = await generate_scenario_to_shots(
        description="A detective enters an office",
        num_shots=7,
        model="claude-3-haiku",
        style="film noir",
        mood="tense"
    )

    for shot in shots:
        print(f"{shot.shot_id}: {shot.shot_type}")

asyncio.run(main())
```

### As Part of Full Pipeline

```python
from pipelines.tasks.film_tasks import (
    ScenarioGenerationTask,
    FilmGenerationTask
)

async def generate_complete_film(description: str):
    # Step 1: Generate shots
    async with ScenarioGenerationTask(model='claude-3-haiku') as scenario_task:
        result = await scenario_task.generate_from_description(
            description=description,
            num_shots=7
        )
        shots = result.shots

    # Step 2: Generate film (implementation here...)
    pass
```

## Best Practices

### Writing Good Descriptions

**✅ Good Example**:
```
A hard-boiled detective enters his dimly lit office on a rainy night.
Shadows from venetian blinds cut across the room. He pours himself a
whiskey, notices a mysterious envelope on his desk, and opens it to
find a cryptic photograph. Thunder rumbles as he studies the photo
with growing concern.
```

**❌ Bad Example**:
```
Detective in office
```

### Key Elements to Include

1. **Setting**: Time, location, lighting conditions
2. **Characters**: Who is present, what they're doing
3. **Actions**: Specific movements and events
4. **Atmosphere**: Mood, sounds, visual details
5. **Emotional Arc**: Beginning, middle, end
6. **Sensory Details**: Sights, sounds, textures

### Style Suggestions

**Effective Style Tags**:
- "film noir" - Classic detective atmosphere
- "cyberpunk, blade runner aesthetic" - Futuristic neon
- "documentary, cinematic realism" - Natural, realistic
- "horror, found footage" - Scary, handheld feel
- "period drama, Victorian era" - Historical accuracy
- "action cinema, fast-paced" - High energy
- "romantic, dreamy" - Soft, emotional

**Mood Tags**:
- tense, mysterious, triumphant, terrifying
- nostalgic, peaceful, intense, uplifting
- melancholic, exciting, contemplative

### Model Selection Tips

1. **Start Cheap**: Use gemini-pro to test your description
2. **Iterate**: Refine description, test again
3. **Scale Up**: Use claude-3-haiku for final generation
4. **Premium Only When Needed**: Use claude-3.5-sonnet for client work

### Shot Count Guidelines

- **3-5 shots**: Quick scene, single beat
- **7-10 shots**: Complete scene with beginning/middle/end
- **12-15 shots**: Complex sequence with multiple locations
- **20+ shots**: Full short film or trailer

More shots = better coverage but higher generation cost (both LLM and film).

## Troubleshooting

### Common Issues

**"Missing OPENROUTER_API_KEY"**
- Add key to `.env` file
- Verify no typos in key name
- Restart shell to reload environment

**"Model not available"**
- Check spelling: `--model claude-3-haiku` not `--model claude-haiku`
- List available models: `--list-models`

**"Output format invalid"**
- The LLM occasionally produces invalid JSON
- Try again (different random seed may work)
- Try a different model (claude models are most reliable)

**"Costs more than expected"**
- Long descriptions increase input tokens
- Many shots increase output tokens
- Premium models cost 10-20x more
- Solution: Use cheaper model or reduce shot count

### Quality Issues

**Shots are too generic**:
- Add more specific details to description
- Include sensory information
- Specify camera angles if you have preferences
- Try claude-3.5-sonnet for more creative output

**Prompts lack cinematic detail**:
- This is unlikely with current system prompt
- Try claude-3-haiku or claude-3.5-sonnet
- GPT models may be less detailed

**Inconsistent character descriptions**:
- Describe characters clearly in original description
- Mention visual details (age, clothing, features)
- Use consistent names

## Advanced Features

### Custom System Prompts

The system prompt is built into `scenario_providers.py`. To customize:

1. Edit `_get_system_prompt()` method
2. Add your own cinematography guidelines
3. Adjust technical specifications
4. Change output format requirements

### Local LLM Support

For offline or private scenario generation:

```python
from film.providers.scenario_providers import LocalLLMScenarioProvider

# Coming soon - support for Ollama, LM Studio
```

### Batch Generation

Generate multiple scenarios at once:

```bash
#!/bin/bash
for scene in scene1.txt scene2.txt scene3.txt; do
  uv run python -m pipelines.scenario_generation \
    --description "$(cat $scene)" \
    --output "${scene%.txt}.json" \
    --num-shots 5
done
```

## API Reference

### ScenarioGenerationTask

```python
from pipelines.tasks.film_tasks import ScenarioGenerationTask

async with ScenarioGenerationTask(
    provider_type='openrouter',
    model='claude-3-haiku',
    api_key=None  # Or from environment
) as task:
    # Generate scenario
    result = await task.generate_from_description(
        description="Scene description",
        num_shots=5,
        style="film noir",
        mood="tense"
    )

    # Estimate cost
    cost = task.estimate_cost("Scene description", num_shots=5)

    # List models
    models = task.get_available_models()
```

### Convenience Function

```python
from pipelines.tasks.film_tasks import generate_scenario_to_shots

shots = await generate_scenario_to_shots(
    description="Scene description",
    num_shots=5,
    model="claude-3-haiku"
)
```

## Cost Comparison

### Scenario Generation vs Manual Writing

**Manual Writing**:
- Time: 30-60 minutes for 5 shots
- Cost: $0 (but your time is valuable!)
- Quality: Depends on your cinematography skills

**AI Generation** (claude-3-haiku):
- Time: 10-30 seconds
- Cost: $0.001-0.002
- Quality: Professional cinematography guidance
- Can iterate quickly

**Best Practice**: Use AI for first draft, manually refine for perfection.

## Examples Collection

See `examples/example_scenarios.txt` for 10+ pre-written scenarios covering:
- Film noir detective
- Cyberpunk street market
- Victorian tea party
- Mountain summit achievement
- Horror abandoned hospital
- Cooking show montage
- Romantic beach sunset
- Action car chase
- Product launch event
- Fantasy temple discovery

Each includes suggested settings and use cases.

## Future Enhancements

### Planned Features

- [ ] **Style presets**: One-click film noir, cyberpunk, etc.
- [ ] **Shot templates**: Common patterns (dialogue, action, montage)
- [ ] **Multi-scene support**: Generate full scripts
- [ ] **Storyboard generation**: Visual previews of shots
- [ ] **Character consistency**: Track character descriptions across shots
- [ ] **Local LLM support**: Ollama, LM Studio integration
- [ ] **A/B testing**: Compare outputs from different models
- [ ] **Prompt refinement**: Iterative improvement suggestions

---

**Ready to create cinematic content?** Start with the examples in `examples/example_scenarios.txt` and experiment with different models!

For questions or issues, see the main project documentation in `FILM_GENERATION.md` and `CLAUDE.md`.
