#!/usr/bin/env python3
"""Test script for Google Imagen 3 integration."""

import os
import yaml
from pathlib import Path
from src.creative.image_generator import AIImageGenerator, create_image_generator_from_config
from loguru import logger

def main():
    """Test Google Imagen image generation."""

    # Load config
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        logger.error("Config file not found. Copy config.example.yaml to config.yaml")
        return

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Create generator using config
    generator = create_image_generator_from_config(config)

    logger.info(f"Using provider: {generator.provider}")

    # Test 1: Generate a simple ad image
    logger.info("=" * 60)
    logger.info("Test 1: Generating stock market ad image")
    logger.info("=" * 60)

    image_bytes = generator.generate_ad_image(
        prompt="A modern smartphone displaying real-time stock market alerts and trading notifications",
        product_name="Stock Alarm",
        style="finance",
        size="1024x1024"
    )

    if image_bytes:
        # Save the image
        output_path = Path("test_outputs")
        output_path.mkdir(exist_ok=True)

        image_file = output_path / "test_google_imagen.png"
        with open(image_file, "wb") as f:
            f.write(image_bytes)

        logger.info(f"✅ Image saved to: {image_file}")
        logger.info(f"Size: {len(image_bytes) / 1024:.2f} KB")
    else:
        logger.error("❌ Failed to generate image")

    # Test 2: Generate variations for A/B testing
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: Generating image variations")
    logger.info("=" * 60)

    variations = generator.generate_variations(
        base_prompt="Professional trader using a smartphone for stock market analysis",
        count=3,
        product_name="Stock Alarm",
        style="modern"
    )

    logger.info(f"✅ Generated {len(variations)} variations")

    for i, var_bytes in enumerate(variations, 1):
        var_file = output_path / f"variation_{i}.png"
        with open(var_file, "wb") as f:
            f.write(var_bytes)
        logger.info(f"  - Variation {i} saved: {var_file}")

    # Test 3: Suggest prompt from ad copy
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: Auto-suggest image prompt")
    logger.info("=" * 60)

    suggested = generator.suggest_prompt(
        product_name="Stock Alarm",
        headline="Never Miss a Trading Alert",
        description="Real-time stock price notifications and trading alerts for day traders",
        industry="finance"
    )

    logger.info(f"Suggested prompt: {suggested}")

    logger.info("\n" + "=" * 60)
    logger.info("✅ All tests completed!")
    logger.info("=" * 60)
    logger.info(f"Check the test_outputs/ directory for generated images")

if __name__ == "__main__":
    main()
