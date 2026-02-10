"""Campaign management module."""

from typing import Dict, List, Optional
from loguru import logger


class CampaignManager:
    """Manages Facebook ad campaigns."""

    def __init__(self, api_client):
        """Initialize campaign manager.

        Args:
            api_client: FacebookAdsClient instance
        """
        self.client = api_client
        self.config = api_client.config

    def create_campaign(
        self,
        name: str,
        objective: str,
        daily_budget: float,
        status: str = "PAUSED",
        special_ad_categories: Optional[List[str]] = None
    ) -> Dict:
        """Create a new campaign with default settings.

        Args:
            name: Campaign name
            objective: Campaign objective
            daily_budget: Daily budget in USD
            status: Initial status
            special_ad_categories: Special categories if applicable (defaults to empty for regular ads)

        Returns:
            Created campaign data
        """
        # Convert budget to cents
        budget_cents = int(daily_budget * 100)

        # Default to empty array for special_ad_categories (required by Facebook)
        if special_ad_categories is None:
            special_ad_categories = []

        campaign = self.client.create_campaign(
            name=name,
            objective=objective,
            status=status,
            special_ad_categories=special_ad_categories
        )

        # Create default ad set if campaign is created successfully
        if campaign and status == "ACTIVE":
            self._create_default_adset(campaign['id'], budget_cents)

        return dict(campaign)

    def _create_default_adset(self, campaign_id: str, budget_cents: int):
        """Create a default ad set for a campaign.

        Args:
            campaign_id: Campaign ID
            budget_cents: Budget in cents
        """
        targeting = self._get_default_targeting()

        adset = self.client.create_adset(
            campaign_id=campaign_id,
            name=f"Ad Set 1",
            daily_budget=budget_cents,
            targeting=targeting,
            optimization_goal="LINK_CLICKS",
            status="ACTIVE"
        )

        logger.info(f"Created default ad set for campaign {campaign_id}")
        return adset

    def _get_default_targeting(self) -> Dict:
        """Get default targeting parameters from config."""
        targeting_config = self.config.get('targeting', {})

        return {
            'geo_locations': {
                'countries': targeting_config.get('default_countries', ['US'])
            },
            'age_min': targeting_config.get('default_age_min', 25),
            'age_max': targeting_config.get('default_age_max', 65),
        }

    def list_campaigns(
        self,
        status_filter: Optional[str] = None,
        include_insights: bool = False
    ) -> List[Dict]:
        """List campaigns with optional filtering.

        Args:
            status_filter: Filter by status (ACTIVE, PAUSED, etc.)
            include_insights: Include performance insights

        Returns:
            List of campaign data
        """
        filtering = []
        if status_filter:
            filtering.append({
                'field': 'status',
                'operator': 'EQUAL',
                'value': status_filter
            })

        campaigns = self.client.get_campaigns(filtering=filtering if filtering else None)

        results = []
        for campaign in campaigns:
            camp_data = dict(campaign)

            if include_insights:
                insights = self.client.get_campaign_insights(campaign['id'])
                if insights:
                    camp_data['insights'] = insights[0]

            results.append(camp_data)

        return results

    def pause_campaign(self, campaign_id: str):
        """Pause a campaign."""
        self.client.pause_campaign(campaign_id)
        logger.info(f"Paused campaign {campaign_id}")

    def activate_campaign(self, campaign_id: str):
        """Activate a campaign."""
        self.client.activate_campaign(campaign_id)
        logger.info(f"Activated campaign {campaign_id}")

    def update_budget(self, campaign_id: str, new_budget: float):
        """Update campaign budget.

        Args:
            campaign_id: Campaign ID
            new_budget: New daily budget in USD
        """
        budget_cents = int(new_budget * 100)

        # Update ad sets associated with campaign
        adsets = self.client.get_adsets(campaign_id=campaign_id)
        for adset in adsets:
            self.client.update_campaign(adset['id'], {'daily_budget': budget_cents})

        logger.info(f"Updated budget for campaign {campaign_id} to ${new_budget}")

    def duplicate_campaign(
        self,
        campaign_id: str,
        new_name: Optional[str] = None
    ) -> Dict:
        """Duplicate a campaign.

        Args:
            campaign_id: Source campaign ID
            new_name: Name for duplicated campaign

        Returns:
            New campaign data
        """
        # Get source campaign
        campaigns = self.client.get_campaigns()
        source = next((c for c in campaigns if c['id'] == campaign_id), None)

        if not source:
            raise ValueError(f"Campaign {campaign_id} not found")

        # Create duplicate
        name = new_name or f"{source['name']} (Copy)"
        return self.create_campaign(
            name=name,
            objective=source['objective'],
            daily_budget=source.get('daily_budget', 5000) / 100,  # Convert cents to USD
            status='PAUSED'
        )
