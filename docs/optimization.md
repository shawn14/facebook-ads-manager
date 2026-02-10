# Budget Optimization Guide

Comprehensive guide to automated budget optimization and campaign management.

## Table of Contents

1. [Overview](#overview)
2. [Budget Optimization](#budget-optimization)
3. [Auto-Pause Underperformers](#auto-pause-underperformers)
4. [Portfolio Rebalancing](#portfolio-rebalancing)
5. [Optimization Strategies](#optimization-strategies)
6. [Best Practices](#best-practices)

---

## Overview

The Budget Optimizer automatically adjusts campaign budgets based on performance, helping you:

- Maximize return on ad spend (ROAS)
- Reduce wasted ad spend
- Scale winning campaigns
- Pause underperformers automatically
- Maintain optimal budget allocation

### Key Features

- **Automated budget adjustments** based on ROAS
- **Underperformer detection** and auto-pause
- **Portfolio rebalancing** for multi-campaign optimization
- **Dry-run mode** to preview changes before applying
- **Customizable thresholds** via configuration

---

## Budget Optimization

### Basic Usage

#### CLI

```bash
# Preview optimization (dry run)
python -m src.cli optimize budgets --min-roas 2.0 --dry-run

# Apply optimization
python -m src.cli optimize budgets --min-roas 2.0 --no-dry-run
```

Output:
```
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Campaign         ┃ Current Budget ┃ New Budget  ┃ Change ┃ Reason                 ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Spring Sale      │ $100.00        │ $120.00     │ +20.0% │ High ROAS (4.2x)       │
│ Q1 Lead Gen      │ $75.00         │ $82.50      │ +10.0% │ Good ROAS (2.8x)       │
│ Brand Awareness  │ $50.00         │ $35.00      │ -30.0% │ Low ROAS (0.9x)        │
└──────────────────┴────────────────┴─────────────┴────────┴────────────────────────┘

ℹ This was a dry run. Use --no-dry-run to apply changes.
```

#### Python

```python
from src.api_client import FacebookAdsClient
from src.optimization.optimizer import BudgetOptimizer

client = FacebookAdsClient()
optimizer = BudgetOptimizer(client)

# Preview changes
changes = optimizer.optimize_budgets(
    min_roas=2.0,
    dry_run=True
)

# Review changes
for change in changes:
    print(f"{change['campaign_name']}:")
    print(f"  ROAS: {change['roas']:.2f}x")
    print(f"  Budget: ${change['old_budget']:.2f} → ${change['new_budget']:.2f}")
    print(f"  Change: {change['change_pct']:+.1f}%")
    print(f"  Reason: {change['reason']}")
    print()

# Apply changes if satisfied
if input("Apply changes? (yes/no): ").lower() == 'yes':
    optimizer.optimize_budgets(min_roas=2.0, dry_run=False)
    print("✓ Budget optimization applied")
```

### How It Works

The optimizer uses a tiered approach based on ROAS:

| ROAS Performance | Action | Budget Change |
|-----------------|--------|---------------|
| ROAS ≥ 2.25x (min_roas × 1.5) | Scale aggressively | +20% |
| ROAS ≥ 1.80x (min_roas × 1.2) | Scale moderately | +10% |
| ROAS ≥ 1.50x (min_roas) | Maintain | 0% |
| ROAS ≥ 1.20x (min_roas × 0.8) | Reduce slightly | -10% |
| ROAS < 1.20x | Reduce significantly | -30% |

**Example:**

With `min_roas = 1.5`:

```python
# ROAS = 4.5x (≥ 2.25x)
# Current budget: $100
# New budget: $100 × 1.2 = $120 (+20%)

# ROAS = 2.0x (≥ 1.80x)
# Current budget: $100
# New budget: $100 × 1.1 = $110 (+10%)

# ROAS = 1.6x (≥ 1.50x)
# Current budget: $100
# New budget: $100 (no change)

# ROAS = 1.3x (≥ 1.20x)
# Current budget: $100
# New budget: $100 × 0.9 = $90 (-10%)

# ROAS = 0.8x (< 1.20x)
# Current budget: $100
# New budget: $100 × 0.7 = $70 (-30%)
```

### Budget Constraints

Budgets are constrained by limits in `config/config.yaml`:

```yaml
campaigns:
  min_daily_budget: 10    # Minimum $10/day
  max_daily_budget: 5000  # Maximum $5000/day
```

Budgets are rounded to nearest $5 for cleaner numbers.

---

## Auto-Pause Underperformers

Automatically pause campaigns that aren't meeting performance standards.

### Basic Usage

#### CLI

```bash
# Preview which campaigns would be paused
python -m src.cli optimize pause-underperformers \
  --threshold 0.5 \
  --min-spend 100 \
  --dry-run

# Apply auto-pause
python -m src.cli optimize pause-underperformers \
  --threshold 0.5 \
  --min-spend 100 \
  --no-dry-run
```

Output:
```
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Campaign         ┃ CTR    ┃ Spend   ┃ Reason                            ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Old Product      │ 0.32%  │ $234.50 │ CTR (0.32%) below threshold (0.5%)│
│ Test Campaign    │ 0.41%  │ $156.20 │ CTR (0.41%) below threshold (0.5%)│
└──────────────────┴────────┴─────────┴───────────────────────────────────┘

✓ No underperforming campaigns found
```

#### Python

```python
# Pause campaigns with CTR < 0.5% and spend > $100
paused = optimizer.pause_underperformers(
    min_ctr=0.5,        # Minimum CTR threshold (%)
    min_spend=100,      # Only evaluate campaigns with $100+ spend
    dry_run=False
)

if paused:
    print(f"Paused {len(paused)} underperforming campaigns:")
    for item in paused:
        print(f"  - {item['campaign_name']}")
        print(f"    CTR: {item['ctr']:.2f}%")
        print(f"    Spend: ${item['spend']:.2f}")
        print(f"    Reason: {item['reason']}")
else:
    print("✓ No underperformers to pause")
```

### Parameters

**min_ctr** (float)
- Minimum click-through rate threshold (%)
- Default: 0.5%
- Campaigns below this CTR are paused

**min_spend** (float)
- Minimum spend to evaluate (USD)
- Default: $100
- Prevents pausing campaigns before they have enough data

### Best Practices

1. **Set appropriate thresholds**
   ```python
   # For brand awareness (lower CTR expected)
   paused = optimizer.pause_underperformers(
       min_ctr=0.3,      # Lower threshold
       min_spend=200     # More data before pausing
   )

   # For direct response (higher CTR expected)
   paused = optimizer.pause_underperformers(
       min_ctr=1.0,      # Higher threshold
       min_spend=50      # Faster decisions
   )
   ```

2. **Use dry-run first**
   ```python
   # Always preview before applying
   paused = optimizer.pause_underperformers(
       min_ctr=0.5,
       min_spend=100,
       dry_run=True
   )

   # Review the list
   if len(paused) < 5:  # Sanity check
       # Apply for real
       optimizer.pause_underperformers(
           min_ctr=0.5,
           min_spend=100,
           dry_run=False
       )
   ```

3. **Combine with anomaly detection**
   ```python
   from src.analytics.reporter import AnalyticsReporter

   reporter = AnalyticsReporter(client)

   # Get all active campaigns
   campaigns = client.get_campaigns(filtering=[{
       'field': 'status',
       'operator': 'EQUAL',
       'value': 'ACTIVE'
   }])

   for campaign in campaigns:
       # Check for anomalies
       anomalies = reporter.detect_anomalies(campaign['id'])

       # High severity anomalies → pause
       high_severity = [a for a in anomalies if a['severity'] == 'high']
       if high_severity:
           print(f"Pausing {campaign['name']} - {len(high_severity)} critical issues")
           client.pause_campaign(campaign['id'])
   ```

---

## Portfolio Rebalancing

Optimize total budget allocation across all campaigns to maximize overall ROI.

### Basic Usage

```python
# Rebalance $1000/day across all active campaigns
allocations = optimizer.rebalance_portfolio(
    total_budget=1000.00,
    dry_run=True
)

for allocation in allocations:
    print(f"{allocation['campaign_name']}:")
    print(f"  ROAS: {allocation['roas']:.2f}x")
    print(f"  Old Budget: ${allocation['old_budget']:.2f}")
    print(f"  New Budget: ${allocation['new_budget']:.2f}")
    print()
```

### How It Works

Budget is allocated proportionally based on ROAS:

**Example:**

```
Total Budget: $1000/day
Active Campaigns:

Campaign A: ROAS = 4.0x
Campaign B: ROAS = 2.0x
Campaign C: ROAS = 1.0x
Campaign D: ROAS = 0.5x (gets $0)

Total ROAS (excluding non-profitable): 4.0 + 2.0 + 1.0 = 7.0x

Allocations:
- Campaign A: (4.0 / 7.0) × $1000 = $571.43
- Campaign B: (2.0 / 7.0) × $1000 = $285.71
- Campaign C: (1.0 / 7.0) × $1000 = $142.86
- Campaign D: $0 (ROAS ≤ 0)
```

### Use Cases

**1. Total Budget Constraint**

You have a fixed total budget and want to allocate it optimally:

```python
# You have $5000/day total to spend
allocations = optimizer.rebalance_portfolio(
    total_budget=5000.00,
    dry_run=False
)
```

**2. Scaling All Campaigns Proportionally**

```python
# Get current total spend
campaigns = client.get_campaigns(filtering=[{
    'field': 'status',
    'operator': 'EQUAL',
    'value': 'ACTIVE'
}])

current_total = sum(
    int(c.get('daily_budget', 0)) / 100
    for c in campaigns
)

# Scale up by 50%
new_total = current_total * 1.5

allocations = optimizer.rebalance_portfolio(
    total_budget=new_total,
    dry_run=False
)

print(f"Scaled from ${current_total:.2f}/day to ${new_total:.2f}/day")
```

---

## Optimization Strategies

### Strategy 1: Conservative Optimization

Optimize only high-confidence changes:

```python
def conservative_optimize():
    """Conservative optimization - only adjust high performers and low performers"""

    # Only scale campaigns with ROAS > 3.0
    # Only reduce campaigns with ROAS < 1.0

    campaigns = client.get_campaigns(filtering=[{
        'field': 'status',
        'operator': 'EQUAL',
        'value': 'ACTIVE'
    }])

    for campaign in campaigns:
        insights = client.get_campaign_insights(
            campaign['id'],
            date_preset='last_7d'
        )

        if not insights:
            continue

        # Calculate ROAS
        insight = insights[0]
        spend = float(insight.get('spend', 0))
        conversions = extract_conversions(insight)
        revenue = conversions * 50  # avg order value
        roas = (revenue / spend) if spend > 0 else 0

        current_budget = int(campaign.get('daily_budget', 0)) / 100

        # High performer: scale up 20%
        if roas > 3.0:
            new_budget = current_budget * 1.2
            update_budget(campaign['id'], new_budget)
            print(f"↑ Scaled {campaign['name']}: ${current_budget} → ${new_budget}")

        # Low performer: reduce 30%
        elif roas < 1.0 and spend > 50:
            new_budget = current_budget * 0.7
            update_budget(campaign['id'], new_budget)
            print(f"↓ Reduced {campaign['name']}: ${current_budget} → ${new_budget}")

conservative_optimize()
```

### Strategy 2: Aggressive Scaling

Quickly scale winners and cut losers:

```python
def aggressive_optimize():
    """Aggressive optimization - rapid scaling and cutting"""

    changes = optimizer.optimize_budgets(
        min_roas=2.5,  # Higher threshold
        dry_run=False
    )

    # Additionally, pause anything with ROAS < 1.5
    campaigns = client.get_campaigns(filtering=[{
        'field': 'status',
        'operator': 'EQUAL',
        'value': 'ACTIVE'
    }])

    for campaign in campaigns:
        insights = client.get_campaign_insights(campaign['id'], date_preset='last_7d')
        if not insights:
            continue

        insight = insights[0]
        spend = float(insight.get('spend', 0))
        conversions = extract_conversions(insight)
        revenue = conversions * 50
        roas = (revenue / spend) if spend > 0 else 0

        if roas < 1.5 and spend > 100:
            client.pause_campaign(campaign['id'])
            print(f"⏸ Paused {campaign['name']}: ROAS {roas:.2f}x")

aggressive_optimize()
```

### Strategy 3: Test-and-Scale

Start small, scale winners:

```python
def test_and_scale():
    """Test new campaigns with small budget, scale winners"""

    campaigns = client.get_campaigns()

    for campaign in campaigns:
        # Check campaign age
        created_time = campaign.get('created_time', '')
        # Parse date and check if campaign is less than 7 days old
        # (simplified - you'd want proper date parsing)

        insights = client.get_campaign_insights(
            campaign['id'],
            date_preset='lifetime'
        )

        if not insights:
            continue

        insight = insights[0]
        spend = float(insight.get('spend', 0))
        conversions = extract_conversions(insight)
        revenue = conversions * 50
        roas = (revenue / spend) if spend > 0 else 0

        current_budget = int(campaign.get('daily_budget', 0)) / 100

        # New campaigns: start at $25/day
        if spend < 50 and current_budget != 25:
            update_budget(campaign['id'], 25.00)
            print(f"🆕 Set {campaign['name']} to test budget: $25/day")

        # After $100 spend with good ROAS: scale to $75/day
        elif spend >= 100 and roas >= 2.0 and current_budget < 75:
            update_budget(campaign['id'], 75.00)
            print(f"↗ Scaled {campaign['name']} to $75/day (ROAS: {roas:.2f}x)")

        # After $500 spend with excellent ROAS: scale to $150/day
        elif spend >= 500 and roas >= 3.0 and current_budget < 150:
            update_budget(campaign['id'], 150.00)
            print(f"⬆ Scaled {campaign['name']} to $150/day (ROAS: {roas:.2f}x)")

test_and_scale()
```

### Strategy 4: Scheduled Optimization

Run optimization on a schedule:

```python
#!/usr/bin/env python3
"""
Scheduled optimization script
Run with cron: 0 9 * * * /path/to/scheduled_optimize.py
"""

from datetime import datetime
from src.api_client import FacebookAdsClient
from src.optimization.optimizer import BudgetOptimizer

def main():
    client = FacebookAdsClient()
    optimizer = BudgetOptimizer(client)

    print(f"[{datetime.now()}] Running scheduled optimization")

    # Daily budget optimization
    changes = optimizer.optimize_budgets(
        min_roas=2.0,
        dry_run=False
    )

    print(f"Adjusted {len(changes)} campaign budgets")

    # Pause underperformers
    paused = optimizer.pause_underperformers(
        min_ctr=0.5,
        min_spend=100,
        dry_run=False
    )

    print(f"Paused {len(paused)} underperforming campaigns")

    # Log results
    with open('logs/optimization.log', 'a') as f:
        f.write(f"{datetime.now()}: Optimized {len(changes)}, Paused {len(paused)}\n")

if __name__ == '__main__':
    main()
```

Set up with cron:

```bash
# Run every day at 9 AM
0 9 * * * cd /path/to/facebook-ads-manager && /path/to/venv/bin/python scripts/scheduled_optimize.py
```

---

## Best Practices

### 1. Always Use Dry-Run First

```python
# Preview changes
changes = optimizer.optimize_budgets(min_roas=2.0, dry_run=True)

# Review and approve
print(f"Would change {len(changes)} campaigns")
for change in changes:
    print(f"  {change['campaign_name']}: {change['change_pct']:+.1f}%")

# Only apply if reasonable
if len(changes) <= 10:  # Sanity check
    optimizer.optimize_budgets(min_roas=2.0, dry_run=False)
```

### 2. Set Appropriate ROAS Thresholds

Different business models need different thresholds:

```python
# E-commerce (higher margins)
optimizer.optimize_budgets(min_roas=2.5, dry_run=False)

# Lead generation (lower margins)
optimizer.optimize_budgets(min_roas=1.5, dry_run=False)

# Subscription business (lifetime value)
optimizer.optimize_budgets(min_roas=1.2, dry_run=False)
```

### 3. Consider Campaign Age

Don't optimize campaigns too early:

```python
campaigns = client.get_campaigns()

for campaign in campaigns:
    insights = client.get_campaign_insights(
        campaign['id'],
        date_preset='lifetime'
    )

    if insights:
        spend = float(insights[0].get('spend', 0))

        # Only optimize campaigns with at least $100 spend
        if spend >= 100:
            # Run optimization
            pass
        else:
            print(f"Skipping {campaign['name']} - insufficient data (${spend:.2f} spend)")
```

### 4. Monitor Optimization Results

Track the impact of optimization:

```python
# Before optimization
before_reports = reporter.account_report(days=7)
before_spend = sum(r['spend'] for r in before_reports)
before_roas = sum(r['roas'] for r in before_reports) / len(before_reports)

# Run optimization
optimizer.optimize_budgets(min_roas=2.0, dry_run=False)

# Wait 7 days...

# After optimization
after_reports = reporter.account_report(days=7)
after_spend = sum(r['spend'] for r in after_reports)
after_roas = sum(r['roas'] for r in after_reports) / len(after_reports)

print(f"Optimization Results:")
print(f"  Spend: ${before_spend:.2f} → ${after_spend:.2f} ({(after_spend - before_spend) / before_spend * 100:+.1f}%)")
print(f"  ROAS: {before_roas:.2f}x → {after_roas:.2f}x ({(after_roas - before_roas) / before_roas * 100:+.1f}%)")
```

### 5. Combine Multiple Strategies

```python
def comprehensive_optimization():
    """Run multiple optimization strategies together"""

    # 1. Budget optimization
    budget_changes = optimizer.optimize_budgets(
        min_roas=2.0,
        dry_run=False
    )

    # 2. Pause underperformers
    paused = optimizer.pause_underperformers(
        min_ctr=0.5,
        min_spend=100,
        dry_run=False
    )

    # 3. Check for anomalies
    from src.analytics.reporter import AnalyticsReporter
    reporter = AnalyticsReporter(client)

    campaigns = client.get_campaigns(filtering=[{
        'field': 'status',
        'operator': 'EQUAL',
        'value': 'ACTIVE'
    }])

    anomaly_paused = 0
    for campaign in campaigns:
        anomalies = reporter.detect_anomalies(campaign['id'])
        critical = [a for a in anomalies if a['severity'] == 'high']

        if critical:
            client.pause_campaign(campaign['id'])
            anomaly_paused += 1

    print(f"Optimization complete:")
    print(f"  Budget changes: {len(budget_changes)}")
    print(f"  Paused (low CTR): {len(paused)}")
    print(f"  Paused (anomalies): {anomaly_paused}")

comprehensive_optimization()
```

---

## Next Steps

- [A/B Testing Guide](ab-testing.md) - Test optimization strategies
- [Analytics Guide](analytics.md) - Track optimization results
- [Campaign Management Guide](campaign-management.md) - Campaign setup
- [API Reference](api-reference.md) - Complete API documentation
