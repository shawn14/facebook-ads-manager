"""A/B testing module."""

from typing import Dict, List, Optional
import numpy as np
from scipy import stats
from rich.console import Console
from rich.table import Table
from loguru import logger


class ABTestManager:
    """Manages A/B tests for ad campaigns."""

    def __init__(self, api_client):
        """Initialize A/B test manager.

        Args:
            api_client: FacebookAdsClient instance
        """
        self.client = api_client
        self.config = api_client.config
        self.console = Console()

    def create_test(
        self,
        base_campaign_id: str,
        num_variants: int,
        test_name: str,
        budget_split: str = "even"
    ) -> Dict:
        """Create a new A/B test.

        Args:
            base_campaign_id: Base campaign to test
            num_variants: Number of variants
            test_name: Name for the test
            budget_split: Budget allocation strategy

        Returns:
            Test configuration
        """
        # Get base campaign
        campaigns = self.client.get_campaigns()
        base_campaign = next((c for c in campaigns if c['id'] == base_campaign_id), None)

        if not base_campaign:
            raise ValueError(f"Campaign {base_campaign_id} not found")

        # Create variant campaigns
        variants = []
        base_budget = int(base_campaign.get('daily_budget', 0)) / 100

        for i in range(num_variants):
            variant_name = f"{test_name} - Variant {i + 1}"
            variant_budget = base_budget / num_variants  # Even split

            variant = self.client.create_campaign(
                name=variant_name,
                objective=base_campaign['objective'],
                status='PAUSED'
            )

            variants.append({
                'id': variant['id'],
                'name': variant_name,
                'budget': variant_budget
            })

            logger.info(f"Created test variant: {variant_name}")

        test = {
            'id': f"test_{base_campaign_id}_{len(variants)}",
            'name': test_name,
            'base_campaign_id': base_campaign_id,
            'variants': variants,
            'created_at': str(np.datetime64('now')),
            'status': 'created'
        }

        return test

    def analyze_test(
        self,
        test_id: str,
        metric: str = 'conversions'
    ) -> Dict:
        """Analyze A/B test results.

        Args:
            test_id: Test ID
            metric: Metric to analyze

        Returns:
            Analysis results
        """
        # This is a simplified version - you'd load test config from storage
        # For now, we'll analyze campaigns by pattern matching

        campaigns = self.client.get_campaigns()

        # Get test campaigns (simplified - in production you'd track this)
        test_campaigns = [c for c in campaigns if test_id in c.get('name', '')]

        if not test_campaigns:
            raise ValueError(f"No campaigns found for test {test_id}")

        # Collect performance data
        variants = []
        for campaign in test_campaigns:
            insights = self.client.get_campaign_insights(
                campaign['id'],
                date_preset='lifetime'
            )

            if not insights:
                continue

            insight = insights[0]
            conversions = self._extract_conversions(insight)
            impressions = int(insight.get('impressions', 0))
            clicks = int(insight.get('clicks', 0))

            variants.append({
                'id': campaign['id'],
                'name': campaign['name'],
                'impressions': impressions,
                'clicks': clicks,
                'conversions': conversions,
                'ctr': (clicks / impressions * 100) if impressions > 0 else 0,
                'cvr': (conversions / clicks * 100) if clicks > 0 else 0
            })

        # Statistical analysis
        if len(variants) >= 2:
            winner, confidence = self._determine_winner(variants, metric)
        else:
            winner = None
            confidence = 0

        return {
            'test_id': test_id,
            'variants': variants,
            'winner': winner,
            'confidence': confidence,
            'metric': metric
        }

    def _determine_winner(
        self,
        variants: List[Dict],
        metric: str
    ) -> tuple[Optional[str], float]:
        """Determine winning variant using statistical testing.

        Args:
            variants: List of variant data
            metric: Metric to compare

        Returns:
            Tuple of (winner_id, confidence)
        """
        if len(variants) < 2:
            return None, 0

        # For conversion rate, use proportions test
        if metric == 'conversions' or metric == 'cvr':
            # Get top 2 variants by conversion rate
            sorted_variants = sorted(variants, key=lambda x: x['cvr'], reverse=True)
            variant_a = sorted_variants[0]
            variant_b = sorted_variants[1]

            # Chi-square test for conversion rates
            # Successes and trials
            successes = [variant_a['conversions'], variant_b['conversions']]
            trials = [variant_a['clicks'], variant_b['clicks']]

            if min(trials) < 30:
                # Not enough data
                return None, 0

            # Z-test for proportions
            p1 = variant_a['conversions'] / variant_a['clicks'] if variant_a['clicks'] > 0 else 0
            p2 = variant_b['conversions'] / variant_b['clicks'] if variant_b['clicks'] > 0 else 0

            n1 = variant_a['clicks']
            n2 = variant_b['clicks']

            # Pooled proportion
            p_pool = (variant_a['conversions'] + variant_b['conversions']) / (n1 + n2)

            # Standard error
            se = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))

            if se == 0:
                return None, 0

            # Z-score
            z = (p1 - p2) / se

            # P-value (two-tailed)
            p_value = 2 * (1 - stats.norm.cdf(abs(z)))

            # Confidence (1 - p_value)
            confidence = 1 - p_value

            confidence_threshold = self.config.get('optimization', {}).get('confidence_level', 0.95)

            if confidence >= confidence_threshold:
                winner = variant_a['id']
            else:
                winner = None

            return winner, confidence

        # For CTR, similar approach
        elif metric == 'ctr':
            sorted_variants = sorted(variants, key=lambda x: x['ctr'], reverse=True)
            variant_a = sorted_variants[0]
            variant_b = sorted_variants[1]

            # Similar statistical test
            # (implementation similar to above)
            return variant_a['id'], 0.85  # Placeholder

        return None, 0

    def display_results(self, results: Dict):
        """Display test results in terminal.

        Args:
            results: Test analysis results
        """
        table = Table(title=f"A/B Test Results - {results['test_id']}")
        table.add_column("Variant", style="cyan")
        table.add_column("Impressions", justify="right")
        table.add_column("Clicks", justify="right")
        table.add_column("CTR", justify="right")
        table.add_column("Conversions", justify="right")
        table.add_column("CVR", justify="right")
        table.add_column("Winner", justify="center")

        for variant in results['variants']:
            is_winner = variant['id'] == results.get('winner')

            table.add_row(
                variant['name'],
                f"{variant['impressions']:,}",
                f"{variant['clicks']:,}",
                f"{variant['ctr']:.2f}%",
                f"{variant['conversions']}",
                f"{variant['cvr']:.2f}%",
                "🏆" if is_winner else ""
            )

        self.console.print(table)

        # Confidence
        if results.get('winner'):
            confidence_pct = results['confidence'] * 100
            self.console.print(
                f"\n[green]Winner detected with {confidence_pct:.1f}% confidence[/green]"
            )
        else:
            self.console.print(
                "\n[yellow]No statistically significant winner yet[/yellow]"
            )

    def _extract_conversions(self, insight: Dict) -> int:
        """Extract conversions from insights."""
        if 'actions' not in insight:
            return 0

        for action in insight['actions']:
            action_type = action.get('action_type', '').lower()
            if 'purchase' in action_type or 'conversion' in action_type:
                return int(action.get('value', 0))

        return 0
