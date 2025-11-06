# PPTX Generation Module

AI-powered PowerPoint presentation generation using OpenAI GPT models.

## Quick Start

```bash
# From src/ directory
uv run python -m pipelines.pptx_generation \
  --presentation-id "demo" \
  --topic "AI in Business" \
  --num-slides 10 \
  --budget-limit 1.00
```

## Module Structure

- `models.py` - Pydantic data models (requests, configs, results)
- `generator.py` - Main orchestrator class
- `template_manager.py` - Template loading and management
- `slide_builder.py` - Slide construction with python-pptx
- `cost_tracker.py` - Cost tracking and budget enforcement
- `providers/` - Content generation providers
  - `base.py` - Abstract base class
  - `content_provider.py` - OpenAI implementation

## Usage

### Programmatic

```python
from pptx_gen.generator import generate_presentation

result = generate_presentation(
    topic="Product Launch",
    brief="New feature overview for Q1 2025",
    num_slides=12,
    budget_limit=1.00,
    model='gpt-4o-mini'
)

print(f"Saved to: {result.file_path}")
```

### Advanced

```python
from pptx_gen.models import PresentationRequest, PresentationConfig
from pptx_gen.generator import PresentationGenerator
from pptx_gen.cost_tracker import CostTracker

# Create request
request = PresentationRequest(
    presentation_id="my_pres",
    topic="Machine Learning 101",
    num_slides=10
)

# Create config
config = PresentationConfig(
    aspect_ratio='16:9',
    font_family='Arial',
    primary_color='#0066CC'
)

# Create generator with cost tracking
cost_tracker = CostTracker(budget_limit=2.00)
generator = PresentationGenerator(config=config, cost_tracker=cost_tracker)

# Generate
result = generator.generate(request, model='gpt-4o-mini')
```

## Features

- **AI Content Generation**: GPT-powered outline and slide content
- **Template Support**: Custom templates or auto-generated
- **Cost Optimization**: Content caching and budget enforcement
- **Multiple Layouts**: Title, content, two-column, image+text, blank
- **Styling**: Configurable fonts, colors, sizes
- **Speaker Notes**: Auto-generated presenter notes

## Models

### Recommended: gpt-4o-mini
- Cost: $0.15/1M input, $0.60/1M output
- Quality: Good for most presentations
- Typical cost: $0.15-$0.30 per 10-slide deck

### Premium: gpt-4o
- Cost: $5/1M input, $15/1M output
- Quality: Best for high-stakes presentations
- Typical cost: $1-$2 per 10-slide deck

## Documentation

See `../../PPTX_GENERATION.md` for complete documentation.

## Examples

See `../../PPTX_GENERATION.md` for detailed examples including:
- Sales presentations
- Technical tutorials
- Educational lectures
- Executive briefs
