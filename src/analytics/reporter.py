"""Analytics and reporting module."""

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
