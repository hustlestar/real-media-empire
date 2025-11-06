"""
Quick test to verify PPTX generation imports work correctly.
"""

def test_imports():
    """Test that all PPTX modules can be imported."""
    print("Testing PPTX generation imports...")

    try:
        # Core models
        from pptx_gen.models import (
            PresentationRequest,
            PresentationConfig,
            SlideDefinition,
            PresentationResult,
            SlideLayout,
            ToneType,
            AspectRatio,
        )
        print("[OK] Models imported successfully")

        # Providers
        from pptx_gen.providers.base import BaseContentProvider
        from pptx_gen.providers.content_provider import OpenAIContentProvider
        print("[OK] Providers imported successfully")

        # Core components
        from pptx_gen.template_manager import TemplateManager
        from pptx_gen.slide_builder import SlideBuilder
        from pptx_gen.cost_tracker import CostTracker
        from pptx_gen.generator import PresentationGenerator
        print("[OK] Core components imported successfully")

        # Pipeline
        from pipelines.pptx_generation import pptx_generation_pipeline
        from pipelines.steps.pptx_steps import (
            create_presentation_request,
            generate_content,
        )
        print("[OK] Pipeline components imported successfully")

        print("\n[SUCCESS] All imports successful!")
        return True

    except ImportError as e:
        print(f"\n[FAILED] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    test_imports()
