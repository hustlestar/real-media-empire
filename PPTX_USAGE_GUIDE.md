# PowerPoint Generation Usage Guide

Quick guide for generating professional PowerPoint presentations using AI or text files.

## Quick Start

### Method 1: AI Generation (Automated Content)

Generate a presentation from a topic - AI creates all content:

```bash
cd src
uv run python -m pipelines.pptx_generation \
  --presentation-id "my_presentation" \
  --topic "Introduction to Python Programming" \
  --brief "Learn Python basics for beginners" \
  --num-slides 10 \
  --budget-limit 2.00
```

**Cost:** ~$0.001-0.003 per presentation (very affordable with gpt-4o-mini)

### Method 2: Text File Input (Manual Content)

Generate from your own pre-written content - no AI needed:

```bash
cd src
uv run python -m pipelines.pptx_generation \
  --presentation-id "my_presentation" \
  --content-file "../examples/example_presentation_content.txt"
```

**Cost:** $0.00 (completely free!)

---

## Text File Format

Create a `.txt` file with this simple format:

```
TITLE: Your Presentation Title
SUBTITLE: Optional subtitle

---

# First Slide Title
- Bullet point with **bold text**
- Another point with *italic text*
  - Sub-bullet (2 spaces indent)

---

# Second Slide Title
1. First numbered item
2. Second numbered item with **emphasis**
3. Third item
  1. Sub-item (2 spaces indent)

---

# More Slides...
```

### Formatting Rules

- `**text**` = **bold** (for key concepts, numbers, actions)
- `*text*` = *italic* (for terms, definitions)
- `-` or `*` = bullet points
- `1.` `2.` = numbered lists
- 2 spaces indent = sub-items
- `---` = slide separator
- `#` = slide title

---

## Common Options

```bash
# Customize appearance
--primary-color "#1F4E78"          # Header accent color (hex)
--font-family "Calibri"             # Font family
--aspect-ratio "16:9"               # Or "4:3"

# AI generation options
--model "gpt-4o-mini"               # Cheap and fast (default)
--model "gpt-4o"                    # Higher quality
--tone "professional"               # Or casual, motivational, educational
--target-audience "executives"      # Customize content for audience

# Output
--output-dir "./my_presentations"   # Where to save files
```

---

## Features

### AI-Powered Content
- ✓ Intelligent content generation
- ✓ Automatic formatting (bold, italic)
- ✓ Smart list selection (bullets vs numbers)
- ✓ Context-aware structure

### Professional Design
- ✓ Clean modern layout
- ✓ Proper font hierarchy
- ✓ Good spacing and alignment
- ✓ Colored accent lines
- ✓ Professional footers

### Rich Formatting
- ✓ **Bold text** for emphasis
- ✓ *Italic text* for terms
- ✓ Bullet lists (•)
- ✓ Numbered lists (1. 2. 3.)
- ✓ Multi-level indentation

---

## Examples

### AI: Generate Marketing Presentation

```bash
cd src
uv run python -m pipelines.pptx_generation \
  --presentation-id "q4_marketing_2025" \
  --topic "Q4 Marketing Strategy" \
  --brief "Digital marketing plan with budget allocation" \
  --num-slides 12 \
  --tone "professional" \
  --target-audience "executives" \
  --budget-limit 3.00
```

### Text File: Custom Training Material

```bash
cd src
uv run python -m pipelines.pptx_generation \
  --presentation-id "python_training" \
  --content-file "./training_content.txt"
```

---

## Output

Presentations are saved to:
- Default: `src/presentations/`
- Custom: Use `--output-dir` option

**File naming:** `{presentation-id}_{timestamp}.pptx`

**Example:** `my_presentation_20251104_112142.pptx`

---

## Template Example

See `examples/example_presentation_content.txt` for a complete example you can copy and modify.

---

## Tips

### For AI Generation:
- Keep topics focused and specific
- Use `--brief` to guide content direction
- Choose appropriate `--tone` for audience
- Use `--budget-limit` to control costs
- Content is cached - regenerating same topic is free

### For Text Files:
- Don't overuse formatting - be selective
- Use numbered lists for steps/processes
- Use bullets for features/benefits
- Keep bullets concise (under 100 chars)
- Use 2-space indent for sub-items only

### General:
- Check presentations in PowerPoint after generation
- Titles are always bold automatically
- First slide is title slide (different layout)
- All markdown formatting is properly parsed

---

## Troubleshooting

**Error: "Either --topic or --content-file must be provided"**
- Provide at least one: either `--topic` for AI or `--content-file` for text input

**Text shows `**` markers:**
- This issue has been fixed - all slides now parse markdown correctly

**Lists not numbered:**
- Use `1.` `2.` format in text file
- For AI: it auto-detects when to use numbers (steps, processes, rankings)

**Sub-items not indented:**
- Use exactly 2 spaces before `-` or `1.` for sub-items

---

## More Information

- **Full docs:** See `PPTX_GENERATION.md`
- **Examples:** Check `examples/` directory
- **Code:** Source in `src/pptx_gen/`

---

## Quick Reference

| Feature | Command Option | Example |
|---------|---------------|---------|
| AI generation | `--topic` | `--topic "Sales Report"` |
| Text file | `--content-file` | `--content-file "my_content.txt"` |
| Slides | `--num-slides` | `--num-slides 8` |
| Budget | `--budget-limit` | `--budget-limit 1.00` |
| Model | `--model` | `--model "gpt-4o-mini"` |
| Color | `--primary-color` | `--primary-color "#FF5733"` |
| Font | `--font-family` | `--font-family "Arial"` |

---

**Need help?** Check the example files or run with `--help` for all options.
