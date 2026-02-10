# Step-by-Step Tutorials

Practical tutorials for common Facebook Ads Manager workflows.

## Table of Contents

1. [Tutorial 1: Your First Campaign](#tutorial-1-your-first-campaign)
2. [Tutorial 2: Performance Analysis](#tutorial-2-performance-analysis)
3. [Tutorial 3: Budget Optimization](#tutorial-3-budget-optimization)
4. [Tutorial 4: A/B Testing](#tutorial-4-ab-testing)
5. [Tutorial 5: Automated Monitoring](#tutorial-5-automated-monitoring)
6. [Tutorial 6: Scaling a Winner](#tutorial-6-scaling-a-winner)

---

## Tutorial 1: Your First Campaign

**Goal**: Create and launch a simple lead generation campaign

**Time**: 15 minutes

### Step 1: Setup and Validation

First, ensure your credentials are configured:

```bash
# Validate API credentials
python -m src.cli validate
```

Expected output:
```
✓ Credentials validated successfully

Account: Your Business Name
ID: act_123456789
Currency: USD
Status: 1
```

### Step 2: Create a Campaign

```bash
python -m src.cli campaign create \
  --name "Lead Gen - Tutorial Campaign" \
  --objective CONVERSIONS \
  --budget 50 \
  --status PAUSED
```

Output:
```
✓ Campaign created: Lead Gen - Tutorial Campaign (ID: 123456789012345)
```

**Save the campaign ID** - you'll need it for the next steps.

### Step 3: Verify Campaign Creation

```bash
python -m src.cli campaign list
```

You should see your campaign in the list:
```
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┓
┃ ID              ┃ Name                       ┃ Objective ┃ Status ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━┩
│ 123456789012345 │ Lead Gen - Tutorial...     │ CONVER... │ PAUSED │
└─────────────────┴────────────────────────────┴───────────┴────────┘
```

### Step 4: Configure the Campaign (Facebook Ads Manager)

The campaign is created but paused. Now configure it in Facebook Ads Manager:

1. Go to https://business.facebook.com/adsmanager
2. Find your campaign: "Lead Gen - Tutorial Campaign"
3. Add an ad set with:
   - Targeting: United States, Ages 25-65
   - Budget: $50/day
   - Optimization: Conversions
4. Add an ad with image/video creative
5. Review settings

### Step 5: Activate the Campaign

```bash
python -m src.cli campaign activate --id 123456789012345
```

Output:
```
✓ Campaign 123456789012345 activated
```

Your campaign is now running!

### Step 6: Monitor Initial Performance

Wait 24 hours, then check performance:

```bash
python -m src.cli analytics report --campaign-id 123456789012345 --days 1
```

**Congratulations!** You've created and launched your first campaign.

---

## Tutorial 2: Performance Analysis

**Goal**: Analyze campaign performance and identify issues

**Time**: 20 minutes

**Prerequisites**: At least one active campaign with 3+ days of data

### Step 1: Account Overview

Get an overview of all campaigns:

```bash
python -m src.cli analytics report --days 7
```

This shows all campaigns' performance for the last 7 days.

### Step 2: Campaign Deep Dive

Choose a campaign to analyze:

```bash
python -m src.cli analytics report \
  --campaign-id 123456789012345 \
  --days 30
```

### Step 3: Identify Issues with Python

Create a script to analyze performance:

```python
# analyze_campaigns.py

from src.api_client import FacebookAdsClient
from src.analytics.reporter import AnalyticsReporter

client = FacebookAdsClient()
reporter = AnalyticsReporter(client)

# Get all campaigns
reports = reporter.account_report(days=7)

# Define thresholds
GOOD_ROAS = 2.5
MIN_ROAS = 1.5
MIN_CTR = 0.5

# Categorize campaigns
excellent = []
good = []
needs_work = []
failing = []

for report in reports:
    campaign_name = report['campaign_name']
    roas = report['roas']
    ctr = report['ctr']
    spend = report['spend']

    if roas >= GOOD_ROAS:
        excellent.append(report)
    elif roas >= MIN_ROAS:
        good.append(report)
    elif roas >= 1.0:
        needs_work.append(report)
    else:
        failing.append(report)

# Print results
print(f"\n{'='*60}")
print("CAMPAIGN PERFORMANCE ANALYSIS")
print(f"{'='*60}\n")

print(f"🏆 EXCELLENT (ROAS ≥ {GOOD_ROAS}x): {len(excellent)} campaigns")
for r in excellent:
    print(f"  ✓ {r['campaign_name']}: ROAS {r['roas']:.2f}x, Spend ${r['spend']:.2f}")

print(f"\n✓ GOOD (ROAS ≥ {MIN_ROAS}x): {len(good)} campaigns")
for r in good:
    print(f"  • {r['campaign_name']}: ROAS {r['roas']:.2f}x, Spend ${r['spend']:.2f}")

print(f"\n⚠ NEEDS WORK (ROAS 1.0-{MIN_ROAS}x): {len(needs_work)} campaigns")
for r in needs_work:
    print(f"  • {r['campaign_name']}: ROAS {r['roas']:.2f}x, Spend ${r['spend']:.2f}")

print(f"\n✗ FAILING (ROAS < 1.0): {len(failing)} campaigns")
for r in failing:
    print(f"  • {r['campaign_name']}: ROAS {r['roas']:.2f}x, Spend ${r['spend']:.2f}")

# Recommendations
print(f"\n{'='*60}")
print("RECOMMENDATIONS")
print(f"{'='*60}\n")

if excellent:
    print("🚀 SCALE: Increase budgets on excellent performers")
    for r in excellent[:3]:  # Top 3
        print(f"  → {r['campaign_name']}: Consider increasing to ${r['spend'] * 1.5:.2f}/day")

if failing and any(r['spend'] > 50 for r in failing):
    print("\n⏸ PAUSE: Stop campaigns that are losing money")
    for r in failing:
        if r['spend'] > 50:
            print(f"  → {r['campaign_name']}: Pause and review creative/targeting")

if needs_work:
    print("\n🔧 OPTIMIZE: Improve underperforming campaigns")
    for r in needs_work:
        print(f"  → {r['campaign_name']}: Review targeting, test new creative")
```

Run the script:

```bash
python analyze_campaigns.py
```

### Step 4: Export Data for Further Analysis

```bash
# Export to CSV
python -m src.cli analytics report --days 30 --format csv
```

This creates a CSV file in `exports/` that you can open in Excel or Google Sheets.

### Step 5: Check for Anomalies

```python
# check_anomalies.py

from src.api_client import FacebookAdsClient
from src.analytics.reporter import AnalyticsReporter
from src.campaign.manager import CampaignManager

client = FacebookAdsClient()
reporter = AnalyticsReporter(client)
manager = CampaignManager(client)

# Get active campaigns
campaigns = manager.list_campaigns(status_filter="ACTIVE")

print("ANOMALY DETECTION REPORT\n")

for campaign in campaigns:
    anomalies = reporter.detect_anomalies(campaign['id'])

    if anomalies:
        print(f"\n⚠ {campaign['name']}:")
        for anomaly in anomalies:
            severity = anomaly['severity'].upper()
            print(f"  [{severity}] {anomaly['message']}")

        # Auto-pause if critical
        critical = [a for a in anomalies if a['severity'] == 'high']
        if len(critical) >= 2:
            print(f"  → RECOMMENDATION: Pause this campaign")
            # Uncomment to auto-pause:
            # manager.pause_campaign(campaign['id'])
```

Run:

```bash
python check_anomalies.py
```

**Next Steps**: Use insights from this analysis to optimize budgets (Tutorial 3)

---

## Tutorial 3: Budget Optimization

**Goal**: Automatically optimize campaign budgets based on performance

**Time**: 15 minutes

**Prerequisites**: At least 3 active campaigns with 7+ days of data

### Step 1: Preview Optimization

Always start with a dry run:

```bash
python -m src.cli optimize budgets --min-roas 2.0 --dry-run
```

Output shows proposed changes:
```
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Campaign         ┃ Current Budget ┃ New Budget  ┃ Change ┃ Reason          ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ Campaign A       │ $100.00        │ $120.00     │ +20.0% │ High ROAS (4.2x)│
│ Campaign B       │ $75.00         │ $82.50      │ +10.0% │ Good ROAS (2.8x)│
│ Campaign C       │ $50.00         │ $35.00      │ -30.0% │ Low ROAS (0.9x) │
└──────────────────┴────────────────┴─────────────┴────────┴─────────────────┘
```

### Step 2: Review Changes

**Questions to ask:**
- Are the changes reasonable?
- Do I agree with scaling/reducing each campaign?
- Is the ROAS threshold appropriate for my business?

### Step 3: Apply Optimization

If changes look good:

```bash
python -m src.cli optimize budgets --min-roas 2.0 --no-dry-run
```

The budgets are now updated!

### Step 4: Verify Changes

```bash
python -m src.cli campaign list
```

Check that budgets were updated correctly.

### Step 5: Pause Underperformers

```bash
# Preview
python -m src.cli optimize pause-underperformers \
  --threshold 0.5 \
  --min-spend 100 \
  --dry-run

# Apply
python -m src.cli optimize pause-underperformers \
  --threshold 0.5 \
  --min-spend 100 \
  --no-dry-run
```

This pauses campaigns with:
- CTR < 0.5%
- Spend > $100

### Step 6: Create Daily Optimization Script

Automate optimization:

```python
#!/usr/bin/env python3
# scripts/daily_optimization.py

from datetime import datetime
from src.api_client import FacebookAdsClient
from src.optimization.optimizer import BudgetOptimizer
from src.analytics.reporter import AnalyticsReporter

def main():
    print(f"\n{'='*60}")
    print(f"DAILY OPTIMIZATION - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    client = FacebookAdsClient()
    optimizer = BudgetOptimizer(client)
    reporter = AnalyticsReporter(client)

    # 1. Optimize budgets
    print("1. Optimizing budgets...")
    changes = optimizer.optimize_budgets(min_roas=2.0, dry_run=False)
    print(f"   ✓ Adjusted {len(changes)} campaign budgets\n")

    # 2. Pause underperformers
    print("2. Checking for underperformers...")
    paused = optimizer.pause_underperformers(
        min_ctr=0.5,
        min_spend=100,
        dry_run=False
    )
    print(f"   ✓ Paused {len(paused)} campaigns\n")

    # 3. Generate report
    print("3. Generating performance report...")
    reports = reporter.account_report(days=1)
    filepath = reporter.export_csv(reports, filename=f"daily_report_{datetime.now().strftime('%Y%m%d')}.csv")
    print(f"   ✓ Report saved to {filepath}\n")

    # Summary
    total_spend = sum(r['spend'] for r in reports)
    avg_roas = sum(r['roas'] for r in reports) / len(reports) if reports else 0

    print(f"{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total Spend (yesterday): ${total_spend:.2f}")
    print(f"Average ROAS: {avg_roas:.2f}x")
    print(f"Budget changes: {len(changes)}")
    print(f"Campaigns paused: {len(paused)}")
    print()

if __name__ == '__main__':
    main()
```

### Step 7: Schedule Daily Run

Add to crontab:

```bash
# Run every day at 9 AM
crontab -e

# Add this line:
0 9 * * * cd /path/to/facebook-ads-manager && /path/to/venv/bin/python scripts/daily_optimization.py >> logs/optimization.log 2>&1
```

**Done!** Your campaigns are now automatically optimized daily.

---

## Tutorial 4: A/B Testing

**Goal**: Test different ad creatives to find the best performer

**Time**: 30 minutes (+ 7 days wait time)

### Step 1: Create Base Campaign

```bash
python -m src.cli campaign create \
  --name "AB Test Base - Product Launch" \
  --objective CONVERSIONS \
  --budget 100 \
  --status PAUSED
```

Save the campaign ID (e.g., `123456789012345`)

### Step 2: Create A/B Test

```bash
python -m src.cli test create \
  --campaign-id 123456789012345 \
  --variants 3 \
  --name "Creative Test - March 2026"
```

This creates 3 variant campaigns, each with $33.33/day budget.

### Step 3: Configure Variants

Go to Facebook Ads Manager and add different creative to each variant:

**Variant 1**: Static image ad
- Upload image: `product_image.jpg`
- Headline: "Introducing Our New Product"
- Description: "Limited time offer - 50% off"

**Variant 2**: Video ad
- Upload video: `product_video.mp4` (15 seconds)
- Same headline and description

**Variant 3**: Carousel ad
- Upload 3-5 images showing product features
- Same headline and description

**Important**: Keep targeting, budget, and all other settings identical!

### Step 4: Activate Variants

```python
# activate_test.py

from src.api_client import FacebookAdsClient
from src.campaign.manager import CampaignManager

client = FacebookAdsClient()
manager = CampaignManager(client)

# Your variant IDs (from test creation output)
variant_ids = [
    "123456789012346",  # Variant 1
    "123456789012347",  # Variant 2
    "123456789012348",  # Variant 3
]

for variant_id in variant_ids:
    manager.activate_campaign(variant_id)
    print(f"✓ Activated variant {variant_id}")

print("\n✓ Test is now running!")
print("Wait 7 days, then analyze results.")
```

### Step 5: Monitor Progress (Day 3)

Mid-test check:

```bash
python -m src.cli test analyze --test-id test_123456789012345_3
```

Output:
```
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━┳━━━━━━┓
┃ Variant           ┃ Impressions┃ Clicks ┃ CTR  ┃ Conversions┃ CVR  ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━╇━━━━━━┩
│ Image - Variant 1 │   15,230   │  412   │2.70% │     45     │10.9% │
│ Video - Variant 2 │   16,102   │  567   │3.52% │     62     │10.9% │
│ Carousel - Var 3  │   14,891   │  389   │2.61% │     38     │ 9.8% │
└───────────────────┴────────────┴────────┴──────┴────────────┴──────┘

No statistically significant winner yet
Continue running the test
```

### Step 6: Analyze Results (Day 7)

```bash
python -m src.cli test analyze --test-id test_123456789012345_3
```

Output:
```
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━┓
┃ Variant           ┃ Impressions┃ Clicks ┃ CTR  ┃ Conversions┃ CVR  ┃ Winner ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━┩
│ Image - Variant 1 │   45,230   │ 1,234  │2.73% │    156     │12.6% │        │
│ Video - Variant 2 │   46,102   │ 1,567  │3.40% │    203     │13.0% │   🏆   │
│ Carousel - Var 3  │   44,891   │ 1,156  │2.58% │    142     │12.3% │        │
└───────────────────┴────────────┴────────┴──────┴────────────┴──────┴────────┘

Winner detected with 96.2% confidence
```

**Winner: Video ad!**

### Step 7: Implement Winner

```python
# implement_winner.py

from src.api_client import FacebookAdsClient
from src.campaign.manager import CampaignManager
from src.optimization.ab_testing import ABTestManager

client = FacebookAdsClient()
manager = CampaignManager(client)
ab_test = ABTestManager(client)

# Analyze test
results = ab_test.analyze_test("test_123456789012345_3")

if results['winner']:
    winner_id = results['winner']

    # Scale winner to full budget
    manager.update_budget(winner_id, new_budget=100.00)
    print(f"✓ Scaled winner to $100/day")

    # Pause losers
    for variant in results['variants']:
        if variant['id'] != winner_id:
            manager.pause_campaign(variant['id'])
            print(f"✓ Paused {variant['name']}")

    print(f"\n✓ Test complete! Video ad is the winner.")
    print(f"Use video creative for future campaigns.")
else:
    print("No winner yet - continue testing")
```

**Key Takeaway**: Video ads performed 3.40% CTR vs 2.73% for images in this test.

---

## Tutorial 5: Automated Monitoring

**Goal**: Set up automated monitoring and alerts

**Time**: 25 minutes

### Step 1: Create Monitoring Script

```python
#!/usr/bin/env python3
# scripts/monitor_campaigns.py

"""
Automated campaign monitoring with Slack/email alerts
"""

from datetime import datetime
from src.api_client import FacebookAdsClient
from src.analytics.reporter import AnalyticsReporter
from src.campaign.manager import CampaignManager

# Configuration
ALERT_THRESHOLDS = {
    'min_roas': 1.5,
    'max_cpa': 50,
    'min_ctr': 0.5,
    'min_spend_to_evaluate': 100
}

def send_alert(message):
    """Send alert (implement with your preferred method)"""
    # Example: Slack webhook
    # import requests
    # requests.post(SLACK_WEBHOOK_URL, json={'text': message})

    # For now, just print
    print(f"🚨 ALERT: {message}")

def monitor_campaigns():
    client = FacebookAdsClient()
    reporter = AnalyticsReporter(client)
    manager = CampaignManager(client)

    print(f"\n{'='*60}")
    print(f"CAMPAIGN MONITORING - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    # Get active campaigns
    campaigns = manager.list_campaigns(
        status_filter="ACTIVE",
        include_insights=True
    )

    alerts = []

    for campaign in campaigns:
        insights = campaign.get('insights', {})
        spend = insights.get('spend', 0)

        # Skip campaigns without enough data
        if spend < ALERT_THRESHOLDS['min_spend_to_evaluate']:
            continue

        campaign_name = campaign['name']
        roas = insights.get('roas', 0)
        ctr = insights.get('ctr', 0)
        cpa = insights.get('cost_per_conversion', 0)

        # Check thresholds
        issues = []

        if roas < ALERT_THRESHOLDS['min_roas']:
            issues.append(f"Low ROAS: {roas:.2f}x (threshold: {ALERT_THRESHOLDS['min_roas']}x)")

        if ctr < ALERT_THRESHOLDS['min_ctr']:
            issues.append(f"Low CTR: {ctr:.2f}% (threshold: {ALERT_THRESHOLDS['min_ctr']}%)")

        if insights.get('conversions', 0) > 0 and cpa > ALERT_THRESHOLDS['max_cpa']:
            issues.append(f"High CPA: ${cpa:.2f} (threshold: ${ALERT_THRESHOLDS['max_cpa']})")

        if issues:
            alert_msg = f"{campaign_name}:\n" + "\n".join(f"  - {issue}" for issue in issues)
            alerts.append(alert_msg)
            send_alert(alert_msg)

            # Auto-pause if multiple critical issues
            if len(issues) >= 2:
                manager.pause_campaign(campaign['id'])
                print(f"⏸ Auto-paused {campaign_name} due to multiple issues")

    # Summary
    print(f"\n{'='*60}")
    print(f"MONITORING SUMMARY")
    print(f"{'='*60}")
    print(f"Campaigns monitored: {len(campaigns)}")
    print(f"Alerts triggered: {len(alerts)}")

    if not alerts:
        print("✓ All campaigns performing well!")

if __name__ == '__main__':
    monitor_campaigns()
```

### Step 2: Test the Script

```bash
python scripts/monitor_campaigns.py
```

### Step 3: Set Up Slack Alerts (Optional)

```python
# Add to monitor_campaigns.py

import requests
import os

SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

def send_alert(message):
    """Send alert to Slack"""
    if SLACK_WEBHOOK_URL:
        payload = {
            'text': f"🚨 Facebook Ads Alert\n\n{message}",
            'username': 'FB Ads Monitor'
        }
        requests.post(SLACK_WEBHOOK_URL, json=payload)
    print(f"🚨 ALERT: {message}")
```

Get Slack webhook:
1. Go to https://api.slack.com/messaging/webhooks
2. Create incoming webhook
3. Set environment variable: `export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."`

### Step 4: Schedule Monitoring

```bash
# Run every 6 hours
crontab -e

# Add:
0 */6 * * * cd /path/to/facebook-ads-manager && /path/to/venv/bin/python scripts/monitor_campaigns.py >> logs/monitoring.log 2>&1
```

### Step 5: Create Dashboard Script

```python
#!/usr/bin/env python3
# scripts/dashboard.py

from src.api_client import FacebookAdsClient
from src.analytics.reporter import AnalyticsReporter

client = FacebookAdsClient()
reporter = AnalyticsReporter(client)

# Show live dashboard
reporter.show_dashboard()
```

Run anytime:

```bash
python scripts/dashboard.py
```

**Done!** You now have automated monitoring and alerts.

---

## Tutorial 6: Scaling a Winner

**Goal**: Systematically scale a successful campaign

**Time**: 10 minutes per step (spread over 2-4 weeks)

### Step 1: Identify Winner

```python
# find_winner.py

from src.api_client import FacebookAdsClient
from src.analytics.reporter import AnalyticsReporter

client = FacebookAdsClient()
reporter = AnalyticsReporter(client)

# Get last 7 days
reports = reporter.account_report(days=7)

# Find best ROAS with sufficient spend
winner = None
for report in reports:
    if report['spend'] >= 200 and report['roas'] >= 3.0:
        if not winner or report['roas'] > winner['roas']:
            winner = report

if winner:
    print(f"Winner: {winner['campaign_name']}")
    print(f"  ROAS: {winner['roas']:.2f}x")
    print(f"  Spend: ${winner['spend']:.2f}")
    print(f"  Conversions: {winner['conversions']}")
    print(f"\nReady to scale!")
else:
    print("No campaigns meet scaling criteria yet")
    print("Criteria: $200+ spend, 3.0x+ ROAS")
```

### Step 2: Gradual Scaling (Week 1)

Start with 20% increase:

```python
from src.campaign.manager import CampaignManager

manager = CampaignManager(client)

winner_id = "123456789012345"
current_budget = 100.00  # Current budget

# Increase by 20%
new_budget = current_budget * 1.2  # $120

manager.update_budget(winner_id, new_budget)
print(f"Scaled from ${current_budget} to ${new_budget}")
```

**Monitor for 3-5 days**. If ROAS stays above 2.5x, continue.

### Step 3: Continue Scaling (Week 2)

Another 20% increase:

```python
current_budget = 120.00
new_budget = current_budget * 1.2  # $144

manager.update_budget(winner_id, new_budget)
```

### Step 4: Aggressive Scaling (Week 3)

If ROAS remains strong (>3.0x), scale more aggressively:

```python
current_budget = 144.00
new_budget = current_budget * 1.5  # $216

manager.update_budget(winner_id, new_budget)
```

### Step 5: Create Scaling Plan

```python
# scaling_plan.py

def create_scaling_plan(campaign_id, start_budget, target_budget, weeks=4):
    """Create gradual scaling plan"""

    steps = []
    current = start_budget

    for week in range(1, weeks + 1):
        # Calculate new budget
        remaining_weeks = weeks - week + 1
        growth_rate = (target_budget / current) ** (1 / remaining_weeks)
        new_budget = current * growth_rate

        steps.append({
            'week': week,
            'budget': new_budget,
            'increase': new_budget - current,
            'increase_pct': ((new_budget - current) / current) * 100
        })

        current = new_budget

    return steps

# Example: Scale from $100 to $500 over 4 weeks
plan = create_scaling_plan(
    campaign_id="123456789",
    start_budget=100,
    target_budget=500,
    weeks=4
)

print("SCALING PLAN\n")
for step in plan:
    print(f"Week {step['week']}: ${step['budget']:.2f} (+${step['increase']:.2f}, +{step['increase_pct']:.1f}%)")

# Execute plan
# Week 1: manager.update_budget(campaign_id, plan[0]['budget'])
# Week 2: manager.update_budget(campaign_id, plan[1]['budget'])
# etc.
```

### Step 6: Monitor Efficiency

```python
# Check if efficiency is maintained during scaling

reports_before = reporter.campaign_report(campaign_id, days=7)
# ... scale budget ...
# Wait 7 days
reports_after = reporter.campaign_report(campaign_id, days=7)

roas_before = reports_before['roas']
roas_after = reports_after['roas']

efficiency_change = ((roas_after - roas_before) / roas_before) * 100

print(f"ROAS before: {roas_before:.2f}x")
print(f"ROAS after:  {roas_after:.2f}x")
print(f"Change: {efficiency_change:+.1f}%")

if efficiency_change < -20:
    print("⚠ Warning: Efficiency dropped significantly")
    print("Consider slowing down scaling")
elif efficiency_change > -10:
    print("✓ Efficiency maintained - continue scaling")
```

### Step 7: Duplicate Winners

Once at target budget, duplicate for redundancy:

```python
duplicated = manager.duplicate_campaign(
    campaign_id=winner_id,
    new_name="Winner Campaign - Duplicate 1"
)

print(f"Created duplicate: {duplicated['id']}")

# Start duplicate at 50% of original budget
manager.update_budget(duplicated['id'], new_budget=250.00)
manager.activate_campaign(duplicated['id'])
```

**Congratulations!** You've successfully scaled a winning campaign.

---

## Next Steps

- [Campaign Management Guide](campaign-management.md)
- [Analytics Guide](analytics.md)
- [Budget Optimization Guide](optimization.md)
- [A/B Testing Guide](ab-testing.md)
- [API Reference](api-reference.md)
