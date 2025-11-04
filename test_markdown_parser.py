"""Test markdown parsing functionality"""

import sys
sys.path.insert(0, 'src')

from pptx_gen.slide_builder import SlideBuilder
from pptx_gen.models import PresentationConfig
from pptx_gen.template_manager import TemplateManager

# Create minimal setup
config = PresentationConfig()
tm = TemplateManager(config)
tm.presentation = tm.create_default_template()
builder = SlideBuilder(tm, config)

# Test cases
test_cases = [
    "Plain text without formatting",
    "Text with **bold** word",
    "Text with *italic* word",
    "Mix of **bold** and *italic* text",
    "Multiple **bold** and **more bold** in one line",
    "**Bold at start** and end **bold**",
    "*Italic at start* and end *italic*",
    "**Bold with *nested italic* inside**",
    "Text with **unclosed bold",
    "Text with *unclosed italic",
    "**",
    "*",
    "",
]

print("Testing Markdown Parser\n" + "="*60)
for test in test_cases:
    print(f"\nInput:  '{test}'")
    result = builder._parse_formatted_text(test)
    print(f"Output: {result}")
    # Reconstruct text to verify
    reconstructed = "".join(seg[0] for seg in result)
    # Remove markdown markers from original for comparison
    clean_original = test.replace("**", "").replace("*", "")
    if reconstructed == clean_original:
        print("[PASS]")
    else:
        print(f"[FAIL] - Expected: '{clean_original}', Got: '{reconstructed}'")

print("\n" + "="*60)
print("Test complete!")
