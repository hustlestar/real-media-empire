"""
Template Library for Common Video Formats

Pre-built templates for common content types to speed up production.

Templates:
- Quote videos
- Product demos
- Tutorials/How-tos
- Listicles (Top 5/10)
- Before/After comparisons
- Testimonials
- Announcements

Benefits:
- 5x faster video creation
- Consistent branding
- Proven formats

Run from project root with:
    PYTHONPATH=src python -c "from features.workflow.template_library import TemplateLibrary; ..."
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class VideoTemplate:
    """Video template configuration."""
    name: str
    category: str  # quote, demo, tutorial, listicle, etc.
    description: str
    duration_range: tuple  # (min, max) seconds
    required_assets: List[str]
    optional_assets: List[str]
    script_structure: List[str]
    visual_style: Dict
    recommended_platforms: List[str]


class TemplateLibrary:
    """
    Library of pre-built video templates for common formats.

    Speed up production with proven templates:
    - Faster creation (5x)
    - Consistent quality
    - Platform-optimized

    Example:
        >>> library = TemplateLibrary()
        >>> template = library.get_template("quote_video")
        >>> # Use template structure for production
    """

    TEMPLATES = {
        "quote_video": VideoTemplate(
            name="Quote Video",
            category="quote",
            description="Motivational quote with background and text overlay",
            duration_range=(15, 60),
            required_assets=["background_video", "quote_text", "author_name"],
            optional_assets=["background_music", "voiceover"],
            script_structure=[
                "Hook: Show quote preview",
                "Main: Full quote with animation",
                "CTA: Follow for more"
            ],
            visual_style={
                "text_animation": "fade_in_up",
                "background": "blurred_video",
                "color_scheme": "high_contrast"
            },
            recommended_platforms=["instagram_reels", "tiktok", "youtube_shorts"]
        ),
        "product_demo": VideoTemplate(
            name="Product Demo",
            category="demo",
            description="Quick product demonstration with features",
            duration_range=(30, 90),
            required_assets=["product_footage", "feature_list"],
            optional_assets=["music", "voiceover", "b_roll"],
            script_structure=[
                "Hook: Problem statement (3s)",
                "Solution: Introduce product (5s)",
                "Features: Show 3-5 key features (40s)",
                "CTA: Where to buy (5s)"
            ],
            visual_style={
                "pacing": "fast",
                "transitions": "quick_cuts",
                "text_style": "bold_captions"
            },
            recommended_platforms=["youtube", "facebook", "instagram"]
        ),
        "tutorial": VideoTemplate(
            name="Tutorial/How-To",
            category="tutorial",
            description="Step-by-step tutorial format",
            duration_range=(60, 300),
            required_assets=["screen_recording", "step_list"],
            optional_assets=["talking_head", "b_roll"],
            script_structure=[
                "Intro: What you'll learn (10s)",
                "Step 1: First step (30-60s)",
                "Step 2: Second step (30-60s)",
                "Step 3: Third step (30-60s)",
                "Outro: Summary + CTA (10s)"
            ],
            visual_style={
                "pacing": "clear_and_steady",
                "text_overlays": "step_numbers",
                "highlighting": "cursor_zoom"
            },
            recommended_platforms=["youtube", "linkedin"]
        ),
        "listicle": VideoTemplate(
            name="Listicle (Top 5/10)",
            category="listicle",
            description="Top N list format",
            duration_range=(45, 120),
            required_assets=["items_list", "item_footage"],
            optional_assets=["countdown_graphics", "music"],
            script_structure=[
                "Hook: Tease #1 item (5s)",
                "Item 5: Fifth place (10s)",
                "Item 4: Fourth place (10s)",
                "Item 3: Third place (10s)",
                "Item 2: Second place (10s)",
                "Item 1: First place (15s)",
                "CTA: Like & subscribe (5s)"
            ],
            visual_style={
                "number_graphics": "large_bold",
                "transitions": "swipe",
                "pacing": "energetic"
            },
            recommended_platforms=["youtube", "tiktok", "instagram"]
        ),
        "before_after": VideoTemplate(
            name="Before/After Comparison",
            category="comparison",
            description="Before and after transformation",
            duration_range=(15, 45),
            required_assets=["before_footage", "after_footage"],
            optional_assets=["transition_effect", "music"],
            script_structure=[
                "Before: Show initial state (10s)",
                "Transition: Transformation (5s)",
                "After: Show result (10s)",
                "CTA: Learn how (5s)"
            ],
            visual_style={
                "split_screen": True,
                "transition": "wipe_or_morph",
                "text": "BEFORE/AFTER labels"
            },
            recommended_platforms=["instagram", "tiktok", "youtube_shorts"]
        ),
        "testimonial": VideoTemplate(
            name="Customer Testimonial",
            category="testimonial",
            description="Customer review/testimonial",
            duration_range=(30, 90),
            required_assets=["customer_video", "customer_name", "quote"],
            optional_assets=["b_roll", "product_shots"],
            script_structure=[
                "Problem: Customer's initial challenge (15s)",
                "Solution: How product helped (30s)",
                "Result: Outcome achieved (20s)",
                "CTA: Try it yourself (10s)"
            ],
            visual_style={
                "captions": "word_by_word",
                "b_roll": "product_shots",
                "credibility": "show_customer_name"
            },
            recommended_platforms=["facebook", "youtube", "linkedin"]
        ),
        "announcement": VideoTemplate(
            name="Announcement",
            category="announcement",
            description="Product launch or news announcement",
            duration_range=(20, 60),
            required_assets=["announcement_text", "visuals"],
            optional_assets=["logo", "music", "countdown"],
            script_structure=[
                "Hook: Build anticipation (5s)",
                "Reveal: The announcement (10s)",
                "Details: Key information (20s)",
                "CTA: Next steps (10s)"
            ],
            visual_style={
                "energy": "high",
                "text_animation": "dynamic",
                "colors": "brand_colors"
            },
            recommended_platforms=["instagram", "twitter", "linkedin", "youtube"]
        )
    }

    def list_templates(self, category: Optional[str] = None) -> List[VideoTemplate]:
        """
        List available templates.

        Args:
            category: Filter by category (optional)

        Returns:
            List of templates
        """
        templates = list(self.TEMPLATES.values())

        if category:
            templates = [t for t in templates if t.category == category]

        return templates

    def get_template(self, template_id: str) -> Optional[VideoTemplate]:
        """Get specific template by ID."""
        return self.TEMPLATES.get(template_id)

    def get_template_structure(self, template_id: str) -> Dict:
        """
        Get template structure for production.

        Returns:
            Dictionary with template structure and requirements
        """
        template = self.get_template(template_id)
        if not template:
            return None

        return {
            "name": template.name,
            "description": template.description,
            "duration_range": template.duration_range,
            "required_assets": template.required_assets,
            "optional_assets": template.optional_assets,
            "script_structure": template.script_structure,
            "visual_style": template.visual_style,
            "platforms": template.recommended_platforms,
            "checklist": self._generate_checklist(template)
        }

    def _generate_checklist(self, template: VideoTemplate) -> List[str]:
        """Generate production checklist for template."""
        checklist = []

        # Required assets
        for asset in template.required_assets:
            checklist.append(f"☐ Prepare {asset}")

        # Script sections
        for section in template.script_structure:
            checklist.append(f"☐ Write: {section}")

        # Visual style
        for key, value in template.visual_style.items():
            checklist.append(f"☐ Apply {key}: {value}")

        # Platform optimization
        checklist.append(f"☐ Format for: {', '.join(template.recommended_platforms)}")

        return checklist


if __name__ == "__main__":
    print("Template Library")
    print("=" * 60)
    print("\nPre-built templates for common video formats")
    print("5x faster production with proven templates!")

    library = TemplateLibrary()
    templates = library.list_templates()

    print(f"\nAvailable Templates ({len(templates)}):\n")
    for t in templates:
        print(f"  • {t.name} ({t.category})")
        print(f"    {t.description}")
        print(f"    Duration: {t.duration_range[0]}-{t.duration_range[1]}s")
        print()
