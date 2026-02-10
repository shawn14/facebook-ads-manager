"""Creative templates and copy helpers for ads."""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AdCopyTemplate:
    """Template for ad copy."""
    headline: str
    primary_text: str
    description: Optional[str] = None
    call_to_action: str = "LEARN_MORE"


class CreativeTemplates:
    """Pre-built templates for common ad types."""

    @staticmethod
    def ecommerce_product(
        product_name: str,
        price: str,
        discount: Optional[str] = None
    ) -> AdCopyTemplate:
        """Template for e-commerce product ads.

        Args:
            product_name: Name of the product
            price: Product price
            discount: Optional discount percentage

        Returns:
            AdCopyTemplate object
        """
        if discount:
            headline = f"{product_name} - {discount} Off!"
            primary_text = f"Get {product_name} now for only {price}. Limited time offer - {discount} off!"
        else:
            headline = f"{product_name} - Only {price}"
            primary_text = f"Discover {product_name} at an amazing price. Shop now for {price}!"

        return AdCopyTemplate(
            headline=headline,
            primary_text=primary_text,
            description=f"High-quality {product_name} at unbeatable prices.",
            call_to_action="SHOP_NOW"
        )

    @staticmethod
    def lead_generation(
        offer: str,
        benefit: str
    ) -> AdCopyTemplate:
        """Template for lead generation ads.

        Args:
            offer: What you're offering (e.g., "Free Guide", "Free Consultation")
            benefit: Main benefit to the user

        Returns:
            AdCopyTemplate object
        """
        return AdCopyTemplate(
            headline=f"Get Your {offer}",
            primary_text=f"Discover {benefit}. Download our {offer} today and start seeing results!",
            description="Limited spots available. Sign up now!",
            call_to_action="SIGN_UP"
        )

    @staticmethod
    def event_promotion(
        event_name: str,
        date: str,
        location: str
    ) -> AdCopyTemplate:
        """Template for event promotion ads.

        Args:
            event_name: Name of the event
            date: Event date
            location: Event location

        Returns:
            AdCopyTemplate object
        """
        return AdCopyTemplate(
            headline=f"Join Us: {event_name}",
            primary_text=f"Don't miss {event_name}! {date} at {location}. Reserve your spot today!",
            description="Limited seats available. Register now!",
            call_to_action="BOOK_NOW"
        )

    @staticmethod
    def app_install(
        app_name: str,
        key_feature: str,
        rating: Optional[str] = None
    ) -> AdCopyTemplate:
        """Template for app installation ads.

        Args:
            app_name: Name of the app
            key_feature: Main feature or benefit
            rating: Optional app rating (e.g., "4.8 stars")

        Returns:
            AdCopyTemplate object
        """
        rating_text = f" Rated {rating}!" if rating else ""
        return AdCopyTemplate(
            headline=f"Download {app_name}",
            primary_text=f"Experience {key_feature} with {app_name}.{rating_text} Download now for free!",
            description=f"Join millions using {app_name}",
            call_to_action="DOWNLOAD"
        )

    @staticmethod
    def service_promotion(
        service_name: str,
        unique_value: str,
        urgency: Optional[str] = None
    ) -> AdCopyTemplate:
        """Template for service promotion ads.

        Args:
            service_name: Name of the service
            unique_value: What makes the service unique
            urgency: Optional urgency message (e.g., "Book this week")

        Returns:
            AdCopyTemplate object
        """
        urgency_text = f" {urgency}" if urgency else ""
        return AdCopyTemplate(
            headline=f"Professional {service_name}",
            primary_text=f"Get expert {service_name} with {unique_value}.{urgency_text}",
            description="Book your appointment today!",
            call_to_action="GET_QUOTE"
        )

    @staticmethod
    def webinar_registration(
        topic: str,
        speaker: str,
        date: str
    ) -> AdCopyTemplate:
        """Template for webinar registration ads.

        Args:
            topic: Webinar topic
            speaker: Speaker name or expertise
            date: Webinar date/time

        Returns:
            AdCopyTemplate object
        """
        return AdCopyTemplate(
            headline=f"Free Webinar: {topic}",
            primary_text=f"Join {speaker} for an exclusive webinar on {topic}. {date}. Reserve your seat now!",
            description="Limited spots available. Free registration!",
            call_to_action="SIGN_UP"
        )

    @staticmethod
    def limited_offer(
        offer_title: str,
        savings: str,
        deadline: str
    ) -> AdCopyTemplate:
        """Template for limited-time offer ads.

        Args:
            offer_title: Title of the offer
            savings: Amount or percentage saved
            deadline: When the offer expires

        Returns:
            AdCopyTemplate object
        """
        return AdCopyTemplate(
            headline=f"{offer_title} - Save {savings}",
            primary_text=f"Limited time only! {offer_title}. Save {savings}. Offer ends {deadline}.",
            description="Don't miss out on this exclusive deal!",
            call_to_action="SHOP_NOW"
        )


