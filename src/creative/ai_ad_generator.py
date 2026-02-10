"""AI-powered ad copy and creative generator."""

import os
from typing import Optional, Dict, Any, List
from openai import OpenAI
from loguru import logger


class AIAdGenerator:
    """Generate complete ads using AI (GPT-4 + DALL-E)."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI ad generator.

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            logger.warning("OpenAI API key not set. AI ad generation disabled.")
            self.client = None

    def generate_ad_copy(
        self,
        prompt: str,
        product_name: str = "",
        target_audience: str = "",
        goal: str = "conversions",
        tone: str = "professional",
        num_variations: int = 3
    ) -> List[Dict[str, str]]:
        """Generate ad copy (headline + description) using AI.

        Args:
            prompt: What the ad should be about (e.g., "promote free trial")
            product_name: Product/service name
            target_audience: Who the ad is for (e.g., "day traders", "investors")
            goal: Ad goal (conversions, awareness, traffic, engagement)
            tone: Writing tone (professional, casual, urgent, friendly)
            num_variations: Number of variations to generate (1-5)

        Returns:
            List of ad variations with headline and description
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return []

        try:
            system_prompt = f"""You are an expert Facebook ads copywriter specializing in {tone} advertising.

Generate {num_variations} Facebook ad variations that:
- Have compelling headlines (max 40 characters)
- Have engaging descriptions/primary text (max 125 characters)
- Are optimized for {goal}
- Target: {target_audience or 'general audience'}
- Follow Facebook ad best practices
- Are clear, concise, and action-oriented

Return ONLY valid JSON array format:
[
  {{"headline": "...", "description": "...", "call_to_action": "LEARN_MORE"}},
  ...
]

Use appropriate CTAs: LEARN_MORE, SHOP_NOW, SIGN_UP, DOWNLOAD, GET_QUOTE, CONTACT_US, APPLY_NOW, SUBSCRIBE, BOOK_NOW, WATCH_MORE
"""

            user_prompt = f"""Create Facebook ad copy for: {product_name or 'our product'}

What the ad should communicate: {prompt}

Target audience: {target_audience or 'general audience'}
Goal: {goal}
Tone: {tone}

Requirements:
- Headline: Max 40 characters, attention-grabbing
- Description: Max 125 characters, clear value proposition
- Include benefit, urgency, or social proof where appropriate
- Match the {tone} tone"""

            logger.info(f"Generating {num_variations} ad variations for: {prompt}")

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,  # More creative
                max_tokens=800
            )

            import json
            content = response.choices[0].message.content.strip()

            # Try to parse JSON
            try:
                variations = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code block
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                variations = json.loads(content)

            # Valid Facebook CTAs
            valid_ctas = {
                'LEARN_MORE', 'SHOP_NOW', 'SIGN_UP', 'DOWNLOAD', 'GET_QUOTE',
                'CONTACT_US', 'APPLY_NOW', 'SUBSCRIBE', 'BOOK_NOW', 'WATCH_MORE',
                'GET_OFFER', 'BUY_NOW', 'INSTALL_APP', 'USE_APP', 'WATCH_VIDEO'
            }

            # CTA mappings for common variations
            cta_mappings = {
                'DOWNLOAD_NOW': 'DOWNLOAD',
                'SHOP': 'SHOP_NOW',
                'BUY': 'BUY_NOW',
                'INSTALL': 'INSTALL_APP',
                'SIGNUP': 'SIGN_UP',
                'GET_STARTED': 'LEARN_MORE',
                'TRY_NOW': 'LEARN_MORE'
            }

            # Validate character limits and CTAs
            validated_variations = []
            for var in variations[:num_variations]:
                headline = var.get('headline', '')[:40]  # Enforce limit
                description = var.get('description', '')[:125]  # Enforce limit
                cta = var.get('call_to_action', 'LEARN_MORE').upper()

                # Map to valid CTA
                if cta not in valid_ctas:
                    cta = cta_mappings.get(cta, 'LEARN_MORE')

                validated_variations.append({
                    'headline': headline,
                    'description': description,
                    'call_to_action': cta
                })

            logger.info(f"✅ Generated {len(validated_variations)} ad variations")
            return validated_variations

        except Exception as e:
            logger.error(f"Failed to generate ad copy: {e}")
            return []

    def generate_complete_ad_plan(
        self,
        user_input: str,
        product_name: str = "",
        industry: str = "tech"
    ) -> Dict[str, Any]:
        """Generate a complete ad plan from natural language input.

        Args:
            user_input: User's description (e.g., "I want to promote our free trial to day traders")
            product_name: Product/service name
            industry: Industry category

        Returns:
            Complete ad plan with copy, image prompt, targeting suggestions
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return {}

        try:
            system_prompt = """You are an expert Facebook ads strategist.
