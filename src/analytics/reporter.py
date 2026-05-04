"""Analytics and reporting module."""

import json
from typing import Dict, List, Optional, Union
import pandas as pd
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from loguru import logger
import csv
from pathlib import Path


class AnalyticsReporter:
    """Generates analytics reports and dashboards."""

    def __init__(self, api_client):
        """Initialize analytics reporter.

        Args:
            api_client: FacebookAdsClient instance
        """
        self.client = api_client
        self.config = api_client.config
        self.console = Console()

    def campaign_report(
        self,
        campaign_id: str,
        days: int = 7
    ) -> Dict:
        """Generate performance report for a campaign.

        Args:
            campaign_id: Campaign ID
            days: Number of days to analyze

        Returns:
            Report data
        """
        date_preset = self._days_to_preset(days)
        insights = self.client.get_campaign_insights(campaign_id, date_preset=date_preset)

        if not insights:
            return {'error': 'No data available'}

        # Get campaign details
        campaigns = self.client.get_campaigns()
        campaign = next((c for c in campaigns if c['id'] == campaign_id), {})

        return self._format_insights(insights[0], campaign)

    def account_report(self, days: int = 7) -> List[Dict]:
        """Generate account-level performance report.

        Args:
            days: Number of days to analyze

        Returns:
            List of campaign reports
        """
        date_preset = self._days_to_preset(days)
        insights = self.client.get_account_insights(
            date_preset=date_preset,
            level='campaign'
        )

        return [self._format_insights(insight) for insight in insights]

    def _format_insights(self, insight: Dict, campaign: Optional[Dict] = None) -> Dict:
        """Format insights data for display.

        Args:
            insight: Raw insights data
            campaign: Campaign metadata

        Returns:
            Formatted report data
        """
        # Extract metrics with safe defaults
        impressions = int(insight.get('impressions', 0))
        clicks = int(insight.get('clicks', 0))
        spend = float(insight.get('spend', 0))

        # Calculate derived metrics
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cpc = (spend / clicks) if clicks > 0 else 0

        # Extract conversions
        conversions = 0
        cost_per_conversion = 0
        if 'actions' in insight:
            for action in insight['actions']:
                if 'purchase' in action.get('action_type', '').lower():
                    conversions = int(action.get('value', 0))
                    break

        if conversions > 0:
            cost_per_conversion = spend / conversions

        # Calculate ROAS
        revenue = conversions * self.config.get('analytics', {}).get('avg_order_value', 50)
        roas = (revenue / spend) if spend > 0 else 0

        formatted = {
            'campaign_id': insight.get('campaign_id', 'N/A'),
            'campaign_name': insight.get('campaign_name', campaign.get('name') if campaign else 'N/A'),
            'impressions': impressions,
            'clicks': clicks,
            'spend': spend,
            'ctr': ctr,
            'cpc': cpc,
            'conversions': conversions,
            'cost_per_conversion': cost_per_conversion,
            'roas': roas,
            'frequency': float(insight.get('frequency', 0)),
            'reach': int(insight.get('reach', 0))
        }

        return formatted

    def display_report(self, data: Union[Dict, List[Dict]]):
        """Display report in terminal.

        Args:
            data: Report data (single campaign or list)
        """
        if isinstance(data, dict):
            data = [data]

        table = Table(title="Campaign Performance Report")
        table.add_column("Campaign", style="cyan")
        table.add_column("Impressions", justify="right")
        table.add_column("Clicks", justify="right")
        table.add_column("CTR", justify="right")
        table.add_column("Spend", justify="right", style="yellow")
        table.add_column("CPC", justify="right")
        table.add_column("Conv.", justify="right")
        table.add_column("CPA", justify="right")
        table.add_column("ROAS", justify="right", style="green")

        for item in data:
            table.add_row(
                item['campaign_name'][:30],
                f"{item['impressions']:,}",
                f"{item['clicks']:,}",
                f"{item['ctr']:.2f}%",
                f"${item['spend']:.2f}",
                f"${item['cpc']:.2f}",
                f"{item['conversions']}",
                f"${item['cost_per_conversion']:.2f}" if item['conversions'] > 0 else "N/A",
                f"{item['roas']:.2f}x" if item['roas'] > 0 else "N/A"
            )

        self.console.print(table)

        # Summary stats
        if len(data) > 1:
            total_spend = sum(d['spend'] for d in data)
            total_conversions = sum(d['conversions'] for d in data)
            avg_roas = sum(d['roas'] for d in data) / len(data)

            summary = Panel(
                f"Total Spend: ${total_spend:.2f} | "
                f"Total Conversions: {total_conversions} | "
                f"Average ROAS: {avg_roas:.2f}x",
                title="Summary"
            )
            self.console.print(summary)

    def show_dashboard(self):
        """Display live performance dashboard."""
        from rich.live import Live
        from rich.layout import Layout

        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )

        # Get data
        report_data = self.account_report(days=7)

        # Header
        layout["header"].update(
            Panel(
                f"Facebook Ads Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                style="bold blue"
            )
        )

        # Body - performance table
        table = Table(title="Active Campaigns (Last 7 Days)")
        table.add_column("Campaign")
        table.add_column("Status")
        table.add_column("Spend", justify="right")
        table.add_column("ROAS", justify="right")
        table.add_column("Conv.", justify="right")

        for item in report_data:
            status_color = "green" if item.get('status') == 'ACTIVE' else "yellow"
            roas_color = "green" if item['roas'] >= 2.0 else "red" if item['roas'] < 1.0 else "yellow"

            table.add_row(
                item['campaign_name'],
                f"[{status_color}]{item.get('status', 'N/A')}[/{status_color}]",
                f"${item['spend']:.2f}",
                f"[{roas_color}]{item['roas']:.2f}x[/{roas_color}]",
                str(item['conversions'])
            )

        layout["body"].update(table)

        self.console.print(layout)

    def export_csv(self, data: Union[Dict, List[Dict]], filename: Optional[str] = None) -> str:
        """Export report data to CSV.

        Args:
            data: Report data
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to exported file
        """
        if isinstance(data, dict):
            data = [data]

        # Create exports directory
        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)

        # Generate filename
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fb_ads_report_{timestamp}.csv"

        filepath = exports_dir / filename

        # Write CSV
        if data:
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            logger.info(f"Exported report to {filepath}")

        return str(filepath)

    def _days_to_preset(self, days: int) -> str:
        """Convert days to Facebook date preset.

        Args:
            days: Number of days

        Returns:
            Date preset string
        """
        presets = {
            1: 'today',
            7: 'last_7d',
            14: 'last_14d',
            30: 'last_30d',
            90: 'last_90d'
        }
        return presets.get(days, 'last_7d')

    # ── Hormozi Creative Performance Tracker (Phase 4.3) ──────────────────────

    def get_creative_performance(
        self,
        campaign_id: str,
        days: int = 7,
        target_cpt_usd: Optional[float] = None,
    ) -> Dict:
        """Pull ad-level performance and classify each creative against kill criteria.

        Requires the campaign to have been created via create_hormozi_testing_campaign()
        so the angle/hook mapping file exists in campaign_mappings/{campaign_id}.json.

        Metrics returned per creative:
          - hook_rate: 3-second video views / impressions (stop-scroll signal)
          - hold_rate: 15-second video views / 3-second video views (body retention)
          - ctr: link clicks / impressions × 100
          - cpt: spend / trial_start events (cost per trial)
          - cpa: spend / all conversions
          - frequency: avg times same user saw this ad
          - verdict: winner | gray_zone | kill | fatigued | insufficient_data

        Kill rules (from Phase 6 plan):
          - hook_rate < 0.25 → kill (scroll-stop failure)
          - spent ≥ 3× target_cpt with 0 conversions → kill (structural failure)
          - cpt > 2× target_cpt by day 10 → kill
          - frequency > 3.0 AND ctr dropped > 30% from peak → fatigued (creative refresh)
          - cpt ≤ target_cpt for 5+ days, hook_rate ≥ 0.30 → winner

        Args:
            campaign_id: Testing campaign ID
            days: Lookback window (use 7 for weekly review)
            target_cpt_usd: Your target cost-per-trial. Required for kill/winner verdicts.

        Returns:
            {ads: [ranked list with verdicts], summary, winners, kills, gray_zone, fatigued}
        """
        from facebook_business.adobjects.ad import Ad as FBAd

        # Load angle/hook mapping
        mapping_path = Path("campaign_mappings") / f"{campaign_id}.json"
        angle_map: Dict[str, Dict] = {}
        if mapping_path.exists():
            with open(mapping_path) as f:
                mapping_data = json.load(f)
            for adset in mapping_data.get('adsets', []):
                if adset.get('ad_id'):
                    angle_map[adset['ad_id']] = adset

        # Get all ads in the campaign
        adsets = self.client.get_adsets(campaign_id=campaign_id)
        ads_data = []

        for adset in adsets:
            adset_id = adset['id']
            ads = self.client.get_ads(adset_id=adset_id)

            for ad in ads:
                ad_id = ad['id']
                try:
                    fb_ad = FBAd(ad_id)
                    date_preset = self._days_to_preset(days)

                    # Request video-specific fields for Hook/Hold Rate alongside standard metrics
                    insights = fb_ad.get_insights(
                        fields=[
                            'spend', 'impressions', 'clicks', 'ctr', 'frequency',
                            'actions',
                            'video_3_sec_watched_actions',   # Hook Rate numerator
                            'video_15_sec_watched_actions',  # Hold Rate numerator
                            'video_30_sec_watched_actions',
                        ],
                        params={'date_preset': date_preset}
                    )

                    if not insights:
                        continue

                    insight = dict(insights[0])
                    spend = float(insight.get('spend', 0))
                    impressions = int(insight.get('impressions', 0))
                    clicks = int(insight.get('clicks', 0))
                    frequency = float(insight.get('frequency', 0))

                    if impressions == 0:
                        continue

                    # Hook Rate: % who watched ≥3 seconds (stop-scroll signal)
                    three_sec = self._extract_video_action(
                        insight.get('video_3_sec_watched_actions', [])
                    )
                    fifteen_sec = self._extract_video_action(
                        insight.get('video_15_sec_watched_actions', [])
                    )
                    hook_rate = (three_sec / impressions) if impressions > 0 else 0
                    hold_rate = (fifteen_sec / three_sec) if three_sec > 0 else 0

                    ctr = (clicks / impressions) if impressions > 0 else 0

                    # Extract trial and conversion events
                    trial_events = self._extract_action_by_type(
                        insight.get('actions', []),
                        ['start_trial', 'StartTrial']
                    )
                    conversions = self._extract_action_by_type(
                        insight.get('actions', []),
                        ['purchase', 'subscribe', 'complete_registration',
                         'offsite_conversion.fb_pixel_purchase']
                    )

                    cpt = (spend / trial_events) if trial_events > 0 else None
                    cpa = (spend / conversions) if conversions > 0 else None

                    # Join with angle/hook data
                    meta = angle_map.get(ad_id, {})

                    record = {
                        'ad_id': ad_id,
                        'adset_id': adset_id,
                        'ad_name': ad.get('name', ''),
                        'angle_id': meta.get('angle_id'),
                        'hook_id': meta.get('hook_id'),
                        'angle_name': meta.get('angle_name', 'Unknown'),
                        'hook_format': meta.get('hook_format', 'Unknown'),
                        'hook_opening': meta.get('hook_opening', ''),
                        'spend': round(spend, 2),
                        'impressions': impressions,
                        'clicks': clicks,
                        'ctr_pct': round(ctr * 100, 2),
                        'hook_rate_pct': round(hook_rate * 100, 2),
                        'hold_rate_pct': round(hold_rate * 100, 2),
                        'trial_events': trial_events,
                        'conversions': conversions,
                        'cpt': round(cpt, 2) if cpt else None,
                        'cpa': round(cpa, 2) if cpa else None,
                        'frequency': round(frequency, 2),
                    }

                    # Apply verdict
                    record['verdict'] = self._classify_creative(
                        record, target_cpt_usd, days
                    )
                    ads_data.append(record)

                except Exception as e:
                    logger.warning(f"Could not fetch insights for ad {ad_id}: {e}")

        if not ads_data:
            return {'ads': [], 'summary': 'No data available', 'winners': [],
                    'kills': [], 'gray_zone': [], 'fatigued': []}

        # Sort by CPT ascending (nulls last), then hook_rate descending
        ads_data.sort(key=lambda x: (x['cpt'] is None, x['cpt'] or 999, -x['hook_rate_pct']))

        winners = [a for a in ads_data if a['verdict'] == 'winner']
        kills = [a for a in ads_data if a['verdict'] == 'kill']
        gray_zone = [a for a in ads_data if a['verdict'] == 'gray_zone']
        fatigued = [a for a in ads_data if a['verdict'] == 'fatigued']

        return {
            'campaign_id': campaign_id,
            'days': days,
            'target_cpt_usd': target_cpt_usd,
            'ads': ads_data,
            'summary': (
                f"{len(ads_data)} ads tracked | "
                f"{len(winners)} winners | {len(kills)} kills | "
                f"{len(gray_zone)} gray zone | {len(fatigued)} fatigued"
            ),
            'winners': winners,
            'kills': kills,
            'gray_zone': gray_zone,
            'fatigued': fatigued,
        }

    def _classify_creative(
        self,
        record: Dict,
        target_cpt: Optional[float],
        days: int
    ) -> str:
        """Apply Phase 6 kill/winner rules to a single creative's data."""
        spend = record['spend']
        hook_rate = record['hook_rate_pct'] / 100
        frequency = record['frequency']
        ctr = record['ctr_pct'] / 100
        cpt = record['cpt']
        conversions = record['conversions']

        # Insufficient data — too early to judge
        if spend < 10 or record['impressions'] < 500:
            return 'insufficient_data'

        # Hard kill: Hook Rate below floor (scroll-stop failure regardless of spend)
        if hook_rate < 0.25 and spend > 20:
            return 'kill'

        if target_cpt:
            # Hard kill: 3× CPT spent with zero conversions (structural failure)
            if spend >= target_cpt * 3 and conversions == 0:
                return 'kill'

            # Kill by day 10: CPT > 2× target with no downward trend
            if days >= 10 and cpt and cpt > target_cpt * 2:
                return 'kill'

            # Winner: CPT at or below target, Hook Rate strong
            if cpt and cpt <= target_cpt and hook_rate >= 0.30:
                return 'winner'

            # Gray zone: CPT up to 30% above target — give more time
            if cpt and cpt <= target_cpt * 1.3:
                return 'gray_zone'

        # Fatigued: high frequency but degrading engagement
        if frequency > 3.0 and ctr < 0.005:
            return 'fatigued'

        return 'gray_zone'

    def _extract_video_action(self, actions: List) -> int:
        """Extract count from a video action list (Meta returns [{action_type, value}])."""
        if not actions:
            return 0
        for action in actions:
            if isinstance(action, dict):
                return int(action.get('value', 0))
        return 0

    def _extract_action_by_type(self, actions: List, types: List[str]) -> int:
        """Sum action values matching any of the given action_type strings."""
        total = 0
        for action in actions:
            if isinstance(action, dict):
                action_type = action.get('action_type', '').lower()
                if any(t.lower() in action_type for t in types):
                    total += int(action.get('value', 0))
        return total

    def detect_anomalies(self, campaign_id: str) -> List[Dict]:
        """Detect performance anomalies.

        Args:
            campaign_id: Campaign ID

        Returns:
            List of detected anomalies
        """
        # Get last 30 days of data
        insights = self.client.get_campaign_insights(campaign_id, date_preset='last_30d')

        if not insights:
            return []

        formatted = self._format_insights(insights[0])
        anomalies = []

        # Check against thresholds
        thresholds = self.config.get('optimization', {})

        if formatted['roas'] < thresholds.get('min_roas', 1.5):
            anomalies.append({
                'type': 'low_roas',
                'severity': 'high',
                'metric': 'roas',
                'value': formatted['roas'],
                'threshold': thresholds['min_roas'],
                'message': f"ROAS ({formatted['roas']:.2f}) below threshold ({thresholds['min_roas']})"
            })

        if formatted['ctr'] < thresholds.get('min_ctr', 0.5):
            anomalies.append({
                'type': 'low_ctr',
                'severity': 'medium',
                'metric': 'ctr',
                'value': formatted['ctr'],
                'threshold': thresholds['min_ctr'],
                'message': f"CTR ({formatted['ctr']:.2f}%) below threshold ({thresholds['min_ctr']}%)"
            })

        if formatted['cost_per_conversion'] > thresholds.get('max_cpa', 50):
            anomalies.append({
                'type': 'high_cpa',
                'severity': 'high',
                'metric': 'cost_per_conversion',
                'value': formatted['cost_per_conversion'],
                'threshold': thresholds['max_cpa'],
                'message': f"CPA (${formatted['cost_per_conversion']:.2f}) above threshold (${thresholds['max_cpa']})"
            })

        return anomalies
