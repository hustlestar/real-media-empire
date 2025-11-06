# PowerPoint Generation System

AI-powered PowerPoint presentation generation using OpenAI GPT models and python-pptx.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Cost Management](#cost-management)
- [Customization](#customization)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

## Overview

The PPTX generation system creates professional PowerPoint presentations using AI to generate content and python-pptx for rendering. It follows the same architectural patterns as the film generation pipeline with provider abstraction, cost tracking, and content caching.

### Features

- **AI-Powered Content Generation**: Uses OpenAI GPT models to generate presentation outlines and detailed slide content
- **Template Support**: Load custom PPTX templates or create professional ones from scratch
- **Smart Content Fitting**: Automatically fits text to slide constraints with proper formatting
- **Cost Optimization**: Content caching, budget enforcement, and cost estimation
- **Flexible Styling**: Configurable fonts, colors, layouts, and themes
- **ZenML Pipeline Integration**: Optional orchestration with the existing pipeline infrastructure

### Supported Features

- **Professional Slide Structure**: Each slide has header, body, and footer sections
- Multiple slide layouts (title, content, two-column, image+text, blank)
- Bullet points with up to 3 indentation levels
- Speaker notes generation
- 4:3 and 16:9 aspect ratios
- Custom color schemes and fonts
- Configurable header/body/footer dimensions
- Cost tracking and reporting

### Slide Structure

Every content slide follows a consistent three-part structure:

```
┌─────────────────────────────────────────┐
│  HEADER (1.0")                          │  ← Title with primary color background
│  • Dark blue background (#1F4E78)      │
│  • White title text                     │
├─────────────────────────────────────────┤
│  BODY (6.0")                            │  ← Main content area
│  • White background                     │
│  • Bullet points or content            │
│  • Full margins for readability        │
├─────────────────────────────────────────┤
│  FOOTER (0.5")                          │  ← Slide metadata
│  • Light gray background (#E7E7E7)     │
│  • Slide number and date               │
└─────────────────────────────────────────┘
```

Title slides use full-screen background with centered title and subtitle.

## Architecture

### Component Structure

```
src/pptx_gen/
├── models.py              # Pydantic data models
├── generator.py           # Main orchestrator
├── template_manager.py    # Template handling
├── slide_builder.py       # Slide construction
├── cost_tracker.py        # Cost management
└── providers/
    ├── base.py           # Abstract provider interface
    └── content_provider.py  # OpenAI implementation

src/pipelines/
├── pptx_generation.py    # ZenML pipeline
└── steps/
    └── pptx_steps.py     # Pipeline steps

templates/
├── default_16x9.pptx     # Default 16:9 template
└── default_4x3.pptx      # Default 4:3 template
```

### Data Flow

1. **Request Creation**: User provides topic, brief, and parameters
2. **Cost Estimation**: Estimate OpenAI API costs before generation
3. **Cache Lookup**: Check if similar content exists (content-addressed caching)
4. **Content Generation**: AI generates outline and detailed slide content
5. **Template Loading**: Load custom template or create default
6. **Slide Building**: Construct slides using python-pptx
7. **File Saving**: Save PPTX file and metadata
8. **Cost Recording**: Track actual costs for reporting

### Provider Pattern

Following the film generation architecture:

```python
BaseContentProvider (ABC)
    ↓
OpenAIContentProvider
    - generate_outline()
    - generate_slide_content()
    - generate_all_content()
    - estimate_cost()
```

Future providers (Anthropic Claude, local LLMs) can be added by implementing `BaseContentProvider`.

## Getting Started

### Prerequisites

1. **OpenAI API Key**: Required for content generation
2. **Python 3.9+**: Via uv package manager
3. **Dependencies**: Installed via `uv sync`

### Installation

```bash
# Install dependencies
uv sync

# Set up environment variables
cp .env_template .env
# Edit .env and add your OPEN_AI_API_KEY
```

### Environment Configuration

Add to your `.env` file:

```env
# OpenAI API Key (required)
OPEN_AI_API_KEY=sk-...

# PPTX Settings (optional)
PPTX_GALLERY_DIR=./presentations
PPTX_DEFAULT_BUDGET_USD=5.00
PPTX_DEFAULT_MODEL=gpt-4o-mini

# Template paths (optional)
PPTX_TEMPLATE_16X9=./templates/default_16x9.pptx
PPTX_TEMPLATE_4X3=./templates/default_4x3.pptx
```

### Quick Start

Generate your first presentation:

```bash
cd src

uv run python -m pipelines.pptx_generation \
  --presentation-id "my_first_presentation" \
  --topic "Introduction to AI" \
  --brief "Overview of AI concepts for beginners" \
  --num-slides 10 \
  --budget-limit 1.00
```

Output will be saved to `./presentations/output/my_first_presentation_*.pptx`

## Usage

### Command Line Interface

The main CLI is `pipelines.pptx_generation`:

```bash
uv run python -m pipelines.pptx_generation [OPTIONS]
```

#### Required Options

- `--presentation-id TEXT`: Unique presentation ID
- `--topic TEXT`: Main topic or title

#### Content Options

- `--brief TEXT`: Detailed brief or description
- `--num-slides INTEGER`: Number of slides (default: 10)
- `--tone CHOICE`: Presentation tone
  - `professional` (default), `casual`, `motivational`, `educational`, `sales`, `technical`
- `--target-audience TEXT`: Target audience (e.g., "executives", "students")

#### Style Options

- `--template-path PATH`: Path to custom PPTX template
- `--aspect-ratio CHOICE`: `4:3` or `16:9` (default: 16:9)
- `--theme-name TEXT`: Theme name (default: professional)
- `--font-family TEXT`: Font family (default: Calibri)
- `--primary-color TEXT`: Primary color hex (default: #1F4E78)

#### Model Options

- `--provider TEXT`: Content provider (default: openai)
- `--model TEXT`: Model name (default: gpt-4o-mini)
  - `gpt-4o-mini`: Recommended, cost-effective ($0.15/1M input, $0.60/1M output)
  - `gpt-4o`: High quality ($5/1M input, $15/1M output)
  - `gpt-3.5-turbo`: Budget option ($0.50/1M input, $1.50/1M output)

#### Cost Options

- `--budget-limit FLOAT`: Budget limit in USD (stops if exceeded)
- `--output-dir PATH`: Output directory (default: ./presentations)

#### Pipeline Options

- `--use-zenml/--no-zenml`: Use ZenML pipeline (default: no)

### Examples

#### Basic Presentation

```bash
uv run python -m pipelines.pptx_generation \
  --presentation-id "intro_ai_2025" \
  --topic "Introduction to Artificial Intelligence" \
  --num-slides 8
```

#### Detailed Presentation with Brief

```bash
uv run python -m pipelines.pptx_generation \
  --presentation-id "sales_q3" \
  --topic "Q3 Sales Review" \
  --brief "Review Q3 performance metrics, highlight top achievements, discuss challenges, and outline Q4 goals" \
  --num-slides 15 \
  --tone sales \
  --target-audience "executive team"
```

#### Custom Styling

```bash
uv run python -m pipelines.pptx_generation \
  --presentation-id "tech_talk" \
  --topic "Modern Web Architecture" \
  --num-slides 12 \
  --tone technical \
  --font-family "Arial" \
  --primary-color "#0066CC" \
  --aspect-ratio "16:9"
```

#### With Budget Limit

```bash
uv run python -m pipelines.pptx_generation \
  --presentation-id "budget_demo" \
  --topic "Cost-Effective Marketing" \
  --num-slides 10 \
  --budget-limit 0.50 \
  --model gpt-4o-mini
```

#### With Custom Template

```bash
uv run python -m pipelines.pptx_generation \
  --presentation-id "branded_deck" \
  --topic "Company Overview" \
  --template-path "./templates/corporate_template.pptx" \
  --num-slides 10
```

### Programmatic Usage

For Python scripts:

```python
from pptx_gen.generator import generate_presentation

result = generate_presentation(
    topic="Machine Learning Basics",
    brief="Introduction to ML concepts for developers",
    num_slides=10,
    budget_limit=1.00,
    model='gpt-4o-mini'
)

print(f"Presentation saved to: {result.file_path}")
print(f"Cost: ${result.cost_usd:.4f}")
print(f"Slides: {result.slide_count}")
```

Advanced usage with full control:

```python
from decimal import Decimal
from pptx_gen.models import PresentationRequest, PresentationConfig, ToneType
from pptx_gen.generator import PresentationGenerator
from pptx_gen.cost_tracker import CostTracker

# Create request
request = PresentationRequest(
    presentation_id="my_pres_001",
    topic="Cloud Computing",
    brief="Overview of cloud services",
    num_slides=12,
    tone=ToneType.TECHNICAL,
    target_audience="developers"
)

# Create config
config = PresentationConfig(
    aspect_ratio='16:9',
    font_family='Helvetica',
    primary_color='#FF6600'
)

# Create cost tracker with budget
cost_tracker = CostTracker(budget_limit=Decimal('2.00'))

# Create generator
generator = PresentationGenerator(
    config=config,
    cost_tracker=cost_tracker
)

# Generate presentation
result = generator.generate(request, model='gpt-4o-mini')
```

## Cost Management

### Cost Estimation

Estimate costs before generation:

```python
from pptx_gen.cost_tracker import CostTracker
from pptx_gen.models import PresentationRequest

request = PresentationRequest(
    presentation_id="test",
    topic="Test Topic",
    num_slides=10
)

tracker = CostTracker()
estimated = tracker.estimate_cost(request, provider_name='openai', model='gpt-4o-mini')
print(f"Estimated cost: ${estimated:.4f}")
```

### Budget Enforcement

Set a budget limit to prevent overspending:

```bash
uv run python -m pipelines.pptx_generation \
  --topic "My Topic" \
  --budget-limit 1.00  # Stops if cost exceeds $1.00
```

If the budget is exceeded, a `BudgetExceededError` is raised and no charges occur.

### Content Caching

The system automatically caches generated content using content-addressed storage (SHA256 hash of request parameters). Identical requests reuse cached content at zero cost.

Cache location: `./presentations/cache/`

To bypass cache:

```python
generator.generate(request, skip_cache=True)
```

### Cost Reports

Cost reports are automatically saved to:
- Individual: `./presentations/cost_reports/presentation_*.json`
- Aggregated: Generated via `CostTracker.save_report()`

Example report:

```json
{
  "total_cost_usd": 0.85,
  "budget_limit_usd": 5.00,
  "remaining_budget_usd": 4.15,
  "total_presentations": 3,
  "cost_by_model": {
    "gpt-4o-mini": 0.60,
    "gpt-4o": 0.25
  },
  "average_cost_per_presentation": 0.28
}
```

### Model Pricing (2025)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Best For |
|-------|----------------------|------------------------|----------|
| gpt-4o-mini | $0.150 | $0.600 | **Recommended** - Cost-effective |
| gpt-3.5-turbo | $0.500 | $1.500 | Budget presentations |
| gpt-4o | $5.00 | $15.00 | High-quality content |
| gpt-4-turbo | $10.00 | $30.00 | Premium presentations |

**Typical Costs:**
- 10-slide presentation with gpt-4o-mini: ~$0.15 - $0.30
- 20-slide presentation with gpt-4o: ~$1.00 - $2.00

## Customization

### Custom Templates

Create a PowerPoint template with desired layouts and styling:

1. Open PowerPoint, design your template
2. Save as `.pptx`
3. Use with `--template-path`:

```bash
uv run python -m pipelines.pptx_generation \
  --template-path "./my_template.pptx" \
  --topic "My Topic"
```

### Tone Customization

Available tones (affects content style):
- `professional`: Formal, business-oriented
- `casual`: Conversational, friendly
- `motivational`: Inspirational, energetic
- `educational`: Clear, instructive
- `sales`: Persuasive, benefits-focused
- `technical`: Detailed, precise

### Color Schemes

Set custom colors via hex codes:

```python
config = PresentationConfig(
    primary_color='#1F4E78',    # Dark blue (header background)
    secondary_color='#2E75B6',  # Medium blue (accents)
    accent_color='#FFC000',     # Gold (highlights)
    text_color='#000000',       # Black (body text)
    background_color='#FFFFFF'  # White (body background)
)
```

### Layout Dimensions

Customize header, body, and footer heights:

```python
config = PresentationConfig(
    header_height=1.2,  # inches (default: 1.0)
    footer_height=0.6,  # inches (default: 0.5)
    margin=0.75,        # inches (default: 0.5)
)
```

This allows you to:
- Increase header for larger branding areas
- Adjust footer for more/less metadata
- Control content margins for readability

### Layout Types

Automatic layout selection based on content:
- `TITLE`: Title slide (first slide)
- `CONTENT`: Standard bullet points
- `TWO_COLUMN`: Split content
- `IMAGE_TEXT`: Text with image placeholder
- `BLANK`: Empty canvas
- `SECTION_HEADER`: Section dividers

## API Reference

### Core Classes

#### `PresentationRequest`

Input request model.

```python
PresentationRequest(
    presentation_id: str,        # Unique ID
    topic: str,                  # Main topic
    brief: Optional[str] = None, # Detailed description
    num_slides: int = 10,        # Target slide count
    tone: ToneType = 'professional',
    target_audience: Optional[str] = None,
    key_points: Optional[List[str]] = None,
    include_title_slide: bool = True,
    include_conclusion: bool = True
)
```

#### `PresentationConfig`

Configuration model.

```python
PresentationConfig(
    aspect_ratio: AspectRatio = '16:9',
    template_path: Optional[str] = None,
    theme_name: str = 'professional',
    font_family: str = 'Calibri',
    title_font_size: int = 44,
    body_font_size: int = 24,
    primary_color: str = '#1F4E78',
    secondary_color: str = '#2E75B6',
    accent_color: str = '#FFC000',
    text_color: str = '#000000',
    background_color: str = '#FFFFFF',
    max_bullets_per_slide: int = 5,
    max_chars_per_bullet: int = 100,
    enable_speaker_notes: bool = True
)
```

#### `PresentationGenerator`

Main orchestrator.

```python
generator = PresentationGenerator(
    config: PresentationConfig,
    cost_tracker: Optional[CostTracker] = None,
    cache_dir: Optional[str] = None,
    output_dir: Optional[str] = None
)

result = generator.generate(
    request: PresentationRequest,
    provider_name: str = 'openai',
    model: str = 'gpt-4o-mini',
    skip_cache: bool = False
) -> PresentationResult
```

#### `CostTracker`

Cost management.

```python
tracker = CostTracker(
    budget_limit: Optional[Decimal] = None,
    tracking_dir: Optional[str] = None
)

estimated = tracker.estimate_cost(request, provider_name, model)
tracker.check_budget(estimated)  # Raises BudgetExceededError if exceeded
tracker.record_presentation(result)
report = tracker.generate_report()
```

### Content Providers

#### `OpenAIContentProvider`

```python
from pptx_gen.providers.content_provider import create_content_provider

provider = create_content_provider(
    provider='openai',
    api_key=None,  # Uses OPEN_AI_API_KEY from env
    model='gpt-4o-mini'
)

outline = provider.generate_outline(request)
slide = provider.generate_slide_content(request, outline, slide_number, slide_title)
content = provider.generate_all_content(request)
cost = provider.estimate_cost(request)
```

## Troubleshooting

### Common Issues

#### "OpenAI API key not found"

**Solution**: Ensure `OPEN_AI_API_KEY` is set in `.env`:

```bash
echo "OPEN_AI_API_KEY=sk-..." >> .env
```

#### "Budget exceeded"

**Error**: `BudgetExceededError: Budget exceeded: $X > $Y`

**Solution**: Increase budget limit or use cheaper model:

```bash
--budget-limit 2.00
--model gpt-4o-mini  # Use cheaper model
```

#### "Template not found"

**Error**: `FileNotFoundError: Template not found: path/to/template.pptx`

**Solution**: Verify template path or omit `--template-path` to create default:

```bash
# Use default template
uv run python -m pipelines.pptx_generation \
  --topic "My Topic" \
  # No --template-path
```

#### "ZenML not available"

**Warning**: Pipeline falls back to standalone mode.

**Solution**: This is expected behavior. The system works without ZenML.

#### "Invalid JSON response from AI"

**Error**: `InvalidResponseError: Failed to parse JSON`

**Solution**: Retry the generation. This is rare and usually transient.

### Performance Tips

1. **Use gpt-4o-mini**: 4-6x cheaper than gpt-4o with good quality
2. **Enable caching**: Identical requests reuse content at zero cost
3. **Set appropriate num_slides**: More slides = higher cost
4. **Batch similar presentations**: Cache hits save money

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or via environment:

```bash
export PYTHONLOG=DEBUG
uv run python -m pipelines.pptx_generation ...
```

### Getting Help

- **Issues**: GitHub repository issues
- **Documentation**: This file (PPTX_GENERATION.md)
- **Architecture**: See CLAUDE.md for system overview
- **Film Generation**: See FILM_GENERATION.md for similar patterns

## Examples Gallery

### Example 1: Sales Presentation

```bash
uv run python -m pipelines.pptx_generation \
  --presentation-id "sales_deck_q4" \
  --topic "Q4 Sales Performance" \
  --brief "Review Q4 sales metrics, highlight top performers, discuss market trends, and set Q1 targets" \
  --num-slides 15 \
  --tone sales \
  --target-audience "sales team and executives" \
  --font-family "Arial" \
  --primary-color "#0066CC" \
  --budget-limit 2.00
```

### Example 2: Technical Tutorial

```bash
uv run python -m pipelines.pptx_generation \
  --presentation-id "docker_intro" \
  --topic "Introduction to Docker" \
  --brief "Explain containerization, Docker basics, and practical examples" \
  --num-slides 12 \
  --tone technical \
  --target-audience "developers" \
  --model gpt-4o-mini
```

### Example 3: Educational Lecture

```bash
uv run python -m pipelines.pptx_generation \
  --presentation-id "photosynthesis_101" \
  --topic "Photosynthesis: How Plants Make Food" \
  --num-slides 10 \
  --tone educational \
  --target-audience "high school students" \
  --font-family "Comic Sans MS"
```

### Example 4: Executive Brief

```bash
uv run python -m pipelines.pptx_generation \
  --presentation-id "exec_brief_2025" \
  --topic "2025 Strategic Priorities" \
  --brief "Company vision, strategic initiatives, financial outlook, and key investments" \
  --num-slides 8 \
  --tone professional \
  --target-audience "board of directors" \
  --template-path "./templates/corporate_template.pptx" \
  --budget-limit 3.00 \
  --model gpt-4o
```

## Next Steps

- **Explore Templates**: Create custom templates for your brand
- **Try Different Tones**: Experiment with tone settings for different audiences
- **Monitor Costs**: Review cost reports in `./presentations/cost_reports/`
- **Integrate with Pipelines**: Use with other media-empire pipelines
- **Extend Providers**: Add new content providers (Claude, local LLMs)

## Credits

Built using:
- **python-pptx**: PowerPoint generation library
- **OpenAI GPT**: Content generation models
- **Pydantic**: Data validation
- **ZenML**: Optional pipeline orchestration

Part of the **Media Empire** automated content creation system.
