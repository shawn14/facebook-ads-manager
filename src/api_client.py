"""Facebook Marketing API client wrapper."""

from typing import Dict, List, Optional, Any
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.advideo import AdVideo
from facebook_business.adobjects.adspixel import AdsPixel
from loguru import logger
import yaml
from pathlib import Path


class FacebookAdsClient:
    """Wrapper for Facebook Marketing API with convenience methods."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the Facebook Ads API client.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self._init_api()
        self.ad_account = AdAccount(self.config['facebook']['ad_account_id'])

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_path}\n"
                "Copy config.example.yaml to config.yaml and fill in your credentials"
            )

        with open(path) as f:
            return yaml.safe_load(f)

    def _init_api(self):
        """Initialize Facebook Ads API."""
        fb_config = self.config['facebook']
        FacebookAdsApi.init(
            app_id=fb_config['app_id'],
            app_secret=fb_config['app_secret'],
            access_token=fb_config['access_token'],
            api_version=fb_config.get('api_version', 'v19.0')
        )
        logger.info("Facebook Ads API initialized")

    # Campaign Management

    def create_campaign(
        self,
        name: str,
        objective: str,
        status: str = "PAUSED",
        special_ad_categories: Optional[List[str]] = None
    ) -> Campaign:
        """Create a new ad campaign.

        Args:
            name: Campaign name
            objective: Campaign objective (LINK_CLICKS, CONVERSIONS, etc.)
            status: Campaign status (ACTIVE, PAUSED)
            special_ad_categories: Special ad categories if applicable

        Returns:
            Created campaign object
        """
        params = {
            'name': name,
            'objective': objective,
            'status': status,
            'special_ad_categories': special_ad_categories if special_ad_categories is not None else []
        }

        campaign = self.ad_account.create_campaign(params=params)
        logger.info(f"Created campaign: {name} (ID: {campaign['id']})")
        return campaign

    def get_campaigns(
        self,
        fields: Optional[List[str]] = None,
        filtering: Optional[List[Dict]] = None
    ) -> List[Campaign]:
        """Get campaigns for the ad account.

        Args:
            fields: Fields to retrieve
            filtering: Filter conditions

        Returns:
            List of campaigns
        """
        if fields is None:
            fields = [
                'id', 'name', 'objective', 'status',
                'daily_budget', 'lifetime_budget',
                'created_time', 'updated_time'
            ]

        params = {'fields': fields}
        if filtering:
            params['filtering'] = filtering

        campaigns = self.ad_account.get_campaigns(params=params)
        return list(campaigns)

    def update_campaign(
        self,
        campaign_id: str,
        updates: Dict[str, Any]
    ) -> Campaign:
        """Update a campaign.

        Args:
            campaign_id: Campaign ID
            updates: Dictionary of fields to update

        Returns:
            Updated campaign object
        """
        campaign = Campaign(campaign_id)
        campaign.api_update(params=updates)
        logger.info(f"Updated campaign {campaign_id}: {updates}")
        return campaign

    def pause_campaign(self, campaign_id: str) -> Campaign:
        """Pause a campaign."""
        return self.update_campaign(campaign_id, {'status': 'PAUSED'})

    def activate_campaign(self, campaign_id: str) -> Campaign:
        """Activate a campaign."""
        return self.update_campaign(campaign_id, {'status': 'ACTIVE'})

    def delete_campaign(self, campaign_id: str):
        """Delete a campaign."""
        campaign = Campaign(campaign_id)
        campaign.api_delete()
        logger.info(f"Deleted campaign {campaign_id}")

    # Ad Set Management

    def create_adset(
        self,
        campaign_id: str,
        name: str,
        daily_budget: int,
        targeting: Dict,
        optimization_goal: str = "LINK_CLICKS",
        billing_event: str = "IMPRESSIONS",
        bid_strategy: str = "LOWEST_COST_WITHOUT_CAP",
        bid_amount: Optional[int] = None,
        status: str = "PAUSED",
        promoted_object: Optional[Dict] = None
    ) -> AdSet:
        """Create a new ad set.

        Args:
            campaign_id: Parent campaign ID
            name: Ad set name
            daily_budget: Daily budget in cents
            targeting: Targeting specification
            optimization_goal: Optimization goal
            billing_event: Billing event
            bid_strategy: Bid strategy
            bid_amount: Max bid in cents (required for LOWEST_COST_WITH_BID_CAP)
            status: Ad set status
            promoted_object: Promoted object (for app installs, page likes, etc.)
                            Example: {'application_id': '123', 'object_store_url': 'https://...'}

        Returns:
            Created ad set object
        """
        params = {
            'name': name,
            'campaign_id': campaign_id,
            'daily_budget': daily_budget,
            'targeting': targeting,
            'optimization_goal': optimization_goal,
            'billing_event': billing_event,
            'bid_strategy': bid_strategy,
            'status': status,
        }

        if bid_amount is not None:
            params['bid_amount'] = bid_amount

        if promoted_object:
            params['promoted_object'] = promoted_object

        adset = self.ad_account.create_ad_set(params=params)
        logger.info(f"Created ad set: {name} (ID: {adset['id']})")
        return adset

    def get_adsets(
        self,
        campaign_id: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> List[AdSet]:
        """Get ad sets.

        Args:
            campaign_id: Filter by campaign ID
            fields: Fields to retrieve

        Returns:
            List of ad sets
        """
        if fields is None:
            fields = [
                'id', 'name', 'status', 'campaign_id',
                'daily_budget', 'optimization_goal',
                'created_time', 'updated_time'
            ]

        if campaign_id:
            campaign = Campaign(campaign_id)
            adsets = campaign.get_ad_sets(fields=fields)
        else:
            adsets = self.ad_account.get_ad_sets(fields=fields)

        return list(adsets)

    def update_adset(self, adset_id: str, updates: Dict[str, Any]) -> AdSet:
        """Update an ad set.

        Args:
            adset_id: Ad set ID
            updates: Fields to update. To set a bid cap, pass:
                     {'bid_strategy': 'LOWEST_COST_WITH_BID_CAP', 'bid_amount': <cents>}
                     To remove a bid cap:
                     {'bid_strategy': 'LOWEST_COST_WITHOUT_CAP'}

        Returns:
            Updated ad set object
        """
        adset = AdSet(adset_id)
        adset.api_update(params=updates)
        logger.info(f"Updated ad set {adset_id}: {updates}")
        return adset

    def pause_adset(self, adset_id: str) -> AdSet:
        """Pause an ad set."""
        return self.update_adset(adset_id, {'status': 'PAUSED'})

    def activate_adset(self, adset_id: str) -> AdSet:
        """Activate an ad set."""
        return self.update_adset(adset_id, {'status': 'ACTIVE'})

    # Creative Management

    def upload_image(
        self,
        image_path: str,
        name: Optional[str] = None
    ) -> AdImage:
        """Upload an image to the ad account.

        Args:
            image_path: Path to the image file
            name: Optional name for the image

        Returns:
            Uploaded image object with hash
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        params = {
            'filename': str(path)
        }
        if name:
            params['name'] = name

        image = self.ad_account.create_ad_image(params=params)
        logger.info(f"Uploaded image: {path.name} (Hash: {image[AdImage.Field.hash]})")
        return image

    def upload_video(
        self,
        video_path: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> AdVideo:
        """Upload a video to the ad account.

        Args:
            video_path: Path to the video file
            name: Optional name for the video
            description: Optional description

        Returns:
            Uploaded video object
        """
        path = Path(video_path)
        if not path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        params = {
            'filepath': str(path)
        }
        if name:
            params['name'] = name
        if description:
            params['description'] = description

        video = self.ad_account.create_ad_video(params=params)
        logger.info(f"Uploaded video: {path.name} (ID: {video['id']})")
        return video

    def create_image_creative(
        self,
        name: str,
        image_hash: str,
        message: str,
        link: str,
        call_to_action_type: str = "LEARN_MORE",
        caption: Optional[str] = None,
        description: Optional[str] = None,
        headline: Optional[str] = None
    ) -> AdCreative:
        """Create an image ad creative.

        Args:
            name: Creative name
            image_hash: Hash of uploaded image
            message: Primary text/message
            link: Destination URL
            call_to_action_type: CTA button type (LEARN_MORE, SHOP_NOW, etc.)
            caption: Link caption
            description: Link description
            headline: Ad headline (displays in large text)

        Returns:
            Created ad creative object
        """
        object_story_spec = {
            'page_id': self.config['facebook'].get('page_id'),
            'link_data': {
                'image_hash': image_hash,
                'link': link,
                'message': message,
                'call_to_action': {
                    'type': call_to_action_type
                }
            }
        }

        if headline:
            object_story_spec['link_data']['name'] = headline
        if caption:
            object_story_spec['link_data']['caption'] = caption
        if description:
            object_story_spec['link_data']['description'] = description

        params = {
            'name': name,
            'object_story_spec': object_story_spec
        }

        creative = self.ad_account.create_ad_creative(params=params)
        logger.info(f"Created image creative: {name} (ID: {creative['id']})")
        return creative

    def create_video_creative(
        self,
        name: str,
        video_id: str,
        message: str,
        link: str,
        call_to_action_type: str = "LEARN_MORE",
        caption: Optional[str] = None,
        description: Optional[str] = None,
        thumbnail_url: Optional[str] = None
    ) -> AdCreative:
        """Create a video ad creative.

        Args:
            name: Creative name
            video_id: ID of uploaded video
            message: Primary text/message
            link: Destination URL
            call_to_action_type: CTA button type
            caption: Link caption
            description: Link description
            thumbnail_url: Custom thumbnail URL

        Returns:
            Created ad creative object
        """
        video_data = {
            'video_id': video_id,
            'message': message,
            'call_to_action': {
                'type': call_to_action_type,
                'value': {
                    'link': link
                }
            }
        }

        if caption:
            video_data['caption'] = caption
        if description:
            video_data['description'] = description
        if thumbnail_url:
            video_data['thumbnail_url'] = thumbnail_url

        params = {
            'name': name,
            'object_story_spec': {
                'page_id': self.config['facebook'].get('page_id'),
                'video_data': video_data
            }
        }

        creative = self.ad_account.create_ad_creative(params=params)
        logger.info(f"Created video creative: {name} (ID: {creative['id']})")
        return creative

    def create_carousel_creative(
        self,
        name: str,
        message: str,
        cards: List[Dict[str, Any]],
        link: str,
        call_to_action_type: str = "LEARN_MORE"
    ) -> AdCreative:
        """Create a carousel ad creative.

        Args:
            name: Creative name
            message: Primary text/message
            cards: List of carousel cards with image_hash, name, link, description
            link: Default destination URL
            call_to_action_type: CTA button type

        Returns:
            Created ad creative object

        Example cards format:
            [
                {
                    'image_hash': 'abc123',
                    'name': 'Card 1',
                    'link': 'https://example.com/product1',
                    'description': 'Product 1 description'
                },
                ...
            ]
        """
        child_attachments = []
        for card in cards:
            attachment = {
                'image_hash': card['image_hash'],
                'name': card['name'],
                'link': card.get('link', link),
                'call_to_action': {
                    'type': call_to_action_type
                }
            }
            if 'description' in card:
                attachment['description'] = card['description']

            child_attachments.append(attachment)

        params = {
            'name': name,
            'object_story_spec': {
                'page_id': self.config['facebook'].get('page_id'),
                'link_data': {
                    'link': link,
                    'message': message,
                    'child_attachments': child_attachments,
                    'call_to_action': {
                        'type': call_to_action_type
                    }
                }
            }
        }

        creative = self.ad_account.create_ad_creative(params=params)
        logger.info(f"Created carousel creative: {name} with {len(cards)} cards (ID: {creative['id']})")
        return creative

    def get_creatives(
        self,
        fields: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[AdCreative]:
        """Get ad creatives for the account.

        Args:
            fields: Fields to retrieve
            limit: Maximum number of creatives to return

        Returns:
            List of ad creatives
        """
        if fields is None:
            fields = [
                'id', 'name', 'status',
                'object_story_spec', 'image_url',
                'video_id', 'thumbnail_url',
                'effective_object_story_id'  # For getting actual post data
            ]

        creatives = self.ad_account.get_ad_creatives(
            fields=fields,
            params={'limit': limit}
        )

        # Convert to list and return
        return list(creatives)

    def get_creative(
        self,
        creative_id: str,
        fields: Optional[List[str]] = None
    ) -> AdCreative:
        """Get a specific ad creative.

        Args:
            creative_id: Creative ID
            fields: Fields to retrieve

        Returns:
            Ad creative object
        """
        if fields is None:
            fields = [
                'id', 'name', 'status',
                'object_story_spec', 'image_url',
                'video_id', 'thumbnail_url',
                'effective_object_story_id'
            ]

        creative = AdCreative(creative_id)
        creative.api_get(fields=fields)
        return creative

    def create_ad(
        self,
        adset_id: str,
        creative_id: str,
        name: str,
        status: str = "PAUSED"
    ) -> Ad:
        """Create an ad with a creative.

        Args:
            adset_id: Parent ad set ID
            creative_id: Creative ID to use
            name: Ad name
            status: Ad status (ACTIVE, PAUSED)

        Returns:
            Created ad object
        """
        params = {
            'name': name,
            'adset_id': adset_id,
            'creative': {'creative_id': creative_id},
            'status': status
        }

        ad = self.ad_account.create_ad(params=params)
        logger.info(f"Created ad: {name} (ID: {ad['id']})")
        return ad

    def get_ads(
        self,
        adset_id: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> List[Ad]:
        """Get ads for the account or ad set.

        Args:
            adset_id: Filter by ad set ID
            fields: Fields to retrieve

        Returns:
            List of ads
        """
        if fields is None:
            fields = [
                'id', 'name', 'status',
                'adset_id', 'creative',
                'created_time', 'updated_time'
            ]

        if adset_id:
            adset = AdSet(adset_id)
            ads = adset.get_ads(fields=fields)
        else:
            ads = self.ad_account.get_ads(fields=fields)

        return list(ads)

    def update_ad(
        self,
        ad_id: str,
        updates: Dict[str, Any]
    ) -> Ad:
        """Update an ad.

        Args:
            ad_id: Ad ID
            updates: Dictionary of fields to update

        Returns:
            Updated ad object
        """
        ad = Ad(ad_id)
        ad.api_update(params=updates)
        logger.info(f"Updated ad {ad_id}: {updates}")
        return ad

    def pause_ad(self, ad_id: str) -> Ad:
        """Pause an ad."""
        return self.update_ad(ad_id, {'status': 'PAUSED'})

    def activate_ad(self, ad_id: str) -> Ad:
        """Activate an ad."""
        return self.update_ad(ad_id, {'status': 'ACTIVE'})

    def delete_ad(self, ad_id: str):
        """Delete an ad."""
        ad = Ad(ad_id)
        ad.api_delete()
        logger.info(f"Deleted ad {ad_id}")

    def get_ad_preview(
        self,
        creative_id: str,
        ad_format: str = "DESKTOP_FEED_STANDARD"
    ) -> str:
        """Get HTML preview of an ad creative.

        Args:
            creative_id: Creative ID
            ad_format: Ad format (DESKTOP_FEED_STANDARD, MOBILE_FEED_STANDARD, etc.)

        Returns:
            HTML preview string
        """
        creative = AdCreative(creative_id)
        previews = creative.get_previews(params={'ad_format': ad_format})

        if previews:
            return previews[0].get('body', '')
        return ''

    # Analytics and Insights

    def get_campaign_insights(
        self,
        campaign_id: str,
        date_preset: str = "last_7d",
        fields: Optional[List[str]] = None
    ) -> List[Dict]:
        """Get insights for a campaign.

        Args:
            campaign_id: Campaign ID
            date_preset: Date range preset
            fields: Metrics to retrieve

        Returns:
            List of insight data
        """
        if fields is None:
            fields = [
                'impressions', 'clicks', 'spend', 'ctr', 'cpc',
                'actions', 'frequency', 'reach'
            ]

        campaign = Campaign(campaign_id)
        insights = campaign.get_insights(
            fields=fields,
            params={'date_preset': date_preset}
        )

        return [dict(insight) for insight in insights]

    def get_account_insights(
        self,
        date_preset: str = "last_7d",
        level: str = "campaign",
        fields: Optional[List[str]] = None
    ) -> List[Dict]:
        """Get insights for the entire ad account.

        Args:
            date_preset: Date range preset
            level: Aggregation level (account, campaign, adset, ad)
            fields: Metrics to retrieve

        Returns:
            List of insight data
        """
        if fields is None:
            fields = [
                'campaign_id', 'campaign_name',
                'impressions', 'clicks', 'spend',
                'ctr', 'cpc', 'actions'
            ]

        insights = self.ad_account.get_insights(
            fields=fields,
            params={
                'date_preset': date_preset,
                'level': level
            }
        )

        return [dict(insight) for insight in insights]

    # Utility Methods

    def create_pixel(self, name: str) -> Dict:
        """
        Create a Facebook Pixel for conversion tracking.

        Args:
            name: Name for the pixel (e.g., "My Website Pixel")

        Returns:
            Dict with pixel_id and pixel details
        """
        try:
            params = {
                'name': name
            }

            pixel = self.ad_account.create_ads_pixel(params=params)
            pixel_id = pixel['id']

            logger.info(f"Created pixel: {name} (ID: {pixel_id})")

            return {
                'id': pixel_id,
                'name': name,
                'code': pixel.get('code'),  # Pixel code snippet if available
            }
        except Exception as e:
            logger.error(f"Failed to create pixel: {e}")
            raise

    def get_pixels(self) -> List[Dict]:
        """
        Get all pixels for this ad account.

        Returns:
            List of pixel dictionaries
        """
        try:
            pixels = self.ad_account.get_ads_pixels(fields=['id', 'name', 'code'])
            return [dict(pixel) for pixel in pixels]
        except Exception as e:
            logger.error(f"Failed to get pixels: {e}")
            raise

    def get_account_info(self) -> Dict:
        """Get ad account information."""
        account = self.ad_account.api_get(fields=[
            'id', 'name', 'currency', 'timezone_name',
            'account_status', 'amount_spent', 'balance'
        ])
        return dict(account)

    def validate_credentials(self) -> bool:
        """Validate API credentials by making a test call."""
        try:
            self.get_account_info()
            logger.info("API credentials validated successfully")
            return True
        except Exception as e:
            logger.error(f"Credential validation failed: {e}")
            return False