class CopyVariationGenerator:
    """Generate variations of ad copy for A/B testing."""

    @staticmethod
    def generate_headline_variations(
        base_headline: str,
        product_name: str
    ) -> List[str]:
        """Generate headline variations for testing.

        Args:
            base_headline: Original headline
            product_name: Product/service name

        Returns:
            List of headline variations
        """
        return [
            base_headline,
            f"Discover {product_name}",
            f"Why Choose {product_name}?",
            f"The Ultimate {product_name}",
            f"Transform Your Life with {product_name}",
            f"Introducing {product_name}",
            f"Get {product_name} Today",
            f"Experience {product_name}"
        ]

    @staticmethod
    def generate_cta_variations() -> List[str]:
        """Generate CTA variations for testing.

        Returns:
            List of CTA types
        """
        return [
            "LEARN_MORE",
            "SHOP_NOW",
            "SIGN_UP",
            "DOWNLOAD",
            "GET_QUOTE",
            "CONTACT_US",
            "APPLY_NOW",
            "BOOK_NOW"
        ]

    @staticmethod
    def add_urgency(
        text: str,
        urgency_type: str = "time"
    ) -> str:
        """Add urgency to ad copy.

        Args:
            text: Original text
            urgency_type: Type of urgency (time, scarcity, demand)

        Returns:
            Text with urgency added
        """
        urgency_phrases = {
            "time": [
                "Limited time offer!",
                "Act now!",
                "Offer ends soon!",
                "Today only!",
                "Don't wait!"
            ],
            "scarcity": [
                "Limited stock available!",
                "While supplies last!",
                "Almost sold out!",
                "Only a few left!",
                "Running low!"
            ],
            "demand": [
                "Join thousands of satisfied customers!",
                "Our most popular offer!",
                "Trending now!",
                "Everyone's buying this!",
                "Best seller!"
            ]
        }

        phrases = urgency_phrases.get(urgency_type, urgency_phrases["time"])
        import random
        urgency = random.choice(phrases)
        return f"{urgency} {text}"

    @staticmethod
    def add_social_proof(
        text: str,
        proof_type: str = "testimonial"
    ) -> str:
        """Add social proof to ad copy.

        Args:
            text: Original text
            proof_type: Type of social proof (testimonial, stats, ratings)

        Returns:
            Text with social proof added
        """
        social_proof = {
            "testimonial": [
                "Loved by thousands!",
                "5-star rated!",
                "Customers rave about us!",
                "See what people are saying!"
            ],
            "stats": [
                "Join 10,000+ happy customers!",
                "Trusted by over 50,000 users!",
                "Used by professionals worldwide!",
                "Growing community of 100,000+!"
            ],
            "ratings": [
                "Rated 4.9/5 stars!",
                "Top rated by customers!",
                "Award-winning service!",
                "Industry-leading ratings!"
            ]
        }

        proofs = social_proof.get(proof_type, social_proof["testimonial"])
        import random
        proof = random.choice(proofs)
        return f"{text} {proof}"


class CreativeBestPractices:
    """Best practices and guidelines for ad creatives."""

    # Recommended character limits
    HEADLINE_MAX_LENGTH = 40
    PRIMARY_TEXT_MAX_LENGTH = 125
    DESCRIPTION_MAX_LENGTH = 30
    LINK_CAPTION_MAX_LENGTH = 30

    # Image specifications (Facebook recommendations)
    IMAGE_RECOMMENDED_SIZE = (1200, 628)  # pixels
    IMAGE_MIN_SIZE = (600, 600)
    IMAGE_ASPECT_RATIO = 1.91  # width:height
    IMAGE_MAX_TEXT_PERCENTAGE = 20  # max % of image covered by text

    # Video specifications
    VIDEO_MIN_LENGTH = 1  # seconds
    VIDEO_MAX_LENGTH = 241  # seconds (4 minutes)
    VIDEO_RECOMMENDED_LENGTH = 15  # seconds for best engagement

    @staticmethod
    def validate_text_length(
        text: str,
        field_name: str,
        max_length: int
    ) -> bool:
        """Validate text length against recommendations.

        Args:
            text: Text to validate
            field_name: Name of the field
            max_length: Maximum recommended length

        Returns:
            True if valid, raises warning if too long
        """
        if len(text) > max_length:
            from loguru import logger
            logger.warning(
                f"{field_name} exceeds recommended length: "
                f"{len(text)} > {max_length} characters"
            )
            return False
        return True

    @staticmethod
    def optimize_headline(headline: str) -> str:
        """Optimize headline for better performance.

        Args:
            headline: Original headline

        Returns:
            Optimized headline
        """
        # Remove excess punctuation
        headline = headline.replace('!!!', '!').replace('...', '.')

        # Capitalize first letter of each word for impact
        if not headline.isupper():  # Don't change if already all caps
            headline = headline.title()

        # Truncate if too long
        if len(headline) > CreativeBestPractices.HEADLINE_MAX_LENGTH:
            headline = headline[:CreativeBestPractices.HEADLINE_MAX_LENGTH - 3] + '...'

        return headline

    @staticmethod
    def get_recommendations() -> Dict[str, str]:
        """Get creative best practice recommendations.

        Returns:
            Dictionary of recommendations
        """
        return {
            "headline": f"Keep under {CreativeBestPractices.HEADLINE_MAX_LENGTH} characters",
            "primary_text": f"Optimal length: {CreativeBestPractices.PRIMARY_TEXT_MAX_LENGTH} characters",
            "description": f"Keep under {CreativeBestPractices.DESCRIPTION_MAX_LENGTH} characters",
            "image_size": f"Recommended: {CreativeBestPractices.IMAGE_RECOMMENDED_SIZE[0]}x{CreativeBestPractices.IMAGE_RECOMMENDED_SIZE[1]}px",
            "image_text": f"Keep text under {CreativeBestPractices.IMAGE_MAX_TEXT_PERCENTAGE}% of image",
            "video_length": f"Optimal: {CreativeBestPractices.VIDEO_RECOMMENDED_LENGTH} seconds",
            "cta": "Use clear, action-oriented CTAs",
            "mobile": "Design mobile-first - most users view on mobile",
            "testing": "Always test multiple creative variations"
        }
