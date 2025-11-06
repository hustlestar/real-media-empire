"""
Text file parser for presentation content.

Allows users to provide presentation content in a simple text format.
"""

import re
from typing import List, Optional
from pathlib import Path

from .models import (
    SlideDefinition,
    SlideContent,
    BulletPoint,
    SlideLayout,
    ListType,
    PresentationOutline,
)


def parse_presentation_from_file(file_path: str) -> tuple[PresentationOutline, List[SlideDefinition]]:
    """
    Parse presentation content from text file.

    File Format:
    ```
    TITLE: Main Presentation Title
    SUBTITLE: Optional subtitle

    ---

    # Slide 1 Title
    - Bullet point with **bold** and *italic*
    - Another bullet
      - Sub-bullet (2 spaces indent)

    ---

    # Slide 2 Title
    1. First numbered item
    2. Second numbered item
      1. Sub-item (2 spaces indent)
    ```

    Args:
        file_path: Path to text file

    Returns:
        Tuple of (outline, slides)

    Raises:
        ValueError: If file format is invalid or no slides found
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Content file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError("Content file is empty")

    # Split into sections
    sections = content.split("---")

    # Parse header section (before first ---)
    header = sections[0].strip()
    title, subtitle = _parse_header(header)

    # Parse slide sections
    slide_sections = [s.strip() for s in sections[1:] if s.strip()]

    if not slide_sections:
        raise ValueError(
            "No slides found in content file. "
            "Make sure to separate slides with '---' on its own line.\n\n"
            "Example format:\n"
            "TITLE: My Title\n"
            "---\n"
            "# First Slide\n"
            "- Bullet point\n"
            "---\n"
            "# Second Slide\n"
            "- Another point\n"
        )

    slides = []
    slide_titles = []

    for idx, section in enumerate(slide_sections, start=1):
        slide_def = _parse_slide(section, idx)
        slides.append(slide_def)
        slide_titles.append(slide_def.content.title)

    # Create outline
    outline = PresentationOutline(title=title, subtitle=subtitle, slide_titles=slide_titles)

    return outline, slides


def _parse_header(header: str) -> tuple[str, Optional[str]]:
    """Parse header section for title and subtitle."""
    title = None
    subtitle = None

    for line in header.split("\n"):
        line = line.strip()
        if line.startswith("TITLE:"):
            title = line[6:].strip()
        elif line.startswith("SUBTITLE:"):
            subtitle = line[9:].strip()

    if not title:
        title = "Untitled Presentation"

    return title, subtitle


def _parse_slide(section: str, slide_number: int) -> SlideDefinition:
    """Parse a single slide section."""
    lines = section.split("\n")

    # First line is the title (starts with #)
    title_line = lines[0].strip()
    if title_line.startswith("#"):
        title = title_line.lstrip("#").strip()
    else:
        title = title_line

    # Parse bullets/content
    bullets = []
    content_lines = [line for line in lines[1:] if line.strip()]

    for line in content_lines:
        bullet = _parse_bullet_line(line)
        if bullet:
            bullets.append(bullet)

    # Determine layout
    layout = SlideLayout.TITLE if slide_number == 1 else SlideLayout.CONTENT

    slide_content = SlideContent(title=title, bullets=bullets)

    return SlideDefinition(slide_number=slide_number, layout_type=layout, content=slide_content)


def _parse_bullet_line(line: str) -> Optional[BulletPoint]:
    """
    Parse a single bullet line.

    Formats:
    - Bullet point (- or *)
    1. Numbered point
      - Indented sub-bullet (2 spaces)
      1. Indented sub-number (2 spaces)
    """
    # Count leading spaces for indentation level
    stripped = line.lstrip()
    indent_count = len(line) - len(stripped)
    level = min(indent_count // 2, 2)  # Max level 2

    # Determine list type
    list_type = ListType.BULLET

    # Check for bullet marker (- or *)
    if stripped.startswith("- ") or stripped.startswith("* "):
        text = stripped[2:].strip()
        list_type = ListType.BULLET
    # Check for numbered marker (1. 2. etc)
    elif re.match(r"^\d+\.\s", stripped):
        match = re.match(r"^\d+\.\s+(.*)$", stripped)
        text = match.group(1).strip()
        list_type = ListType.NUMBERED
    else:
        # No marker, skip this line
        return None

    if not text:
        return None

    return BulletPoint(text=text, level=level, list_type=list_type)


def create_example_file(output_path: str):
    """Create an example presentation content file."""
    example_content = """TITLE: My Presentation Title
SUBTITLE: A comprehensive guide

---

# Introduction
- Welcome to this presentation
- Overview of key topics
  - Subtopic 1
  - Subtopic 2
- Expected outcomes with **bold emphasis**

---

# Main Points
1. First important point with **key concept**
2. Second point with *technical term*
3. Third point
  1. Sub-point one
  2. Sub-point two

---

# Benefits
- Increased productivity by **50%**
- Improved *user experience*
- Cost reduction
  - Lower operational costs
  - Better resource utilization

---

# Implementation Steps
1. **Plan** your approach carefully
2. **Execute** with precision
3. **Monitor** progress regularly
4. **Adjust** based on feedback

---

# Conclusion
- Summary of key takeaways
- Next steps and **action items**
- Questions and answers
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(example_content)

    return output_path
