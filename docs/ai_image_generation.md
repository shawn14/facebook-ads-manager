# AI Image Generation for Facebook Ads

This document explains how to use AI-powered image generation for creating Facebook ad creatives.

## Overview

The Facebook Ads Manager now supports AI-powered image generation using:
- **Google Gemini 2.5 Flash Image** (Recommended) - Fast, high-quality image generation
- **OpenAI DALL-E 3** - Alternative provider with different artistic style

## Quick Start

### 1. Configure API Keys

Edit `config/config.yaml`:

```yaml
ai_image:
  provider: "google"  # or "openai"

google:
  api_key: "YOUR_GOOGLE_API_KEY"  # Get from https://aistudio.google.com/app/apikey

openai:
  api_key: "YOUR_OPENAI_API_KEY"  # Get from https://platform.openai.com/api-keys
```

### 2. Basic Usage

```python
from src.creative.image_generator import create_image_generator_from_config
import yaml

# Load config
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

# Create generator
generator = create_image_generator_from_config(config)

# Generate an image
image_bytes = generator.generate_ad_image(
    prompt="A modern smartphone displaying real-time stock market alerts",
    product_name="Stock Alarm",
    style="finance",  # professional, modern, minimalist, bold, tech, finance
    size="1024x1024"  # 1024x1024 (square), 1792x1024 (landscape), 1024x1792 (portrait)
)

# Save the image
if image_bytes:
    with open("ad_image.png", "wb") as f:
        f.write(image_bytes)
```

### 3. Generate Multiple Variations for A/B Testing

```python
# Generate 3-4 variations of an image
variations = generator.generate_variations(
    base_prompt="Professional trader analyzing stock charts on mobile",
    count=3,
    product_name="Stock Alarm",
    style="modern"
)

# Save variations
for i, img_bytes in enumerate(variations, 1):
    with open(f"variation_{i}.png", "wb") as f:
        f.write(img_bytes)
```

### 4. Auto-Suggest Prompts

```python
# Generate image prompt from ad copy
suggested_prompt = generator.suggest_prompt(
    product_name="Stock Alarm",
    headline="Never Miss a Trading Alert",
    description="Real-time stock price notifications for day traders",
    industry="finance"  # tech, finance, ecommerce, saas, health, education
)

print(suggested_prompt)
# Output: "A financial charts, professional business setting image
#          representing Stock Alarm. Showing notifications, alerts,
#          mobile phone. Stock market, trading, financial data..."
```

## Image Styles

Available styles:
- **professional** - Clean, corporate, suitable for B2B
- **modern** - Sleek, contemporary design
- **minimalist** - Simple, elegant, less is more
- **bold** - Vibrant, eye-catching colors
- **tech** - High-tech, futuristic, digital
- **finance** - Financial charts, professional business setting

## Image Sizes

### For Google Gemini
- `1024x1024` → 1:1 square (best for carousel ads)
- `1792x1024` → 16:9 landscape (best for feed ads)
- `1024x1792` → 9:16 portrait (best for stories)

### For OpenAI DALL-E 3
- `1024x1024` - Square format
- `1792x1024` - Landscape format
- `1024x1792` - Portrait format

## Facebook Ad Specifications

The generator automatically optimizes images for Facebook ad formats:

| Format | Recommended Size | Aspect Ratio | Use Case |
|--------|-----------------|--------------|----------|
| Feed | 1200x628 | 1.91:1 | News feed ads |
| Square | 1080x1080 | 1:1 | Instagram, carousel |
| Story | 1080x1920 | 9:16 | Stories, Reels |
| Carousel | 1080x1080 | 1:1 | Multi-image ads |

Use `resize_for_facebook()` to resize generated images:

```python
# Generate image
image_bytes = generator.generate_ad_image(...)

# Resize for feed ads
resized = generator.resize_for_facebook(image_bytes, format_type="feed")
```

## Complete Ad Creation Workflow

