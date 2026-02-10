"""Pre-built workflow automation for common tasks."""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger


class WorkflowAutomation:
    """Pre-built workflows for common automation tasks."""

    def __init__(self, api_client):
        """Initialize workflow automation.

        Args:
            api_client: FacebookAdsClient instance
        """
        self.client = api_client
        self.config = api_client.config

    def daily_performance_check(self, dry_run: bool = True) -> Dict:
        """Daily performance check workflow.

        Checks all active campaigns and:
        - Pauses campaigns with low CTR
        - Reduces budget for underperformers
        - Increases budget for high performers
        - Sends alerts for anomalies

        Args:
            dry_run: Preview without making changes

        Returns:
            Summary of actions taken
        """
        logger.info("Running daily performance check workflow")

        results = {
            'paused': [],
            'budget_increased': [],
            'budget_decreased': [],
            'alerts': [],
            'timestamp': datetime.now().isoformat()
        }

        # Get all active campaigns
        campaigns = self.client.get_campaigns(filtering=[{
            'field': 'status',
            'operator': 'EQUAL',
            'value': 'ACTIVE'
        }])

        min_ctr = self.config.get('optimization', {}).get('min_ctr', 0.5)
        min_roas = self.config.get('optimization', {}).get('min_roas', 1.5)

        for campaign in campaigns:
            try:
                # Get performance metrics
                insights = self.client.get_campaign_insights(campaign['id'], date_preset='last_7d')

                if not insights or not insights[0]:
                    continue

                insight = insights[0]
                spend = float(insight.get('spend', 0))

                # Skip if not enough data
                if spend < 50:
                    continue

                impressions = int(insight.get('impressions', 0))
                clicks = int(insight.get('clicks', 0))
                ctr = (clicks / impressions * 100) if impressions > 0 else 0

                # Calculate ROAS
                conversions = self._extract_conversions(insight)
                avg_order_value = self.config.get('analytics', {}).get('avg_order_value', 50)
                revenue = conversions * avg_order_value
                roas = (revenue / spend) if spend > 0 else 0

                current_budget = int(campaign.get('daily_budget', 0)) / 100

                # Action 1: Pause very low performers
                if ctr < min_ctr * 0.5 and spend > 100:
                    if not dry_run:
                        self.client.pause_campaign(campaign['id'])

                    results['paused'].append({
                        'campaign_id': campaign['id'],
                        'campaign_name': campaign['name'],
                        'ctr': ctr,
                        'spend': spend,
                        'reason': f"CTR ({ctr:.2f}%) significantly below threshold"
                    })

                # Action 2: Reduce budget for low ROAS
                elif roas < min_roas * 0.7 and roas > 0:
                    new_budget = current_budget * 0.8

                    if not dry_run:
                        self._update_budget(campaign['id'], new_budget)

                    results['budget_decreased'].append({
                        'campaign_id': campaign['id'],
                        'campaign_name': campaign['name'],
                        'old_budget': current_budget,
                        'new_budget': new_budget,
                        'roas': roas,
                        'reason': f"ROAS ({roas:.2f}) below target"
                    })

                # Action 3: Increase budget for high performers
                elif roas >= min_roas * 1.5:
                    new_budget = min(current_budget * 1.2, 5000)

                    if not dry_run:
                        self._update_budget(campaign['id'], new_budget)

                    results['budget_increased'].append({
                        'campaign_id': campaign['id'],
                        'campaign_name': campaign['name'],
                        'old_budget': current_budget,
                        'new_budget': new_budget,
                        'roas': roas,
                        'reason': f"High ROAS ({roas:.2f}), scaling up"
                    })

                # Action 4: Alert on anomalies
                if spend > current_budget * 1.5:
                    results['alerts'].append({
                        'campaign_id': campaign['id'],
                        'campaign_name': campaign['name'],
                        'type': 'overspend',
                        'message': f"Spending ${spend:.2f} exceeded budget ${current_budget:.2f}"
                    })

            except Exception as e:
                logger.error(f"Error processing campaign {campaign['id']}: {e}")

        logger.info(f"Daily check complete: {len(results['paused'])} paused, "
                   f"{len(results['budget_increased'])} increased, "
                   f"{len(results['budget_decreased'])} decreased")

        return results

    def weekend_campaign_pause(self, dry_run: bool = True) -> Dict:
        """Pause campaigns on weekends (if targeting B2B).

        Args:
            dry_run: Preview without making changes

        Returns:
            Summary of paused campaigns
        """
        logger.info("Running weekend campaign pause workflow")

        results = {
            'paused': [],
            'timestamp': datetime.now().isoformat()
        }

        # Check if today is weekend
        today = datetime.now().weekday()
        if today not in [5, 6]:  # Saturday=5, Sunday=6
            logger.info("Not a weekend day, skipping")
            return results

        # Get all active campaigns
        campaigns = self.client.get_campaigns(filtering=[{
            'field': 'status',
            'operator': 'EQUAL',
            'value': 'ACTIVE'
        }])

        for campaign in campaigns:
            # Check if campaign is marked for weekend pause
            # (In real implementation, you'd check campaign tags or metadata)
            if 'B2B' in campaign['name'] or 'business' in campaign['name'].lower():
                if not dry_run:
                    self.client.pause_campaign(campaign['id'])

                results['paused'].append({
                    'campaign_id': campaign['id'],
                    'campaign_name': campaign['name'],
                    'reason': 'Weekend B2B pause'
                })

        logger.info(f"Weekend pause complete: {len(results['paused'])} campaigns paused")
        return results

    def campaign_refresh(self, campaign_id: str, dry_run: bool = True) -> Dict:
        """Refresh a campaign by duplicating and pausing the original.

        Useful for combating ad fatigue.

        Args:
            campaign_id: Campaign to refresh
            dry_run: Preview without making changes

        Returns:
            Summary of refresh operation
        """
        logger.info(f"Running campaign refresh workflow for {campaign_id}")

        results = {
            'original_campaign_id': campaign_id,
            'new_campaign_id': None,
            'actions': [],
            'timestamp': datetime.now().isoformat()
        }

        try:
            if not dry_run:
                from src.campaign.manager import CampaignManager
                manager = CampaignManager(self.client)

                # Duplicate campaign
                campaigns = self.client.get_campaigns()
                original = next((c for c in campaigns if c['id'] == campaign_id), None)

                if not original:
                    raise ValueError(f"Campaign {campaign_id} not found")

                new_name = f"{original['name']} - Refresh {datetime.now().strftime('%m/%d')}"
                new_campaign = manager.duplicate_campaign(campaign_id, new_name)

                results['new_campaign_id'] = new_campaign['id']
                results['actions'].append(f"Duplicated campaign as {new_campaign['id']}")

                # Activate new campaign
                manager.activate_campaign(new_campaign['id'])
                results['actions'].append("Activated new campaign")

                # Pause original
                manager.pause_campaign(campaign_id)
                results['actions'].append("Paused original campaign")

            else:
                results['actions'].append(f"Would duplicate and refresh campaign {campaign_id}")

            logger.info(f"Campaign refresh complete")

        except Exception as e:
            logger.error(f"Error refreshing campaign: {e}")
            results['error'] = str(e)

        return results

    def smart_budget_rebalance(self, total_budget: float, dry_run: bool = True) -> Dict:
        """Intelligently rebalance budget across all campaigns.

        Args:
            total_budget: Total daily budget to allocate
            dry_run: Preview without making changes

        Returns:
            Summary of budget changes
        """
        logger.info(f"Running smart budget rebalance for ${total_budget} total budget")

        from src.optimization.optimizer import BudgetOptimizer
        optimizer = BudgetOptimizer(self.client)

        # Use the optimizer's rebalance method
        allocations = optimizer.rebalance_portfolio(total_budget, dry_run=dry_run)

        results = {
            'total_budget': total_budget,
            'allocations': allocations,
            'campaigns_updated': len(allocations),
            'timestamp': datetime.now().isoformat()
        }

        logger.info(f"Budget rebalance complete: {len(allocations)} campaigns updated")
        return results

    def campaign_health_report(self) -> Dict:
        """Generate comprehensive health report for all campaigns.

        Returns:
            Health report with scores and recommendations
        """
        logger.info("Generating campaign health report")

        report = {
            'campaigns': [],
            'summary': {
                'healthy': 0,
                'warning': 0,
                'critical': 0
            },
            'timestamp': datetime.now().isoformat()
        }

        campaigns = self.client.get_campaigns(filtering=[{
            'field': 'status',
            'operator': 'EQUAL',
            'value': 'ACTIVE'
        }])

        min_ctr = self.config.get('optimization', {}).get('min_ctr', 0.5)
        min_roas = self.config.get('optimization', {}).get('min_roas', 1.5)

        for campaign in campaigns:
            try:
                insights = self.client.get_campaign_insights(campaign['id'], date_preset='last_7d')

                if not insights or not insights[0]:
                    continue

                insight = insights[0]
                spend = float(insight.get('spend', 0))

                # Skip campaigns with minimal spend
                if spend < 10:
                    continue

                impressions = int(insight.get('impressions', 0))
                clicks = int(insight.get('clicks', 0))
                ctr = (clicks / impressions * 100) if impressions > 0 else 0
                cpc = float(insight.get('cpc', 0))

                # Calculate ROAS
                conversions = self._extract_conversions(insight)
                avg_order_value = self.config.get('analytics', {}).get('avg_order_value', 50)
                revenue = conversions * avg_order_value
                roas = (revenue / spend) if spend > 0 else 0

                # Calculate health score (0-100)
                health_score = 50  # Start neutral

                # CTR contribution
                if ctr >= min_ctr * 1.5:
                    health_score += 20
                elif ctr >= min_ctr:
                    health_score += 10
                elif ctr < min_ctr * 0.5:
                    health_score -= 30

                # ROAS contribution
                if roas >= min_roas * 1.5:
                    health_score += 30
                elif roas >= min_roas:
                    health_score += 15
                elif roas < min_roas * 0.5:
                    health_score -= 30

                # Determine status
                if health_score >= 70:
                    status = 'healthy'
                    report['summary']['healthy'] += 1
                elif health_score >= 40:
                    status = 'warning'
                    report['summary']['warning'] += 1
                else:
                    status = 'critical'
                    report['summary']['critical'] += 1

                # Generate recommendations
                recommendations = []
                if ctr < min_ctr:
                    recommendations.append("Consider refreshing ad creative (low CTR)")
                if roas < min_roas:
                    recommendations.append("Review targeting and reduce budget (low ROAS)")
                if cpc > 5.0:
                    recommendations.append("High CPC - optimize bidding strategy")
                if conversions == 0 and spend > 100:
                    recommendations.append("No conversions - review funnel and landing page")

                report['campaigns'].append({
                    'campaign_id': campaign['id'],
                    'campaign_name': campaign['name'],
                    'health_score': health_score,
                    'status': status,
                    'metrics': {
                        'spend': spend,
                        'impressions': impressions,
                        'clicks': clicks,
                        'ctr': round(ctr, 2),
                        'cpc': round(cpc, 2),
                        'conversions': conversions,
                        'roas': round(roas, 2)
                    },
                    'recommendations': recommendations
                })

            except Exception as e:
                logger.error(f"Error analyzing campaign {campaign['id']}: {e}")

        # Sort by health score (worst first)
        report['campaigns'].sort(key=lambda x: x['health_score'])

        logger.info(f"Health report generated: {report['summary']}")
        return report

    def emergency_pause_all(self, reason: str = "Emergency pause", dry_run: bool = True) -> Dict:
        """Emergency pause all active campaigns.

        Args:
            reason: Reason for pause
            dry_run: Preview without making changes

        Returns:
            Summary of paused campaigns
        """
        logger.warning(f"Running emergency pause: {reason}")

        results = {
            'paused': [],
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }

        campaigns = self.client.get_campaigns(filtering=[{
            'field': 'status',
            'operator': 'EQUAL',
            'value': 'ACTIVE'
        }])

        for campaign in campaigns:
            if not dry_run:
                self.client.pause_campaign(campaign['id'])

            results['paused'].append({
                'campaign_id': campaign['id'],
                'campaign_name': campaign['name']
            })

        logger.warning(f"Emergency pause complete: {len(results['paused'])} campaigns paused")
        return results

    def scale_winners(self, min_roas: float = 2.0, scale_factor: float = 1.5, dry_run: bool = True) -> Dict:
        """Scale up budget for winning campaigns.

        Args:
            min_roas: Minimum ROAS to qualify as winner
            scale_factor: Budget multiplier
            dry_run: Preview without making changes

        Returns:
            Summary of scaled campaigns
        """
        logger.info(f"Scaling winners with ROAS >= {min_roas}x by {scale_factor}x")

        results = {
            'scaled': [],
            'timestamp': datetime.now().isoformat()
        }

        campaigns = self.client.get_campaigns(filtering=[{
            'field': 'status',
            'operator': 'EQUAL',
            'value': 'ACTIVE'
        }])

        for campaign in campaigns:
            try:
                insights = self.client.get_campaign_insights(campaign['id'], date_preset='last_7d')

                if not insights or not insights[0]:
                    continue

                insight = insights[0]
                spend = float(insight.get('spend', 0))

                # Skip campaigns with minimal spend
                if spend < 100:
                    continue

                # Calculate ROAS
                conversions = self._extract_conversions(insight)
                avg_order_value = self.config.get('analytics', {}).get('avg_order_value', 50)
                revenue = conversions * avg_order_value
                roas = (revenue / spend) if spend > 0 else 0

                if roas >= min_roas:
                    current_budget = int(campaign.get('daily_budget', 0)) / 100
                    new_budget = min(current_budget * scale_factor, 10000)  # Cap at $10k

                    if not dry_run:
                        self._update_budget(campaign['id'], new_budget)

                    results['scaled'].append({
                        'campaign_id': campaign['id'],
                        'campaign_name': campaign['name'],
                        'roas': round(roas, 2),
                        'old_budget': current_budget,
                        'new_budget': new_budget,
                        'increase': round((new_budget - current_budget) / current_budget * 100, 1)
                    })

            except Exception as e:
                logger.error(f"Error scaling campaign {campaign['id']}: {e}")

        logger.info(f"Scaling complete: {len(results['scaled'])} campaigns scaled")
        return results

    def _update_budget(self, campaign_id: str, new_budget: float):
        """Update campaign budget.

        Args:
            campaign_id: Campaign ID
            new_budget: New budget in USD
        """
        from src.campaign.manager import CampaignManager
        manager = CampaignManager(self.client)
        manager.update_budget(campaign_id, new_budget)

    def _extract_conversions(self, insight: Dict) -> int:
        """Extract conversion count from insights."""
        if 'actions' not in insight:
            return 0

        for action in insight['actions']:
            action_type = action.get('action_type', '').lower()
            if 'purchase' in action_type or 'conversion' in action_type:
                return int(action.get('value', 0))

        return 0
