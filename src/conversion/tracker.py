"""
Facebook Conversions API Tracker

Server-side conversion tracking using Facebook's Conversions API.
More reliable than browser pixels and can't be blocked by ad blockers.
"""

import hashlib
import time
from typing import Optional, Dict, Any, List
from loguru import logger

try:
    from facebook_business.adobjects.serverside.event import Event
    from facebook_business.adobjects.serverside.event_request import EventRequest
    from facebook_business.adobjects.serverside.user_data import UserData
    from facebook_business.adobjects.serverside.custom_data import CustomData
    from facebook_business.adobjects.serverside.action_source import ActionSource
except ImportError:
    logger.warning("Facebook Business SDK server-side modules not available. Install facebook-business>=19.0.0")
    Event = None
    EventRequest = None
    UserData = None
    CustomData = None
    ActionSource = None


class ConversionTracker:
    """
    Server-side conversion tracking using Facebook Conversions API.

    Sends conversion events directly from your server to Facebook,
    bypassing browser-based pixels for more reliable tracking.
    """

    # Standard Facebook event types
    STANDARD_EVENTS = {
        'PageView': 'User viewed a page',
        'ViewContent': 'User viewed content (product, article, etc.)',
        'Search': 'User performed a search',
        'AddToCart': 'User added item to cart',
        'AddToWishlist': 'User added item to wishlist',
        'InitiateCheckout': 'User started checkout process',
        'AddPaymentInfo': 'User added payment information',
        'Purchase': 'User completed a purchase',
        'Lead': 'User submitted a lead form',
        'CompleteRegistration': 'User completed registration/signup',
        'Contact': 'User contacted your business',
        'CustomizeProduct': 'User customized a product',
        'Donate': 'User made a donation',
        'FindLocation': 'User searched for a location',
        'Schedule': 'User scheduled an appointment',
        'StartTrial': 'User started a free trial',
        'SubmitApplication': 'User submitted an application',
        'Subscribe': 'User subscribed to a service',
    }

    def __init__(self, access_token: str, pixel_id: str):
        """
        Initialize the Conversion Tracker.

        Args:
            access_token: Facebook API access token
            pixel_id: Facebook Pixel ID (from Events Manager)
        """
        if not Event or not EventRequest:
            raise ImportError(
                "Facebook Business SDK server-side modules not available. "
                "Upgrade facebook-business: pip install --upgrade facebook-business"
            )

        self.access_token = access_token
        self.pixel_id = pixel_id
        logger.info(f"Initialized ConversionTracker with pixel_id: {pixel_id}")

    @staticmethod
    def hash_data(data: str) -> str:
        """
        Hash user data using SHA-256 for privacy.

        Facebook requires hashed user data for privacy compliance.

        Args:
            data: Raw data (email, phone, etc.)

        Returns:
            SHA-256 hashed string
        """
        if not data:
            return None
        return hashlib.sha256(data.lower().strip().encode()).hexdigest()

    def track_event(
        self,
        event_name: str,
        event_source_url: Optional[str] = None,
        user_email: Optional[str] = None,
        user_phone: Optional[str] = None,
        user_first_name: Optional[str] = None,
        user_last_name: Optional[str] = None,
        user_city: Optional[str] = None,
        user_state: Optional[str] = None,
        user_zip: Optional[str] = None,
        user_country: Optional[str] = None,
        user_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        fbp: Optional[str] = None,  # Facebook browser ID
        fbc: Optional[str] = None,  # Facebook click ID
        value: Optional[float] = None,
        currency: str = "USD",
        content_name: Optional[str] = None,
        content_category: Optional[str] = None,
        content_ids: Optional[List[str]] = None,
        num_items: Optional[int] = None,
        custom_data: Optional[Dict[str, Any]] = None,
        test_event_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Track a conversion event.

        Args:
            event_name: Event type (e.g., 'Purchase', 'Lead', 'CompleteRegistration')
            event_source_url: URL where event occurred
            user_email: User's email (will be hashed)
            user_phone: User's phone (will be hashed)
            user_first_name: User's first name (will be hashed)
            user_last_name: User's last name (will be hashed)
            user_city: User's city (will be hashed)
            user_state: User's state (will be hashed)
            user_zip: User's zip code (will be hashed)
            user_country: User's country code (will be hashed)
            user_ip: User's IP address
            user_agent: User's browser user agent
            fbp: Facebook browser pixel ID (_fbp cookie)
            fbc: Facebook click ID (_fbc cookie)
            value: Transaction value (for Purchase events)
            currency: Currency code (default: USD)
            content_name: Product/content name
            content_category: Product/content category
            content_ids: List of product IDs
            num_items: Number of items
            custom_data: Additional custom data
            test_event_code: Test event code from Facebook (for testing)

        Returns:
            Response from Facebook API
        """
        try:
            # Build user data with hashed PII
            user_data = UserData()

            if user_email:
                user_data.email = self.hash_data(user_email)
            if user_phone:
                user_data.phone = self.hash_data(user_phone)
            if user_first_name:
                user_data.first_name = self.hash_data(user_first_name)
            if user_last_name:
                user_data.last_name = self.hash_data(user_last_name)
            if user_city:
                user_data.city = self.hash_data(user_city)
            if user_state:
                user_data.state = self.hash_data(user_state)
            if user_zip:
                user_data.zip_code = self.hash_data(user_zip)
            if user_country:
                user_data.country_code = self.hash_data(user_country)
            if user_ip:
                user_data.client_ip_address = user_ip
            if user_agent:
                user_data.client_user_agent = user_agent
            if fbp:
                user_data.fbp = fbp
            if fbc:
                user_data.fbc = fbc

            # Build custom data for purchase/transaction info
            custom = CustomData()
            if value is not None:
                custom.value = value
            if currency:
                custom.currency = currency
            if content_name:
                custom.content_name = content_name
            if content_category:
                custom.content_category = content_category
            if content_ids:
                custom.content_ids = content_ids
            if num_items is not None:
                custom.num_items = num_items
            if custom_data:
                custom.custom_properties = custom_data

            # Create event
            event = Event(
                event_name=event_name,
                event_time=int(time.time()),
                user_data=user_data,
                custom_data=custom,
                action_source=ActionSource.WEBSITE,
            )

            if event_source_url:
                event.event_source_url = event_source_url

            # Create event request
            event_request = EventRequest(
                events=[event],
                pixel_id=self.pixel_id,
            )

            # Add test event code if provided
            if test_event_code:
                event_request.test_event_code = test_event_code

            # Send to Facebook
            response = event_request.execute()

            logger.info(f"Sent {event_name} event to Facebook Conversions API")
            logger.debug(f"Response: {response}")

            return {
                "success": True,
                "event_name": event_name,
                "pixel_id": self.pixel_id,
                "response": response,
            }

        except Exception as e:
            logger.error(f"Failed to track {event_name} event: {e}")
            return {
                "success": False,
                "event_name": event_name,
                "error": str(e),
            }

    def track_page_view(self, url: str, user_email: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Track a page view event."""
        return self.track_event(
            event_name="PageView",
            event_source_url=url,
            user_email=user_email,
            **kwargs
        )

    def track_purchase(
        self,
        value: float,
        currency: str = "USD",
        user_email: Optional[str] = None,
        content_ids: Optional[List[str]] = None,
        num_items: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Track a purchase/transaction event."""
        return self.track_event(
            event_name="Purchase",
            value=value,
            currency=currency,
            user_email=user_email,
            content_ids=content_ids,
            num_items=num_items,
            **kwargs
        )

    def track_lead(
        self,
        user_email: str,
        content_name: Optional[str] = None,
        value: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Track a lead generation event."""
        return self.track_event(
            event_name="Lead",
            user_email=user_email,
            content_name=content_name,
            value=value,
            **kwargs
        )

    def track_registration(
        self,
        user_email: str,
        user_first_name: Optional[str] = None,
        user_last_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Track a user registration/signup event."""
        return self.track_event(
            event_name="CompleteRegistration",
            user_email=user_email,
            user_first_name=user_first_name,
            user_last_name=user_last_name,
            **kwargs
        )

    def track_subscription(
        self,
        value: float,
        currency: str = "USD",
        user_email: Optional[str] = None,
        content_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Track a subscription event."""
        return self.track_event(
            event_name="Subscribe",
            value=value,
            currency=currency,
            user_email=user_email,
            content_name=content_name,
            **kwargs
        )

    def get_standard_events(self) -> Dict[str, str]:
        """Get list of standard Facebook event types."""
        return self.STANDARD_EVENTS.copy()
