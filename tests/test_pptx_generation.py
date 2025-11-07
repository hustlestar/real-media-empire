"""
Test script to generate a sample presentation with header/body/footer structure.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_presentation_generation():
    """Test generating a simple presentation."""
    from pptx_gen.models import (
        PresentationRequest,
        PresentationConfig,
        ToneType,
        AspectRatio,
        SlideDefinition,
        SlideContent,
        SlideLayout,
        BulletPoint,
        PresentationOutline,
    )
    from pptx_gen.template_manager import TemplateManager
    from pptx_gen.slide_builder import SlideBuilder

    print("="*60)
    print("Testing PPTX Generation with Header/Body/Footer")
    print("="*60)
    print()

    # Create config
    config = PresentationConfig(
        aspect_ratio=AspectRatio.RATIO_16_9,
        theme_name='professional',
        font_family='Calibri',
        primary_color='#1F4E78',
        secondary_color='#2E75B6',
        accent_color='#FFC000',
    )

    # Create template manager and load presentation
    print("1. Creating template manager...")
    template_manager = TemplateManager(config)
    template_manager.load_or_create_presentation()
    print(f"   [OK] Presentation loaded: {template_manager.presentation.slide_width.inches}\" x {template_manager.presentation.slide_height.inches}\"")
    print()

    # Create slide builder
    print("2. Creating slide builder...")
    slide_builder = SlideBuilder(template_manager, config)
    print(f"   [OK] Slide builder initialized")
    print(f"   - Header height: {slide_builder.HEADER_HEIGHT}\"")
    print(f"   - Body height: {slide_builder.body_height:.2f}\"")
    print(f"   - Footer height: {slide_builder.FOOTER_HEIGHT}\"")
    print()

    # Create title slide
    print("3. Creating title slide...")
    title_slide = SlideDefinition(
        slide_number=1,
        layout_type=SlideLayout.TITLE,
        content=SlideContent(
            title="Test Presentation",
            text_content="Testing Header, Body, and Footer Structure",
            bullets=[]
        )
    )
    slide_builder.build_slide(title_slide)
    print("   [OK] Title slide created")
    print()

    # Create content slides
    print("4. Creating content slides...")
    for i in range(2, 5):
        content_slide = SlideDefinition(
            slide_number=i,
            layout_type=SlideLayout.CONTENT,
            content=SlideContent(
                title=f"Slide {i}: Test Content",
                bullets=[
                    BulletPoint(text="First main point", level=0),
                    BulletPoint(text="Supporting detail for first point", level=1),
                    BulletPoint(text="Second main point", level=0),
                    BulletPoint(text="Third main point with details", level=0),
                    BulletPoint(text="Detail for third point", level=1),
                ]
            )
        )
        slide_builder.build_slide(content_slide)
        print(f"   [OK] Content slide {i} created")

    print()

    # Save presentation
    print("5. Saving presentation...")
    output_dir = "./test_output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "test_presentation.pptx")

    saved_path = template_manager.save_presentation(output_path)
    print(f"   [OK] Presentation saved to: {saved_path}")
    print()

    print("="*60)
    print("[SUCCESS] Test completed successfully!")
    print("="*60)
    print()
    print("Please open the generated file to verify:")
    print(f"  {saved_path}")
    print()
    print("Expected structure:")
    print("  - Title slide: Full-screen primary color with centered title")
    print("  - Content slides: Header (blue) + Body (white) + Footer (gray)")
    print("  - Footer shows: Slide X | Month Year")


if __name__ == '__main__':
    try:
        test_presentation_generation()
    except Exception as e:
        print(f"\n[FAILED] Test failed with error:")
        print(f"  {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