Given a user's request, create a complete ad strategy including:
1. Ad copy (headline and description)
2. Image prompt for DALL-E
3. Target audience suggestions
4. Recommended CTA

Return valid JSON format:
{
  "headline": "max 40 chars",
  "description": "max 125 chars",
  "image_prompt": "detailed prompt for DALL-E image generation",
  "target_audience": "description of ideal audience",
  "call_to_action": "LEARN_MORE/SHOP_NOW/etc",
  "ad_format": "feed/square/story",
  "image_style": "professional/modern/finance/tech/bold"
}
"""

            user_prompt = f"""Create a complete Facebook ad plan for:

Product: {product_name}
Industry: {industry}
User wants: {user_input}

Make it specific and actionable."""

            logger.info(f"Generating complete ad plan: {user_input}")

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )

            import json
            content = response.choices[0].message.content.strip()

            # Parse JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            plan = json.loads(content)

            # Enforce character limits
            plan['headline'] = plan.get('headline', '')[:40]
            plan['description'] = plan.get('description', '')[:125]

            # Validate CTA
            valid_ctas = {
                'LEARN_MORE', 'SHOP_NOW', 'SIGN_UP', 'DOWNLOAD', 'GET_QUOTE',
                'CONTACT_US', 'APPLY_NOW', 'SUBSCRIBE', 'BOOK_NOW', 'WATCH_MORE',
                'GET_OFFER', 'BUY_NOW', 'INSTALL_APP', 'USE_APP', 'WATCH_VIDEO'
            }
            cta_mappings = {
                'DOWNLOAD_NOW': 'DOWNLOAD',
                'SHOP': 'SHOP_NOW',
                'BUY': 'BUY_NOW',
                'INSTALL': 'INSTALL_APP',
                'SIGNUP': 'SIGN_UP',
                'GET_STARTED': 'LEARN_MORE',
                'TRY_NOW': 'LEARN_MORE'
            }

            cta = plan.get('call_to_action', 'LEARN_MORE').upper()
            if cta not in valid_ctas:
                cta = cta_mappings.get(cta, 'LEARN_MORE')
            plan['call_to_action'] = cta

            logger.info(f"✅ Generated complete ad plan")
            return plan

        except Exception as e:
            logger.error(f"Failed to generate ad plan: {e}")
            return {}

    def improve_ad_copy(
        self,
        current_headline: str,
        current_description: str,
        feedback: str = "make it more compelling"
    ) -> Dict[str, str]:
        """Improve existing ad copy based on feedback.

        Args:
            current_headline: Current headline
            current_description: Current description
            feedback: What to improve (e.g., "make it more urgent", "add social proof")

        Returns:
            Improved headline and description
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return {"headline": current_headline, "description": current_description}

        try:
            prompt = f"""Improve this Facebook ad copy based on the feedback:

Current headline: "{current_headline}"
Current description: "{current_description}"

Feedback: {feedback}

Requirements:
- Headline: Max 40 characters
- Description: Max 125 characters
- Keep it compelling and clear
- Maintain Facebook ad best practices

Return JSON:
{{"headline": "...", "description": "..."}}
"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )

            import json
            content = response.choices[0].message.content.strip()
            if "```" in content:
                content = content.split("```")[1].split("```")[0].replace("json", "").strip()

            improved = json.loads(content)
            improved['headline'] = improved.get('headline', current_headline)[:40]
            improved['description'] = improved.get('description', current_description)[:125]

            logger.info("✅ Improved ad copy")
            return improved

        except Exception as e:
            logger.error(f"Failed to improve ad copy: {e}")
            return {"headline": current_headline, "description": current_description}
