# Analytics and Reporting Guide

Comprehensive guide to tracking, analyzing, and reporting on Facebook ad campaign performance.

## Table of Contents

1. [Overview](#overview)
2. [Performance Metrics](#performance-metrics)
3. [Generating Reports](#generating-reports)
4. [Dashboard](#dashboard)
5. [Anomaly Detection](#anomaly-detection)
6. [Exporting Data](#exporting-data)
7. [Best Practices](#best-practices)

---

## Overview

The Analytics module provides powerful tools for tracking campaign performance, identifying trends, and making data-driven decisions.

### Key Features

- Real-time performance tracking
- Campaign and account-level reporting
- Customizable metrics
- Anomaly detection
- CSV export for further analysis
- Live dashboard

---

## Performance Metrics

### Standard Metrics

The following metrics are tracked automatically:

| Metric | Description | Formula |
|--------|-------------|---------|
| **Impressions** | Number of times ads were shown | - |
| **Clicks** | Number of clicks on ads | - |
| **Spend** | Total amount spent | - |
| **CTR** | Click-through rate | (Clicks / Impressions) × 100 |
| **CPC** | Cost per click | Spend / Clicks |
| **Conversions** | Number of conversion events | - |
| **CPA** | Cost per acquisition | Spend / Conversions |
| **ROAS** | Return on ad spend | Revenue / Spend |
| **Frequency** | Average times each person saw an ad | Impressions / Reach |
| **Reach** | Number of unique people who saw ads | - |

### Understanding ROAS

**ROAS (Return on Ad Spend)** is the most important metric for profitability:

- **ROAS < 1.0**: Losing money
- **ROAS = 1.0**: Breaking even
- **ROAS > 1.0**: Profitable
- **ROAS > 2.0**: Target for most campaigns
- **ROAS > 4.0**: Exceptional performance

Example:
```
Spend: $100
Revenue: $300
ROAS: 300 / 100 = 3.0x
```

For every $1 spent, you made $3 in revenue.

---

## Generating Reports

### CLI Reports

#### Account-Level Report

View all campaigns:

```bash
# Last 7 days (default)
python -m src.cli analytics report

# Last 30 days
python -m src.cli analytics report --days 30

# Export to CSV
python -m src.cli analytics report --days 30 --format csv
```

Output:
```
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━┓
┃ Campaign          ┃ Impress... ┃ Clicks┃ CTR   ┃ Spend  ┃ ROAS ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━┩
│ Q1 Lead Gen       │    45,230  │  892  │ 1.97% │ $234.50│ 2.8x │
│ Brand Awareness   │   102,445  │  512  │ 0.50% │ $156.20│ 1.2x │
│ Spring Sale       │    28,901  │  1023 │ 3.54% │ $445.80│ 4.2x │
└───────────────────┴────────────┴───────┴───────┴────────┴──────┘
```

#### Campaign-Specific Report

```bash
python -m src.cli analytics report \
  --campaign-id 123456789 \
  --days 30
```

### Python Reports

#### Account Report

```python
from src.api_client import FacebookAdsClient
from src.analytics.reporter import AnalyticsReporter

client = FacebookAdsClient()
reporter = AnalyticsReporter(client)

# Generate report
reports = reporter.account_report(days=7)

# Display in terminal
reporter.display_report(reports)

# Analyze data
for report in reports:
    campaign_name = report['campaign_name']
    roas = report['roas']
    spend = report['spend']

    if roas > 3.0:
        print(f"✓ {campaign_name}: Excellent ROAS ({roas:.2f}x)")
    elif roas < 1.5:
        print(f"✗ {campaign_name}: Low ROAS ({roas:.2f}x) - Review")
```

#### Campaign Report

```python
# Single campaign analysis
report = reporter.campaign_report(
    campaign_id="123456789",
    days=30
)

print(f"Campaign: {report['campaign_name']}")
print(f"Period: Last 30 days")
print(f"")
print(f"Performance:")
print(f"  Impressions: {report['impressions']:,}")
print(f"  Clicks: {report['clicks']:,}")
print(f"  CTR: {report['ctr']:.2f}%")
print(f"  Spend: ${report['spend']:.2f}")
print(f"  CPC: ${report['cpc']:.2f}")
print(f"  Conversions: {report['conversions']}")
print(f"  CPA: ${report['cost_per_conversion']:.2f}")
print(f"  ROAS: {report['roas']:.2f}x")
```

Output:
```
Campaign: Q1 Lead Generation
Period: Last 30 days

Performance:
  Impressions: 156,234
  Clicks: 3,456
  CTR: 2.21%
  Spend: $1,234.56
  CPC: $0.36
  Conversions: 89
  CPA: $13.88
  ROAS: 2.87x
```

#### Custom Date Ranges

```python
# Note: Use Facebook's date presets
# Available: 'today', 'yesterday', 'last_7d', 'last_14d', 'last_30d', 'last_90d', 'lifetime'

insights_7d = client.get_campaign_insights(
    campaign_id="123456789",
    date_preset="last_7d"
)

insights_30d = client.get_campaign_insights(
    campaign_id="123456789",
    date_preset="last_30d"
)

insights_lifetime = client.get_campaign_insights(
    campaign_id="123456789",
    date_preset="lifetime"
)
```

---

## Dashboard

### Live Dashboard

Display a live performance dashboard:

```bash
python -m src.cli analytics dashboard
```

Python:

```python
reporter.show_dashboard()
```

The dashboard shows:
- Active campaigns
- Real-time metrics (last 7 days)
- Status indicators
- ROAS color coding (green > 2.0, yellow 1.0-2.0, red < 1.0)

### Custom Dashboard

Build your own dashboard:

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout

console = Console()

# Get data
reports = reporter.account_report(days=7)

# Create layout
layout = Layout()
layout.split_column(
    Layout(name="header", size=3),
    Layout(name="body")
)

# Header
layout["header"].update(
    Panel("📊 My Custom Dashboard", style="bold blue")
)

# Performance table
table = Table(title="Top Performers")
table.add_column("Campaign")
table.add_column("ROAS", justify="right")
table.add_column("Spend", justify="right")

# Sort by ROAS
top_campaigns = sorted(reports, key=lambda x: x['roas'], reverse=True)[:5]

for campaign in top_campaigns:
    roas_color = "green" if campaign['roas'] >= 2.0 else "yellow"
    table.add_row(
        campaign['campaign_name'],
        f"[{roas_color}]{campaign['roas']:.2f}x[/{roas_color}]",
        f"${campaign['spend']:.2f}"
    )

layout["body"].update(table)
console.print(layout)
```

---

## Anomaly Detection

Automatically detect performance issues:

### CLI

```bash
# Anomaly detection is integrated into reports
python -m src.cli analytics report --campaign-id 123456789
```

### Python

```python
# Detect anomalies for a campaign
anomalies = reporter.detect_anomalies("123456789")

if anomalies:
    print(f"⚠ Found {len(anomalies)} anomalies:")
    for anomaly in anomalies:
        severity = anomaly['severity'].upper()
        message = anomaly['message']
        print(f"  [{severity}] {message}")
else:
    print("✓ No anomalies detected")
```

Example output:
```
⚠ Found 2 anomalies:
  [HIGH] ROAS (0.85) below threshold (1.5)
  [MEDIUM] CTR (0.32%) below threshold (0.5%)
```

### Configured Thresholds

Thresholds are set in `config/config.yaml`:

```yaml
optimization:
  min_roas: 1.5   # Minimum acceptable ROAS
  min_ctr: 0.5    # Minimum CTR (%)
  max_cpa: 50     # Maximum cost per acquisition
```

### Automated Alerts

Set up automated anomaly checking:

```python
from src.campaign.manager import CampaignManager

# Check all active campaigns
campaigns = manager.list_campaigns(status_filter="ACTIVE")

for campaign in campaigns:
    anomalies = reporter.detect_anomalies(campaign['id'])

    if anomalies:
        # High severity: pause campaign
        high_severity = [a for a in anomalies if a['severity'] == 'high']
        if high_severity:
            print(f"Pausing {campaign['name']} due to high severity issues")
            manager.pause_campaign(campaign['id'])

            # Send alert (integrate with your notification system)
            # send_email(f"Campaign {campaign['name']} paused", anomalies)

        # Medium severity: log warning
        else:
            print(f"⚠ Warning for {campaign['name']}")
            for anomaly in anomalies:
                print(f"  {anomaly['message']}")
```

---

## Exporting Data

### CSV Export

Export reports for external analysis:

```bash
# CLI
python -m src.cli analytics report --format csv --days 30
```

Python:

```python
# Generate and export report
reports = reporter.account_report(days=30)
filepath = reporter.export_csv(reports, filename="monthly_report.csv")

print(f"Report saved to: {filepath}")
```

Output location: `exports/fb_ads_report_YYYYMMDD_HHMMSS.csv`

### Custom Export

```python
import pandas as pd

# Get data
reports = reporter.account_report(days=30)

# Convert to DataFrame
df = pd.DataFrame(reports)

# Add calculated columns
df['roi'] = (df['roas'] - 1) * 100  # ROI percentage
df['profit'] = (df['roas'] * df['spend']) - df['spend']

# Sort by ROAS
df = df.sort_values('roas', ascending=False)

# Export with custom formatting
df.to_csv('custom_report.csv', index=False, float_format='%.2f')

# Or export to Excel
df.to_excel('custom_report.xlsx', index=False)
```

### JSON Export

```python
import json

reports = reporter.account_report(days=7)

# Save as JSON
with open('reports.json', 'w') as f:
    json.dump(reports, f, indent=2)
```

---

## Best Practices

### 1. Daily Performance Checks

Establish a daily routine:

```python
#!/usr/bin/env python3
"""Daily performance check script"""

from src.api_client import FacebookAdsClient
from src.analytics.reporter import AnalyticsReporter
from src.campaign.manager import CampaignManager

client = FacebookAdsClient()
reporter = AnalyticsReporter(client)
manager = CampaignManager(client)

# Get yesterday's performance
reports = reporter.account_report(days=1)

# Display summary
reporter.display_report(reports)

# Check for issues
total_spend = sum(r['spend'] for r in reports)
avg_roas = sum(r['roas'] for r in reports) / len(reports) if reports else 0

print(f"\nSummary:")
print(f"  Total Spend: ${total_spend:.2f}")
print(f"  Average ROAS: {avg_roas:.2f}x")

# Alert on low performers
low_performers = [r for r in reports if r['roas'] < 1.5 and r['spend'] > 50]

if low_performers:
    print(f"\n⚠ {len(low_performers)} campaigns need attention:")
    for report in low_performers:
        print(f"  - {report['campaign_name']}: ROAS {report['roas']:.2f}x")
```

### 2. Weekly Deep Dive

```python
# Weekly analysis script
reports = reporter.account_report(days=7)

# Export for review
filepath = reporter.export_csv(reports, filename="weekly_review.csv")

# Identify trends
for report in reports:
    # Get current week vs previous week
    current = reporter.campaign_report(report['campaign_id'], days=7)
    previous = reporter.campaign_report(report['campaign_id'], days=14)

    # Calculate trend (simplified)
    # Note: This is a basic example; you'd want more sophisticated trend analysis
    current_roas = current.get('roas', 0)
    # For accurate trend, you'd need day-by-day data

    print(f"{report['campaign_name']}:")
    print(f"  Current ROAS: {current_roas:.2f}x")
    print(f"  Spend: ${current.get('spend', 0):.2f}")
```

### 3. Compare Time Periods

```python
def compare_periods(campaign_id, days1=7, days2=14):
    """Compare two time periods for a campaign"""

    # Get data for both periods
    # Note: Facebook API limitations - this is simplified
    period1 = reporter.campaign_report(campaign_id, days=days1)
    period2 = reporter.campaign_report(campaign_id, days=days2)

    # Calculate changes
    metrics = ['impressions', 'clicks', 'spend', 'ctr', 'roas']

    print(f"Campaign Performance Comparison:")
    print(f"Period 1: Last {days1} days")
    print(f"Period 2: Last {days2} days")
    print()

    for metric in metrics:
        val1 = period1.get(metric, 0)
        val2 = period2.get(metric, 0)

        # Calculate percentage change
        if val2 > 0:
            change = ((val1 - val2) / val2) * 100
            direction = "↑" if change > 0 else "↓"
            print(f"{metric}: {val1:.2f} {direction} {abs(change):.1f}%")

# Usage
compare_periods("123456789", days1=7, days2=14)
```

### 4. Benchmark Against Goals

```python
# Define goals
GOALS = {
    'min_roas': 2.0,
    'max_cpa': 25.00,
    'min_ctr': 1.0
}

# Check campaigns against goals
reports = reporter.account_report(days=7)

for report in reports:
    campaign_name = report['campaign_name']
    meets_goals = True

    print(f"\n{campaign_name}:")

    # Check ROAS
    if report['roas'] < GOALS['min_roas']:
        print(f"  ✗ ROAS: {report['roas']:.2f}x (Goal: {GOALS['min_roas']}x)")
        meets_goals = False
    else:
        print(f"  ✓ ROAS: {report['roas']:.2f}x")

    # Check CPA
    if report['conversions'] > 0:
        if report['cost_per_conversion'] > GOALS['max_cpa']:
            print(f"  ✗ CPA: ${report['cost_per_conversion']:.2f} (Goal: ${GOALS['max_cpa']})")
            meets_goals = False
        else:
            print(f"  ✓ CPA: ${report['cost_per_conversion']:.2f}")

    # Check CTR
    if report['ctr'] < GOALS['min_ctr']:
        print(f"  ✗ CTR: {report['ctr']:.2f}% (Goal: {GOALS['min_ctr']}%)")
        meets_goals = False
    else:
        print(f"  ✓ CTR: {report['ctr']:.2f}%")

    if meets_goals:
        print(f"  🎯 All goals met!")
```

### 5. Cohort Analysis

Track campaign performance by launch date:

```python
from datetime import datetime

# Group campaigns by month
reports = reporter.account_report(days=90)

# Get full campaign details
campaigns = manager.list_campaigns()

# Create cohorts by month
cohorts = {}

for campaign in campaigns:
    created_time = campaign.get('created_time', '')
    if created_time:
        # Parse month
        month = created_time[:7]  # YYYY-MM

        if month not in cohorts:
            cohorts[month] = []

        # Find matching report
        report = next(
            (r for r in reports if r['campaign_id'] == campaign['id']),
            None
        )

        if report:
            cohorts[month].append(report)

# Analyze each cohort
for month, campaigns in sorted(cohorts.items()):
    total_spend = sum(c['spend'] for c in campaigns)
    avg_roas = sum(c['roas'] for c in campaigns) / len(campaigns)

    print(f"\n{month} Cohort ({len(campaigns)} campaigns):")
    print(f"  Total Spend: ${total_spend:.2f}")
    print(f"  Average ROAS: {avg_roas:.2f}x")
```

### 6. Attribution Analysis

Understand the customer journey:

```python
# Multi-touch attribution
# Note: This requires custom tracking implementation

def analyze_attribution(campaign_id):
    """Analyze conversion attribution"""

    insights = client.get_campaign_insights(
        campaign_id=campaign_id,
        date_preset="last_30d",
        fields=[
            'impressions',
            'clicks',
            'actions',
            'action_values'
        ]
    )

    if not insights:
        return

    insight = insights[0]

    # Extract conversion types
    if 'actions' in insight:
        print(f"Conversion Breakdown:")
        for action in insight['actions']:
            action_type = action.get('action_type', '')
            value = action.get('value', 0)
            print(f"  {action_type}: {value}")

# Usage
analyze_attribution("123456789")
```

---

## Advanced Analytics

### Correlation Analysis

Find relationships between metrics:

```python
import pandas as pd
import numpy as np

# Get data
reports = reporter.account_report(days=30)
df = pd.DataFrame(reports)

# Calculate correlations
correlations = df[['impressions', 'clicks', 'spend', 'ctr', 'roas']].corr()

print("Correlation Matrix:")
print(correlations)

# Find strong correlations
print("\nStrong correlations with ROAS:")
roas_corr = correlations['roas'].sort_values(ascending=False)
print(roas_corr)
```

### Spend Efficiency

```python
def calculate_efficiency_score(report):
    """Calculate overall efficiency score (0-100)"""

    # Weighted scoring
    weights = {
        'roas': 0.4,
        'ctr': 0.3,
        'cpa': 0.3
    }

    # Normalize metrics (example thresholds)
    roas_score = min(report['roas'] / 3.0, 1.0) * 100  # 3.0 ROAS = 100%
    ctr_score = min(report['ctr'] / 2.0, 1.0) * 100    # 2.0% CTR = 100%

    # Invert CPA (lower is better)
    target_cpa = 25
    if report['conversions'] > 0:
        cpa_score = max(0, (1 - report['cost_per_conversion'] / target_cpa)) * 100
    else:
        cpa_score = 0

    # Weighted average
    efficiency = (
        roas_score * weights['roas'] +
        ctr_score * weights['ctr'] +
        cpa_score * weights['cpa']
    )

    return efficiency

# Usage
reports = reporter.account_report(days=7)

for report in reports:
    score = calculate_efficiency_score(report)
    print(f"{report['campaign_name']}: Efficiency Score = {score:.1f}/100")
```

---

## Next Steps

- [Budget Optimization Guide](optimization.md) - Automate budget decisions
- [A/B Testing Guide](ab-testing.md) - Test and improve performance
- [Campaign Management Guide](campaign-management.md) - Campaign best practices
- [API Reference](api-reference.md) - Complete API documentation
