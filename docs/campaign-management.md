# Campaign Management Guide

Complete guide to creating, managing, and optimizing Facebook ad campaigns.

## Table of Contents

1. [Overview](#overview)
2. [Creating Campaigns](#creating-campaigns)
3. [Managing Campaigns](#managing-campaigns)
4. [Campaign Objectives](#campaign-objectives)
5. [Budget Management](#budget-management)
6. [Best Practices](#best-practices)

---

## Overview

The Facebook Ads Manager provides comprehensive tools for campaign management, from creation to optimization. This guide covers everything you need to know about managing campaigns effectively.

### Campaign Hierarchy

Facebook ads are organized in a three-tier hierarchy:

```
Campaign
├── Ad Set 1
│   ├── Ad 1
│   └── Ad 2
└── Ad Set 2
    ├── Ad 3
    └── Ad 4
```

- **Campaign**: Top level - defines the objective
- **Ad Set**: Defines targeting, budget, and schedule
- **Ad**: Contains creative (image, video, copy)

---

## Creating Campaigns

### Using the CLI

The simplest way to create a campaign:

```bash
python -m src.cli campaign create \
  --name "Q1 2026 Lead Generation" \
  --objective CONVERSIONS \
  --budget 100 \
  --status PAUSED
```

**Parameters:**
- `--name`: Campaign name (descriptive and unique)
- `--objective`: Marketing objective (see [Campaign Objectives](#campaign-objectives))
- `--budget`: Daily budget in USD
- `--status`: Initial status (`ACTIVE` or `PAUSED`)

### Using Python Code

```python
from src.api_client import FacebookAdsClient
from src.campaign.manager import CampaignManager

# Initialize
client = FacebookAdsClient()
manager = CampaignManager(client)

# Create campaign
campaign = manager.create_campaign(
    name="Q1 2026 Lead Generation",
    objective="CONVERSIONS",
    daily_budget=100.00,
    status="PAUSED"
)

print(f"Created campaign: {campaign['id']}")
```

### Creating Campaigns for Special Categories

For housing, employment, or credit ads:

```python
campaign = manager.create_campaign(
    name="Job Openings Campaign",
    objective="CONVERSIONS",
    daily_budget=50.00,
    special_ad_categories=["EMPLOYMENT"],
    status="PAUSED"
)
```

---

## Managing Campaigns

### Listing Campaigns

View all campaigns:

```bash
# CLI
python -m src.cli campaign list

# Filter by status
python -m src.cli campaign list --status ACTIVE

# JSON output
python -m src.cli campaign list --format json
```

Python code:

```python
# All campaigns
campaigns = manager.list_campaigns()

# Active campaigns only
active = manager.list_campaigns(status_filter="ACTIVE")

# Include performance insights
campaigns_with_insights = manager.list_campaigns(
    status_filter="ACTIVE",
    include_insights=True
)

for campaign in campaigns_with_insights:
    print(f"{campaign['name']}")
    print(f"  ROAS: {campaign['insights']['roas']:.2f}x")
    print(f"  Spend: ${campaign['insights']['spend']:.2f}")
```

### Pausing Campaigns

Pause a running campaign:

```bash
# CLI
python -m src.cli campaign pause --id 123456789
```

Python:

```python
manager.pause_campaign("123456789")
```

### Activating Campaigns

Activate a paused campaign:

```bash
# CLI
python -m src.cli campaign activate --id 123456789
```

Python:

```python
manager.activate_campaign("123456789")
```

### Updating Budget

Change campaign budget:

```python
# Increase budget to $150/day
manager.update_budget(
    campaign_id="123456789",
    new_budget=150.00
)
```

### Duplicating Campaigns

Create a copy of an existing campaign:

```python
new_campaign = manager.duplicate_campaign(
    campaign_id="123456789",
    new_name="Q2 2026 Campaign"
)

print(f"Duplicated campaign: {new_campaign['id']}")
```

---

## Campaign Objectives

Choose the right objective for your marketing goal:

### Website Traffic

**Objective:** `LINK_CLICKS`

Drive traffic to your website or landing page.

```python
campaign = manager.create_campaign(
    name="Blog Traffic Campaign",
    objective="LINK_CLICKS",
    daily_budget=50.00
)
```

**Best for:**
- Blog content promotion
- Product page visits
- Landing page traffic

### Conversions

**Objective:** `CONVERSIONS`

Optimize for specific actions on your website (purchases, sign-ups, etc.).

```python
campaign = manager.create_campaign(
    name="Lead Generation",
    objective="CONVERSIONS",
    daily_budget=100.00
)
```

**Best for:**
- E-commerce sales
- Lead generation
- Newsletter sign-ups
- App events

**Requirements:**
- Facebook Pixel installed
- Conversion events configured

### Brand Awareness

**Objective:** `BRAND_AWARENESS`

Reach people likely to remember your ads.

```python
campaign = manager.create_campaign(
    name="Brand Launch",
    objective="BRAND_AWARENESS",
    daily_budget=75.00
)
```

**Best for:**
- New product launches
- Brand building
- Top-of-funnel awareness

### Reach

**Objective:** `REACH`

Show ads to the maximum number of people in your target audience.

```python
campaign = manager.create_campaign(
    name="Local Event Promotion",
    objective="REACH",
    daily_budget=30.00
)
```

**Best for:**
- Local business promotion
- Event announcements
- Limited-time offers

### App Installs

**Objective:** `APP_INSTALLS`

Drive mobile app installations.

```python
campaign = manager.create_campaign(
    name="Mobile App Launch",
    objective="APP_INSTALLS",
    daily_budget=100.00
)
```

**Best for:**
- Mobile app launches
- App user acquisition
- Gaming apps

### Video Views

**Objective:** `VIDEO_VIEWS`

Get more views on video content.

```python
campaign = manager.create_campaign(
    name="Product Video Campaign",
    objective="VIDEO_VIEWS",
    daily_budget=40.00
)
```

**Best for:**
- Video content promotion
- Storytelling
- Product demonstrations

---

## Budget Management

### Setting Daily Budgets

Daily budgets control spending per day:

```python
# Start with moderate budget
campaign = manager.create_campaign(
    name="Test Campaign",
    objective="CONVERSIONS",
    daily_budget=50.00  # $50/day
)

# Scale up successful campaigns
manager.update_budget("123456789", new_budget=150.00)
```

### Budget Best Practices

**Start Small, Scale Up:**
```python
# Week 1: Test with small budget
campaign = manager.create_campaign(
    name="New Product Launch",
    objective="CONVERSIONS",
    daily_budget=25.00
)

# Week 2: If ROAS > 2.0, increase budget
# (See Analytics Guide for performance tracking)
if roas > 2.0:
    manager.update_budget(campaign['id'], new_budget=75.00)

# Week 3: Continue scaling
if roas > 2.5:
    manager.update_budget(campaign['id'], new_budget=150.00)
```

**Set Budget Limits:**

Configure in `config/config.yaml`:

```yaml
campaigns:
  min_daily_budget: 10   # Minimum $10/day
  max_daily_budget: 5000 # Maximum $5000/day
```

### Lifetime Budgets

For time-bound campaigns:

```python
# Use the low-level API client for lifetime budgets
campaign = client.create_campaign(
    name="Black Friday Sale",
    objective="CONVERSIONS",
    status="PAUSED"
)

# Update with lifetime budget (API level)
client.update_campaign(
    campaign_id=campaign['id'],
    updates={
        'lifetime_budget': 50000,  # $500.00 total
        'end_time': '2026-11-30T23:59:59'
    }
)
```

---

## Best Practices

### 1. Campaign Naming Convention

Use a consistent naming structure:

```
[Objective] - [Target Audience] - [Product/Offer] - [Date]
```

Examples:
- `CONV - US 25-45 - Spring Sale - Feb2026`
- `TRAFFIC - Tech Enthusiasts - Blog Content - Q1-2026`
- `AWARENESS - Broad - Brand Launch - 2026`

```python
campaign = manager.create_campaign(
    name="CONV - US 25-45 - Spring Sale - Feb2026",
    objective="CONVERSIONS",
    daily_budget=100.00
)
```

### 2. Start Campaigns Paused

Always create campaigns in paused state, then review before activating:

```python
# Create paused
campaign = manager.create_campaign(
    name="New Campaign",
    objective="CONVERSIONS",
    daily_budget=75.00,
    status="PAUSED"
)

# Review campaign settings
# Add ad sets and ads
# Then activate when ready
manager.activate_campaign(campaign['id'])
```

### 3. One Objective Per Campaign

Don't try to achieve multiple objectives in one campaign:

**Good:**
```python
# Campaign 1: Drive traffic
traffic_campaign = manager.create_campaign(
    name="Blog Traffic",
    objective="LINK_CLICKS",
    daily_budget=50.00
)

# Campaign 2: Generate conversions
conversion_campaign = manager.create_campaign(
    name="Lead Generation",
    objective="CONVERSIONS",
    daily_budget=100.00
)
```

**Bad:**
```python
# Trying to do both in one campaign
mixed_campaign = manager.create_campaign(
    name="Traffic AND Conversions",  # Don't do this
    objective="LINK_CLICKS",
    daily_budget=150.00
)
```

### 4. Use Campaign Budget Optimization (CBO)

Let Facebook optimize budget across ad sets:

```python
# Create campaign
campaign = client.create_campaign(
    name="CBO Test Campaign",
    objective="CONVERSIONS",
    status="PAUSED"
)

# Enable Campaign Budget Optimization
client.update_campaign(
    campaign_id=campaign['id'],
    updates={
        'daily_budget': 10000,  # $100.00
        'bid_strategy': 'LOWEST_COST_WITHOUT_CAP'
    }
)
```

### 5. Monitor and Adjust

Regular monitoring is essential:

```python
from src.analytics.reporter import AnalyticsReporter

reporter = AnalyticsReporter(client)

# Daily check
campaigns = manager.list_campaigns(
    status_filter="ACTIVE",
    include_insights=True
)

for campaign in campaigns:
    insights = campaign.get('insights', {})
    roas = insights.get('roas', 0)

    # Pause if underperforming
    if roas < 1.0 and insights.get('spend', 0) > 100:
        print(f"Pausing {campaign['name']} - Low ROAS: {roas:.2f}")
        manager.pause_campaign(campaign['id'])

    # Scale if performing well
    elif roas > 3.0:
        current_budget = insights.get('daily_budget', 0) / 100
        new_budget = current_budget * 1.2  # Increase by 20%
        print(f"Scaling {campaign['name']} - High ROAS: {roas:.2f}")
        manager.update_budget(campaign['id'], new_budget)
```

### 6. Test Multiple Ad Sets

Create multiple ad sets with different targeting:

```python
campaign = manager.create_campaign(
    name="Product Launch - Multi-Audience",
    objective="CONVERSIONS",
    daily_budget=150.00,
    status="ACTIVE"
)

# Ad Set 1: Lookalike audience
lookalike_targeting = {
    'geo_locations': {'countries': ['US']},
    'custom_audiences': [{'id': 'lookalike_123'}],
    'age_min': 25,
    'age_max': 55
}

adset1 = client.create_adset(
    campaign_id=campaign['id'],
    name="Lookalike Audience",
    daily_budget=7500,  # $75
    targeting=lookalike_targeting,
    optimization_goal="CONVERSIONS",
    status="ACTIVE"
)

# Ad Set 2: Interest-based audience
interest_targeting = {
    'geo_locations': {'countries': ['US']},
    'interests': [
        {'id': '6003107902433', 'name': 'Technology'}
    ],
    'age_min': 25,
    'age_max': 45
}

adset2 = client.create_adset(
    campaign_id=campaign['id'],
    name="Tech Enthusiasts",
    daily_budget=7500,  # $75
    targeting=interest_targeting,
    optimization_goal="CONVERSIONS",
    status="ACTIVE"
)
```

### 7. Leverage Automation

Use the built-in optimization tools:

```python
from src.optimization.optimizer import BudgetOptimizer

optimizer = BudgetOptimizer(client)

# Daily: Optimize budgets based on ROAS
changes = optimizer.optimize_budgets(
    min_roas=2.0,
    dry_run=False
)

# Daily: Pause underperformers
paused = optimizer.pause_underperformers(
    min_ctr=0.5,
    min_spend=100,
    dry_run=False
)
```

---

## Common Workflows

### Launch a New Product

```python
# 1. Create awareness campaign
awareness = manager.create_campaign(
    name="AWARE - Broad - New Product - Feb2026",
    objective="BRAND_AWARENESS",
    daily_budget=50.00,
    status="ACTIVE"
)

# 2. Create consideration campaign
consideration = manager.create_campaign(
    name="TRAFFIC - Engaged - New Product - Feb2026",
    objective="LINK_CLICKS",
    daily_budget=75.00,
    status="ACTIVE"
)

# 3. Create conversion campaign
conversion = manager.create_campaign(
    name="CONV - Warm Audience - New Product - Feb2026",
    objective="CONVERSIONS",
    daily_budget=100.00,
    status="ACTIVE"
)

# Monitor and optimize
# After 7 days, analyze performance and adjust budgets
```

### Seasonal Campaign

```python
# Create campaign with end date
campaign = client.create_campaign(
    name="Holiday Sale - Dec 2026",
    objective="CONVERSIONS",
    status="PAUSED"
)

# Set lifetime budget and schedule
client.update_campaign(
    campaign_id=campaign['id'],
    updates={
        'lifetime_budget': 500000,  # $5000 total
        'start_time': '2026-12-01T00:00:00',
        'end_time': '2026-12-25T23:59:59'
    }
)

# Activate
manager.activate_campaign(campaign['id'])
```

### A/B Test Campaigns

```python
from src.optimization.ab_testing import ABTestManager

ab_test = ABTestManager(client)

# Create base campaign
base_campaign = manager.create_campaign(
    name="AB Test Base - Creative Variations",
    objective="CONVERSIONS",
    daily_budget=100.00,
    status="ACTIVE"
)

# Create A/B test with 3 variants
test = ab_test.create_test(
    base_campaign_id=base_campaign['id'],
    num_variants=3,
    test_name="Creative Test - Feb 2026"
)

# After 7 days, analyze results
results = ab_test.analyze_test(test['id'])
ab_test.display_results(results)

# Scale the winner
if results['winner']:
    manager.update_budget(results['winner'], new_budget=200.00)
```

---

## Troubleshooting

### Campaign Not Delivering

**Possible causes:**

1. **Budget too low**
   ```python
   # Increase budget
   manager.update_budget("123456789", new_budget=50.00)
   ```

2. **Audience too narrow**
   ```python
   # Check ad set targeting
   adsets = client.get_adsets(campaign_id="123456789")
   # Broaden targeting if needed
   ```

3. **Campaign paused**
   ```python
   # Activate campaign
   manager.activate_campaign("123456789")
   ```

### High Cost Per Result

**Solutions:**

1. **Optimize for conversions instead of clicks**
   ```python
   client.update_campaign(
       campaign_id="123456789",
       updates={'objective': 'CONVERSIONS'}
   )
   ```

2. **Improve ad relevance**
   - Review ad creative and copy
   - Ensure targeting matches offer

3. **Use automated bidding**
   ```python
   # Let Facebook optimize bids
   adset = client.get_adsets(campaign_id="123456789")[0]
   # Update adset with automatic bidding
   ```

---

## Next Steps

- [Analytics Guide](analytics.md) - Track campaign performance
- [Budget Optimization](optimization.md) - Automate budget allocation
- [A/B Testing Guide](ab-testing.md) - Test creative variations
- [API Reference](api-reference.md) - Complete API documentation
