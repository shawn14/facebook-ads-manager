"""AI-powered image generation for Facebook ads."""

import os
import io
import base64
from typing import Optional, Dict, Any, Literal
from pathlib import Path
import requests
from PIL import Image
from openai import OpenAI
from loguru import logger

try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Google Imagen support disabled.")


class AIImageGenerator:
    """Generate ad images using AI (DALL-E or Google Imagen)."""

    def __init__(
        self,
        provider: Literal["openai", "google"] = "google",
        openai_api_key: Optional[str] = None,
        google_api_key: Optional[str] = None
    ):
        """Initialize the AI image generator.

        Args:
            provider: AI provider to use ("openai" for DALL-E, "google" for Imagen)
            openai_api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            google_api_key: Google API key (or set GOOGLE_API_KEY env var)
        """
        self.provider = provider
        self.openai_client = None
        self.google_client = None

        # Initialize OpenAI if selected or as fallback
        if provider == "openai" or not GOOGLE_AI_AVAILABLE:
            openai_key = openai_api_key or os.getenv('OPENAI_API_KEY')
            if openai_key:
                self.openai_client = OpenAI(api_key=openai_key)
                logger.info("OpenAI DALL-E initialized")
            else:
                logger.warning("OpenAI API key not set.")

        # Initialize Google if selected
        if provider == "google" and GOOGLE_AI_AVAILABLE:
            google_key = google_api_key or os.getenv('GOOGLE_API_KEY')
            if google_key:
                genai.configure(api_key=google_key)
                self.google_client = genai.GenerativeModel('imagen-3.0-generate-001')
                logger.info("Google Imagen 3 initialized")
            else:
                logger.warning("Google API key not set. Falling back to OpenAI.")
                self.provider = "openai"

        # Validate we have at least one working client
        if not self.openai_client and not self.google_client:
            logger.error("No AI image generation API configured!")

    def _generate_with_google(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        negative_prompt: str = "low quality, blurry, distorted"
    ) -> Optional[bytes]:
        """Generate image using Google Gemini 2.5 Flash Image.

        Args:
            prompt: Description of the image to generate
            aspect_ratio: Aspect ratio (not used with current model)
            negative_prompt: What to avoid in the image (not used with current model)

        Returns:
            Image bytes (PNG format) or None if failed
        """
        try:
            logger.info(f"Generating image with Google Gemini: {prompt[:100]}...")

            # Use Gemini 2.5 Flash Image model (most reliable for now)
            model = genai.GenerativeModel('gemini-2.5-flash-image')

            # Generate image
            result = model.generate_content(prompt)

            # Extract image from response
            # Images are typically in the second part (index 1)
            if result and result.candidates:
                candidate = result.candidates[0]
                if candidate.content and candidate.content.parts:
                    # Check all parts for image data
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data.data:
                            image_bytes = part.inline_data.data
                            mime_type = part.inline_data.mime_type
                            logger.info(f"✅ Generated image with Google: {len(image_bytes)} bytes ({mime_type})")
                            return image_bytes

            logger.error("No image data found in response")
            return None

        except Exception as e:
            logger.error(f"Failed to generate image with Google: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None

    def _generate_with_openai(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Optional[bytes]:
        """Generate image using OpenAI DALL-E.

        Args:
            prompt: Description of the image to generate
            size: Image size (1024x1024, 1792x1024, 1024x1792)
            quality: Image quality (standard, hd)

        Returns:
            Image bytes or None if failed
        """
        if not self.openai_client:
            logger.error("OpenAI client not initialized")
            return None

        try:
            logger.info(f"Generating image with DALL-E: {prompt[:100]}...")

            # Generate image
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )

            # Download the generated image
            image_url = response.data[0].url
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()

            image_bytes = image_response.content
            logger.info(f"✅ Generated image with DALL-E: {len(image_bytes)} bytes")

            return image_bytes

        except Exception as e:
            logger.error(f"Failed to generate image with DALL-E: {e}")
            return None

    def generate_ad_image(
        self,
        prompt: str,
        product_name: str = "",
        style: str = "professional",
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Optional[bytes]:
        """Generate an ad image using configured AI provider.

        Args:
            prompt: Description of the image to generate
            product_name: Product/service name to include
            style: Visual style (professional, modern, minimalist, bold, tech, finance)
            size: Image size - for OpenAI: (1024x1024, 1792x1024, 1024x1792)
                              for Google: maps to aspect ratio (1:1, 16:9, 9:16)
            quality: Image quality (standard, hd) - OpenAI only

        Returns:
            Image bytes (PNG format) or None if failed

        Raises:
            ValueError: If no AI provider is configured
        """
        # Check if we have any working client
        if not self.google_client and not self.openai_client:
            error_msg = (
                "No AI image generation provider configured. "
                "Set either Google API key (GOOGLE_API_KEY) or OpenAI API key (OPENAI_API_KEY) "
                "in config.yaml or environment variables."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Build enhanced prompt
        style_prompts = {
            "professional": "professional, clean, corporate style",
            "modern": "modern, sleek, contemporary design",
            "minimalist": "minimalist, simple, elegant",
            "bold": "bold, vibrant, eye-catching colors",
            "tech": "high-tech, futuristic, digital",
            "finance": "financial, professional, trustworthy"
        }

        style_desc = style_prompts.get(style, "professional")

        full_prompt = f"{prompt}. {style_desc}. "
        if product_name:
            full_prompt += f"For {product_name}. "
        full_prompt += "Suitable for Facebook ad, high quality, no text overlay."

        # Generate based on provider
        if self.provider == "google" and self.google_client:
            # Map size to Google aspect ratio
            aspect_ratio_map = {
                "1024x1024": "1:1",
                "1792x1024": "16:9",
                "1024x1792": "9:16"
            }
            aspect_ratio = aspect_ratio_map.get(size, "1:1")

            result = self._generate_with_google(full_prompt, aspect_ratio)
            if result is None:
                raise ValueError("Google Gemini image generation failed")
            return result

        elif self.provider == "openai" and self.openai_client:
            result = self._generate_with_openai(full_prompt, size, quality)
            if result is None:
                raise ValueError("OpenAI DALL-E image generation failed")
            return result

        else:
            error_msg = f"Provider '{self.provider}' selected but not initialized"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def resize_for_facebook(
        self,
        image_bytes: bytes,
        format_type: str = "feed"
    ) -> bytes:
        """Resize image to Facebook ad specifications.

        Args:
            image_bytes: Original image bytes
            format_type: Ad format (feed, story, carousel)

        Returns:
            Resized image bytes
        """
        # Facebook recommended sizes
        sizes = {
            "feed": (1200, 628),      # 1.91:1 landscape
            "square": (1080, 1080),   # 1:1 square
            "story": (1080, 1920),    # 9:16 vertical
            "carousel": (1080, 1080)  # 1:1 square
        }

        target_size = sizes.get(format_type, (1200, 628))

        try:
            # Open image
            img = Image.open(io.BytesIO(image_bytes))

            # Resize maintaining aspect ratio
            img.thumbnail(target_size, Image.Resampling.LANCZOS)

            # Create new image with exact dimensions (add padding if needed)
            new_img = Image.new('RGB', target_size, (255, 255, 255))

            # Center the image
            x = (target_size[0] - img.size[0]) // 2
            y = (target_size[1] - img.size[1]) // 2
            new_img.paste(img, (x, y))

            # Convert to bytes
            output = io.BytesIO()
            new_img.save(output, format='JPEG', quality=95, optimize=True)
            output.seek(0)

            logger.info(f"✅ Resized image to {target_size}")
            return output.read()

        except Exception as e:
            logger.error(f"Failed to resize image: {e}")
            return image_bytes

    def generate_variations(
        self,
        base_prompt: str,
        count: int = 4,
        product_name: str = "",
        style: str = "professional"
    ) -> list[bytes]:
        """Generate multiple image variations for A/B testing.

        Args:
            base_prompt: Base description
            count: Number of variations (max 4)
            product_name: Product name
            style: Visual style

        Returns:
            List of image bytes
        """
        variations = []

        # Different prompt variations
        variation_prompts = [
            f"{base_prompt}, close-up view",
            f"{base_prompt}, wide angle view",
            f"{base_prompt}, lifestyle context",
            f"{base_prompt}, dramatic lighting"
        ]

        for i in range(min(count, 4)):
            prompt = variation_prompts[i] if i < len(variation_prompts) else base_prompt
            image = self.generate_ad_image(prompt, product_name, style)
            if image:
                variations.append(image)

        logger.info(f"✅ Generated {len(variations)} variations using {self.provider}")
        return variations

    def suggest_prompt(
        self,
        product_name: str,
        headline: str,
        description: str,
        industry: str = "tech"
    ) -> str:
        """Generate an image prompt based on ad copy.

        Args:
            product_name: Product/service name
            headline: Ad headline
            description: Ad description
            industry: Industry category

        Returns:
            Suggested AI image generation prompt
        """
        # Industry-specific prompts
        industry_styles = {
            "tech": "modern technology, digital interface, sleek design",
            "finance": "financial charts, professional business setting",
            "ecommerce": "product showcase, shopping, lifestyle",
            "saas": "software interface, dashboard, productivity",
            "health": "wellness, healthy lifestyle, medical",
            "education": "learning, students, knowledge"
        }

        style = industry_styles.get(industry, "professional business")

        # Extract key themes from headline/description
        prompt = f"A {style} image representing {product_name}. "

        # Add context from headline
        if "alert" in headline.lower() or "notification" in headline.lower():
            prompt += "Showing notifications, alerts, mobile phone. "
        if "trading" in description.lower() or "stock" in description.lower():
            prompt += "Stock market, trading, financial data. "
        if "price" in description.lower():
            prompt += "Price charts, market data. "

        return prompt


def create_image_generator_from_config(config: Dict[str, Any]) -> AIImageGenerator:
    """Create an image generator from configuration.

    Args:
        config: Configuration dictionary with ai_image, openai, and google sections

    Returns:
        Configured AIImageGenerator instance
    """
    provider = config.get('ai_image', {}).get('provider', 'google')
    openai_key = config.get('openai', {}).get('api_key')
    google_key = config.get('google', {}).get('api_key')

    logger.info(f"Creating image generator with provider: {provider}")

    return AIImageGenerator(
        provider=provider,
        openai_api_key=openai_key,
        google_api_key=google_key
    )
