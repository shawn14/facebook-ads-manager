"""Budget optimization module."""

from typing import Dict, List, Optional
from loguru import logger


class BudgetOptimizer:
    """Optimizes budget allocation across campaigns."""

    def __init__(self, api_client):
        """Initialize budget optimizer.

        Args:
            api_client: FacebookAdsClient instance
        """
        self.client = api_client
        self.config = api_client.config

    def optimize_budgets(
        self,
        min_roas: Optional[float] = None,
        dry_run: bool = True
    ) -> List[Dict]:
        """Optimize budget allocation based on performance.

        Args:
            min_roas: Minimum ROAS threshold
            dry_run: Preview changes without applying

        Returns:
            List of budget changes
        """
        min_roas = min_roas or self.config.get('optimization', {}).get('min_roas', 1.5)

        # Get all active campaigns with insights
        campaigns = self.client.get_campaigns(filtering=[{
            'field': 'status',
            'operator': 'EQUAL',
            'value': 'ACTIVE'
        }])

        changes = []

        for campaign in campaigns:
            # Get performance data
            insights = self.client.get_campaign_insights(
                campaign['id'],
                date_preset='last_7d'
            )

            if not insights or not insights[0]:
                continue

            insight = insights[0]
            current_budget = int(campaign.get('daily_budget', 0)) / 100  # Convert cents to USD

            # Calculate ROAS
            spend = float(insight.get('spend', 0))
            conversions = self._extract_conversions(insight)
            revenue = conversions * self.config.get('analytics', {}).get('avg_order_value', 50)
            roas = (revenue / spend) if spend > 0 else 0

            # Determine budget change
            new_budget = self._calculate_optimal_budget(
                current_budget,
                roas,
                min_roas,
                spend
            )

            if new_budget != current_budget:
                change_pct = ((new_budget - current_budget) / current_budget) * 100

                change = {
                    'campaign_id': campaign['id'],
                    'campaign_name': campaign['name'],
                    'old_budget': current_budget,
                    'new_budget': new_budget,
                    'change_pct': change_pct,
                    'roas': roas,
                    'reason': self._get_change_reason(roas, min_roas, change_pct)
                }

                changes.append(change)

                # Apply change if not dry run
                if not dry_run:
                    self._update_campaign_budget(campaign['id'], new_budget)
                    logger.info(f"Updated budget for {campaign['name']}: ${current_budget} → ${new_budget}")

        return changes

    def _calculate_optimal_budget(
        self,
        current_budget: float,
        roas: float,
        min_roas: float,
        spend: float
    ) -> float:
        """Calculate optimal budget based on performance.

        Args:
            current_budget: Current daily budget
            roas: Current ROAS
            min_roas: Minimum acceptable ROAS
            spend: Total spend in period

        Returns:
            Optimal budget
        """
        min_budget = self.config.get('campaigns', {}).get('min_daily_budget', 10)
        max_budget = self.config.get('campaigns', {}).get('max_daily_budget', 5000)

        # High performers - increase budget
        if roas >= min_roas * 1.5:
            new_budget = current_budget * 1.2  # Increase by 20%
        # Good performers - slight increase
        elif roas >= min_roas * 1.2:
            new_budget = current_budget * 1.1  # Increase by 10%
        # Meeting threshold - maintain
        elif roas >= min_roas:
            new_budget = current_budget
        # Below threshold but close - slight decrease
        elif roas >= min_roas * 0.8:
            new_budget = current_budget * 0.9  # Decrease by 10%
        # Poor performers - significant decrease
        else:
            new_budget = current_budget * 0.7  # Decrease by 30%

        # Enforce limits
        new_budget = max(min_budget, min(max_budget, new_budget))

        # Round to nearest $5
        new_budget = round(new_budget / 5) * 5

        return new_budget

    def _get_change_reason(self, roas: float, min_roas: float, change_pct: float) -> str:
        """Get human-readable reason for budget change.

        Args:
            roas: Current ROAS
            min_roas: Minimum ROAS threshold
            change_pct: Percentage change

        Returns:
            Reason string
        """
        if change_pct > 0:
            if roas >= min_roas * 1.5:
                return f"High ROAS ({roas:.2f}x) - scaling up"
            elif roas >= min_roas:
                return f"Good ROAS ({roas:.2f}x) - increasing budget"
        else:
            if roas < min_roas:
                return f"Low ROAS ({roas:.2f}x) - reducing budget"
            else:
                return f"Below threshold ({roas:.2f}x < {min_roas:.2f}x)"

        return "Budget optimization"

    def pause_underperformers(
        self,
        min_ctr: float = 0.5,
        min_spend: float = 100,
        dry_run: bool = True
    ) -> List[Dict]:
        """Pause campaigns that are underperforming.

        Args:
            min_ctr: Minimum CTR threshold (%)
            min_spend: Minimum spend to evaluate
            dry_run: Preview without pausing

        Returns:
            List of paused campaigns
        """
        campaigns = self.client.get_campaigns(filtering=[{
            'field': 'status',
            'operator': 'EQUAL',
            'value': 'ACTIVE'
        }])

        paused = []

        for campaign in campaigns:
            insights = self.client.get_campaign_insights(
                campaign['id'],
                date_preset='last_7d'
            )

            if not insights:
                continue

            insight = insights[0]
            spend = float(insight.get('spend', 0))

            # Skip if not enough spend
            if spend < min_spend:
                continue

            # Calculate CTR
            impressions = int(insight.get('impressions', 0))
            clicks = int(insight.get('clicks', 0))
            ctr = (clicks / impressions * 100) if impressions > 0 else 0

            # Check if underperforming
            if ctr < min_ctr:
                paused.append({
                    'campaign_id': campaign['id'],
                    'campaign_name': campaign['name'],
                    'ctr': ctr,
                    'spend': spend,
                    'reason': f"CTR ({ctr:.2f}%) below threshold ({min_ctr}%)"
                })

                if not dry_run:
                    self.client.pause_campaign(campaign['id'])
                    logger.warning(f"Paused underperforming campaign: {campaign['name']}")

        return paused

    def _update_campaign_budget(self, campaign_id: str, new_budget: float):
        """Update campaign budget through ad sets.

        Args:
            campaign_id: Campaign ID
            new_budget: New budget in USD
        """
        budget_cents = int(new_budget * 100)

        # Get ad sets for campaign
        adsets = self.client.get_adsets(campaign_id=campaign_id)

        # Update each ad set
        for adset in adsets:
            from facebook_business.adobjects.adset import AdSet
            ad_set = AdSet(adset['id'])
            ad_set.api_update(params={'daily_budget': budget_cents})

    def _extract_conversions(self, insight: Dict) -> int:
        """Extract conversion count from insights.

        Args:
            insight: Insights data

        Returns:
            Number of conversions
        """
        if 'actions' not in insight:
            return 0

        for action in insight['actions']:
            action_type = action.get('action_type', '').lower()
            if 'purchase' in action_type or 'conversion' in action_type:
                return int(action.get('value', 0))

        return 0

    def rebalance_portfolio(self, total_budget: float, dry_run: bool = True) -> List[Dict]:
        """Rebalance budget across all campaigns to maximize ROI.

        Args:
            total_budget: Total budget to allocate
            dry_run: Preview without applying

        Returns:
            List of allocations
        """
        # Get all active campaigns with performance data
        campaigns = self.client.get_campaigns(filtering=[{
            'field': 'status',
            'operator': 'EQUAL',
            'value': 'ACTIVE'
        }])

        # Calculate performance scores
        scored_campaigns = []
        for campaign in campaigns:
            insights = self.client.get_campaign_insights(campaign['id'], date_preset='last_7d')
            if not insights:
                continue

            insight = insights[0]
            spend = float(insight.get('spend', 0))
            conversions = self._extract_conversions(insight)
            revenue = conversions * self.config.get('analytics', {}).get('avg_order_value', 50)
            roas = (revenue / spend) if spend > 0 else 0

            scored_campaigns.append({
                'campaign': campaign,
                'roas': roas,
                'current_budget': int(campaign.get('daily_budget', 0)) / 100
            })

        # Sort by ROAS
        scored_campaigns.sort(key=lambda x: x['roas'], reverse=True)

        # Allocate budget proportional to ROAS
        total_roas = sum(c['roas'] for c in scored_campaigns if c['roas'] > 0)

        allocations = []
        for item in scored_campaigns:
            if item['roas'] <= 0:
                new_budget = 0
            else:
                proportion = item['roas'] / total_roas
                new_budget = total_budget * proportion

            allocations.append({
                'campaign_id': item['campaign']['id'],
                'campaign_name': item['campaign']['name'],
                'old_budget': item['current_budget'],
                'new_budget': new_budget,
                'roas': item['roas']
            })

            if not dry_run:
                self._update_campaign_budget(item['campaign']['id'], new_budget)

        return allocations