```python
from src.api_client import FacebookAdsClient
from src.creative.manager import CreativeManager
from src.creative.image_generator import create_image_generator_from_config
import yaml

# 1. Load config
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

# 2. Initialize clients
fb_client = FacebookAdsClient()
creative_mgr = CreativeManager(fb_client)
img_gen = create_image_generator_from_config(config)

# 3. Generate AI image
image_bytes = img_gen.generate_ad_image(
    prompt="Modern trading app interface showing real-time alerts",
    product_name="Stock Alarm",
    style="finance"
)

# 4. Save image temporarily
with open("temp_ad_image.png", "wb") as f:
    f.write(image_bytes)

# 5. Create Facebook ad with the image
creative, ad = creative_mgr.create_complete_ad(
    adset_id="YOUR_ADSET_ID",
    ad_name="Stock Alert Ad - AI Generated",
    creative_name="Stock Alert Creative",
    creative_type=CreativeType.IMAGE,
    message="Never miss important stock price movements",
    link="https://yourapp.com",
    asset_path="temp_ad_image.png",
    call_to_action=CallToActionType.DOWNLOAD
)

print(f"✅ Ad created: {ad['id']}")
```

## Providers Comparison

| Feature | Google Gemini | OpenAI DALL-E 3 |
|---------|---------------|-----------------|
| Speed | ~6 seconds | ~8-10 seconds |
| Cost | Lower | Higher |
| Style | Photorealistic | Artistic variations |
| API Calls/min | Higher limits | Stricter limits |
| Max Resolution | 1024x1024 | 1792x1024 |

## Best Practices

1. **Be Specific**: Provide detailed prompts for better results
   - ❌ Bad: "trading app"
   - ✅ Good: "modern smartphone displaying real-time stock charts with green and red candlesticks, professional trading desk background"

2. **Include Style Keywords**: Add visual style descriptors
   - "professional", "modern", "clean interface", "high quality"

3. **Avoid Text in Images**: Facebook has text overlay limits
   - Always add "no text overlay" to prompts

4. **Generate Variations**: Create 3-4 variations for A/B testing
   - Test which visual style performs best

5. **Match Brand**: Ensure images align with your brand aesthetic
   - Use consistent colors and styles across campaigns

6. **Follow Facebook Guidelines**:
   - Avoid misleading imagery
   - Don't use before/after comparisons (health/fitness)
   - No shocking or sensational content

## Troubleshooting

### Issue: "No image data in response"
- Check API key is valid
- Ensure you have API credits/quota
- Try switching providers (google ↔ openai)

### Issue: "API rate limit exceeded"
- Reduce generation frequency
- Wait before retrying
- Consider upgrading API plan

### Issue: Poor image quality
- Make prompts more specific
- Try different styles
- Use quality="hd" for DALL-E (costs more)

### Issue: Images don't match prompt
- Rephrase prompt to be more explicit
- Add negative prompts (what to avoid)
- Try generating multiple variations

## Cost Optimization

1. **Use Google Gemini** - Generally more cost-effective than DALL-E
2. **Generate in batches** - Avoid regenerating similar images
3. **Cache results** - Save successful generations for reuse
4. **Use variations** - Generate variations instead of new images

## Examples

### Example 1: E-commerce Product
```python
image = generator.generate_ad_image(
    prompt="A premium leather laptop bag on a wooden desk, "
           "professional office setting, natural lighting",
    product_name="Executive Laptop Bag",
    style="professional",
    size="1024x1024"
)
```

### Example 2: SaaS Dashboard
```python
image = generator.generate_ad_image(
    prompt="Modern analytics dashboard showing colorful charts and graphs, "
           "clean interface, laptop screen, professional workspace",
    product_name="DataViz Pro",
    style="tech",
    size="1792x1024"
)
```

### Example 3: Financial App
```python
image = generator.generate_ad_image(
    prompt="Smartphone displaying stock market trading interface with "
           "real-time price alerts, candlestick charts, modern UI",
    product_name="Stock Alarm",
    style="finance",
    size="1024x1792"
)
```

## Next Steps

- Test both providers to find which style fits your brand
- Experiment with different prompts and styles
- Use A/B testing to optimize image performance
- Monitor Facebook ad performance metrics (CTR, conversions)
- Iterate based on what resonates with your audience
