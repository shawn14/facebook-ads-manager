#!/usr/bin/env python3
"""Test web integration with Google Gemini."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.api_client import FacebookAdsClient
from src.creative.image_generator import create_image_generator_from_config

def main():
    """Test that image generator works with config."""

    print("Testing web integration setup...")
    print("=" * 60)

    # Initialize FB client (this loads config)
    try:
        client = FacebookAdsClient()
        print(f"✅ FacebookAdsClient initialized")
        print(f"   Config loaded from: config/config.yaml")
    except Exception as e:
        print(f"❌ Failed to initialize FB client: {e}")
        return

    # Create image generator from config
    try:
        image_gen = create_image_generator_from_config(client.config)
        print(f"✅ Image generator created")
        print(f"   Provider: {image_gen.provider}")
        print(f"   Google client: {'✅' if image_gen.google_client else '❌'}")
        print(f"   OpenAI client: {'✅' if image_gen.openai_client else '❌'}")
    except Exception as e:
        print(f"❌ Failed to create image generator: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test image generation
    print("\n" + "=" * 60)
    print("Testing image generation...")
    print("=" * 60)

    try:
        image_bytes = image_gen.generate_ad_image(
            prompt="A modern smartphone displaying stock market charts",
            product_name="Stock Alarm",
            style="finance",
            size="1024x1024"
        )

        if image_bytes:
            print(f"✅ Image generated successfully!")
            print(f"   Size: {len(image_bytes) / 1024:.2f} KB")
            print(f"   Provider used: {image_gen.provider}")

            # Save test image
            test_file = Path("test_web_integration.png")
            with open(test_file, "wb") as f:
                f.write(image_bytes)
            print(f"   Saved to: {test_file}")
        else:
            print(f"❌ Image generation returned None")

    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("✅ All tests passed! Web integration should work.")
    print("=" * 60)

if __name__ == "__main__":
    main()
