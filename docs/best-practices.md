# Best Practices

Production-ready best practices for Facebook Ads management.

## Table of Contents

1. [Campaign Setup](#campaign-setup)
2. [Budget Management](#budget-management)
3. [Creative & Copy](#creative--copy)
4. [Targeting](#targeting)
5. [Optimization](#optimization)
6. [Testing](#testing)
7. [Monitoring & Alerts](#monitoring--alerts)
8. [Security](#security)
9. [Data Management](#data-management)
10. [Team Workflows](#team-workflows)

---

## Campaign Setup

### Naming Conventions

Use consistent, descriptive names:

```
[Objective] - [Audience] - [Product/Offer] - [Date]

Examples:
✓ CONV - US 25-45 - Spring Sale - Mar2026
✓ TRAFFIC - Tech Enthusiasts - Blog Posts - Q1-2026
✓ AWARENESS - Lookalike - Brand Launch - Feb2026

✗ Campaign 1
✗ Test
✗ Facebook Ads
```

**Benefits:**
- Easy to filter and search
- Clear reporting
- Team understanding

### Campaign Structure

```
Campaign (Objective)
  ├── Ad Set 1 (Audience A, Budget A)
  │   ├── Ad 1 (Creative A)
  │   └── Ad 2 (Creative B)
  └── Ad Set 2 (Audience B, Budget B)
      ├── Ad 1 (Creative A)
      └── Ad 2 (Creative C)
```

**Best practices:**
- One objective per campaign
- 2-5 ad sets per campaign
- 2-3 ads per ad set
- Test creatives within ad sets

### Start Paused

```python
# Always create campaigns paused
campaign = manager.create_campaign(
    name="New Campaign",
    objective="CONVERSIONS",
    daily_budget=50.00,
    status="PAUSED"  # ← Important
)

# Review settings
# Add creatives
# Then activate
manager.activate_campaign(campaign['id'])
```

**Why:**
- Review before spending money
- Avoid mistakes
- Configure properly first

---

## Budget Management

### Budget Sizing

| Campaign Phase | Daily Budget | Purpose |
|----------------|--------------|---------|
| Testing | $25-50 | Validate concept |
| Scaling | $75-150 | Grow winners |
| Mature | $200+ | Maximize volume |

```python
# Testing phase
campaign = manager.create_campaign(
    name="Test - New Audience",
    objective="CONVERSIONS",
    daily_budget=25.00  # Small budget
)

# After proving ROAS > 2.5x, scale
if roas > 2.5:
    manager.update_budget(campaign['id'], new_budget=75.00)
```

### The 20% Rule

Never increase budget by more than 20% at once:

```python
def safe_scale(campaign_id, target_budget):
    """Scale gradually to avoid disrupting learning"""

    current_budget = get_current_budget(campaign_id)

    while current_budget < target_budget:
        # Increase by 20% or reach target
        new_budget = min(
            current_budget * 1.2,
            target_budget
        )

        manager.update_budget(campaign_id, new_budget)
        print(f"Scaled to ${new_budget:.2f}")

        # Wait 3-5 days between increases
        # (manually check before next increase)
        current_budget = new_budget

safe_scale("123456789", target_budget=200.00)
```

**Why:**
- Preserves Facebook's learning
- Avoids performance drops
- Maintains stable delivery

### Budget Diversification

Don't put all eggs in one basket:

```python
# ✗ Bad: 100% budget in one campaign
total_budget = 1000
campaign_a_budget = 1000  # Risky!

# ✓ Good: Diversify across campaigns
total_budget = 1000
campaign_a_budget = 400  # Best performer
campaign_b_budget = 300  # Second best
campaign_c_budget = 200  # Testing
campaign_d_budget = 100  # New test
```

---

## Creative & Copy

### Image Best Practices

- **Size**: 1200x628 pixels (1.91:1 ratio)
- **Text**: Less than 20% of image
- **Focus**: Clear product/benefit
- **Quality**: High resolution, professional

```python
# Facebook's text overlay tool
# https://business.facebook.com/ads/text-overlay

# Keep text minimal for better delivery
```

### Video Best Practices

- **Length**: 15-30 seconds (shorter = better)
- **Format**: Square (1:1) or vertical (4:5)
- **Hook**: First 3 seconds critical
- **Sound**: Design for sound-off viewing
- **Captions**: Always include

### Copy Formula

```
[Attention] + [Benefit] + [Social Proof] + [CTA]

Example:
"Stop wasting time on manual reports. [Attention]
Get automated insights in seconds. [Benefit]
Join 10,000+ marketers who save 5 hours per week. [Social Proof]
Start your free trial today. [CTA]"
```

### A/B Test Everything

```python
# Test one variable at a time
tests_to_run = [
    "Image vs Video",
    "Headline A vs B vs C",
    "Long copy vs Short copy",
    "CTA: 'Buy Now' vs 'Learn More'",
    "Benefit-focused vs Feature-focused"
]
```

---

## Targeting

### Audience Size Guidelines

| Audience Size | Campaign Type | Notes |
|--------------|---------------|-------|
| < 50K | Avoid | Too small, inconsistent |
| 50K - 200K | Niche products | Monitor closely |
| 200K - 2M | Sweet spot | Best performance |
| 2M - 10M | Broad | Good for scale |
| > 10M | Very broad | For awareness |

### Targeting Strategy

```python
# Start broad, narrow based on data
targeting_progression = {
    'week_1': {
        'geo_locations': {'countries': ['US']},
        'age_min': 25,
        'age_max': 65,
        # Broad targeting
    },

    'week_2': {
        'geo_locations': {'countries': ['US']},
        'age_min': 30,  # Narrowed based on data
        'age_max': 55,
        'interests': [
            {'id': '6003107902433', 'name': 'Technology'}
        ]
    },

    'week_3': {
        # Further refinement based on best performers
        'geo_locations': {
            'countries': ['US'],
            'regions': [{'key': 'California'}]  # Best region
        },
        'age_min': 35,
        'age_max': 50,
        'interests': [
            {'id': '6003107902433', 'name': 'Technology'},
            {'id': '6003139266461', 'name': 'Shopping'}
        ]
    }
}
```

### Exclusions

Always exclude:

```python
targeting = {
    'geo_locations': {'countries': ['US']},

    # Exclude existing customers
    'excluded_custom_audiences': [
        {'id': 'existing_customers_audience_id'}
    ],

    # Exclude converters (for top-of-funnel)
    'excluded_custom_audiences': [
        {'id': 'purchasers_last_30_days_id'}
    ]
}
```

---

## Optimization

### Daily Optimization Checklist

```python
#!/usr/bin/env python3
# Daily optimization routine

def daily_optimization():
    """Run every morning"""

    # 1. Check yesterday's performance
    reports = reporter.account_report(days=1)
    reporter.display_report(reports)

    # 2. Identify issues
    for report in reports:
        if report['roas'] < 1.5 and report['spend'] > 50:
            print(f"⚠ Review: {report['campaign_name']}")

    # 3. Optimize budgets
    optimizer.optimize_budgets(min_roas=2.0, dry_run=False)

    # 4. Pause underperformers
    optimizer.pause_underperformers(
        min_ctr=0.5,
        min_spend=100,
        dry_run=False
    )

    # 5. Check A/B tests
    # (If you have active tests)

    # 6. Export report
    reporter.export_csv(reports)
```

### When to Intervene

| Metric | Threshold | Action |
|--------|-----------|--------|
| ROAS < 1.0 | After $100 spend | Pause and review |
| ROAS 1.0-1.5 | After $200 spend | Reduce budget 30% |
| CTR < 0.5% | After $100 spend | Test new creative |
| CPA > $50 | After 20 conversions | Review targeting |
| Frequency > 3 | Any spend | Expand audience |

### Learning Phase

Don't make changes during learning:

```python
# Facebook's learning phase: ~50 conversions/week

def check_learning_phase(campaign_id):
    """Check if campaign is in learning"""

    insights = client.get_campaign_insights(
        campaign_id,
        date_preset='last_7d'
    )

    if insights:
        # Get ad sets
        adsets = client.get_adsets(campaign_id=campaign_id)

        for adset in adsets:
            # Check delivery status
            # If "LEARNING", don't make changes
            pass

# Wait for learning to complete before optimizing
```

---

## Testing

### Testing Framework

```python
class TestingStrategy:
    """Systematic testing approach"""

    def __init__(self):
        self.test_queue = [
            {
                'type': 'creative',
                'variable': 'format',
                'variants': ['image', 'video', 'carousel'],
                'budget': 100,
                'duration_days': 7
            },
            {
                'type': 'copy',
                'variable': 'headline',
                'variants': [
                    'Benefit-focused',
                    'Feature-focused',
                    'Question-based'
                ],
                'budget': 75,
                'duration_days': 7
            },
            {
                'type': 'audience',
                'variable': 'targeting',
                'variants': ['broad', 'narrow', 'lookalike'],
                'budget': 150,
                'duration_days': 14
            }
        ]

    def run_next_test(self):
        """Run next test in queue"""
        if self.test_queue:
            test = self.test_queue.pop(0)
            return self.create_test(test)

    def create_test(self, test_config):
        """Create and run test"""
        # Implementation
        pass
```

### Test Prioritization

Order of testing:

1. **Creative format** (biggest impact)
2. **Headlines** (medium impact)
3. **Audience** (medium impact)
4. **Copy length** (small impact)
5. **CTA** (small impact)

### Statistical Rigor

```python
# Minimum requirements for valid test
MIN_REQUIREMENTS = {
    'conversions_per_variant': 100,
    'days': 7,
    'confidence': 0.95
}

def is_test_valid(results):
    """Check if test has enough data"""

    for variant in results['variants']:
        if variant['conversions'] < MIN_REQUIREMENTS['conversions_per_variant']:
            return False, "Not enough conversions"

    if results['confidence'] < MIN_REQUIREMENTS['confidence']:
        return False, "Not statistically significant"

    return True, "Test is valid"
```

---

## Monitoring & Alerts

### Alert Hierarchy

**Critical** (immediate action):
- ROAS < 1.0 with $100+ spend
- Campaign spending > 2x daily budget
- API errors

**Warning** (review within 24h):
- ROAS 1.0-1.5 with $100+ spend
- CTR < 0.5% with $50+ spend
- Frequency > 3

**Info** (monitor):
- ROAS declining trend
- Increasing CPA
- Audience saturation

### Implementation

```python
# Alert configuration
ALERTS = {
    'critical': {
        'channels': ['slack', 'email', 'sms'],
        'conditions': [
            {'metric': 'roas', 'operator': '<', 'value': 1.0, 'min_spend': 100},
        ]
    },
    'warning': {
        'channels': ['slack', 'email'],
        'conditions': [
            {'metric': 'roas', 'operator': '<', 'value': 1.5, 'min_spend': 100},
            {'metric': 'ctr', 'operator': '<', 'value': 0.5, 'min_spend': 50},
        ]
    }
}
```

---

## Security

### API Credentials

**Never commit credentials:**

```bash
# .gitignore
config/config.yaml
.env
*.key
```

**Use environment variables:**

```python
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'facebook': {
        'app_id': os.getenv('FB_APP_ID'),
        'app_secret': os.getenv('FB_APP_SECRET'),
        'access_token': os.getenv('FB_ACCESS_TOKEN'),
    }
}
```

**Rotate tokens regularly:**

```bash
# Generate new access token every 60 days
# https://developers.facebook.com/apps/your-app-id/marketing-api/tools/
```

### Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_hour=200):
    """Decorator to rate limit API calls"""

    min_interval = 3600 / calls_per_hour  # seconds between calls

    def decorator(func):
        last_called = [0.0]

        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed

            if left_to_wait > 0:
                time.sleep(left_to_wait)

            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result

        return wrapper
    return decorator

@rate_limit(calls_per_hour=200)
def create_campaign(...):
    # API call
    pass
```

---

## Data Management

### Export Regular Backups

```python
# Weekly backup script

from datetime import datetime

def weekly_backup():
    """Export all data for backup"""

    # Get all campaigns
    reports = reporter.account_report(days=30)

    # Export with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    filename = f"backup_{timestamp}.csv"

    reporter.export_csv(reports, filename=filename)

    print(f"✓ Backup saved: {filename}")

# Run weekly
```

### Data Retention

```yaml
# config/config.yaml

data_retention:
  raw_exports: 90  # Keep CSV exports for 90 days
  logs: 30         # Keep logs for 30 days
  aggregated: 365  # Keep aggregated data for 1 year
```

---

## Team Workflows

### Multi-User Setup

```yaml
# config/team.yaml

users:
  - name: "John (Manager)"
    role: "admin"
    permissions: ["create", "edit", "delete", "optimize"]

  - name: "Sarah (Analyst)"
    role: "analyst"
    permissions: ["view", "report", "export"]

  - name: "Mike (Operator)"
    role: "operator"
    permissions: ["create", "edit", "view"]
```

### Change Log

```python
# Track all changes
import json
from datetime import datetime

def log_change(user, action, details):
    """Log all campaign changes"""

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user': user,
        'action': action,
        'details': details
    }

    with open('logs/changes.json', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

# Usage
log_change(
    user='john@company.com',
    action='budget_update',
    details={
        'campaign_id': '123456789',
        'old_budget': 100,
        'new_budget': 150
    }
)
```

### Code Review

```python
# Always dry-run in production

def production_deploy(changes):
    """Require approval for production changes"""

    # 1. Dry run
    preview = optimizer.optimize_budgets(
        min_roas=2.0,
        dry_run=True
    )

    # 2. Review
    print(f"Proposed changes: {len(preview)}")
    for change in preview:
        print(f"  {change['campaign_name']}: {change['change_pct']:+.1f}%")

    # 3. Approve
    approval = input("Apply changes? (yes/no): ")

    if approval.lower() == 'yes':
        # 4. Execute
        optimizer.optimize_budgets(
            min_roas=2.0,
            dry_run=False
        )

        # 5. Log
        log_change(
            user=get_current_user(),
            action='bulk_optimization',
            details={'changes': len(preview)}
        )
```

---

## Performance Benchmarks

Industry averages (2025-2026):

| Metric | Good | Excellent |
|--------|------|-----------|
| ROAS | 2.0x+ | 4.0x+ |
| CTR | 1.0%+ | 2.5%+ |
| CPC | < $1.00 | < $0.50 |
| CVR | 2.0%+ | 5.0%+ |
| CPA | Varies | 50% of LTV |

**Your goals may differ based on:**
- Industry
- Product margins
- Customer lifetime value
- Business model

---

## Quick Reference

### Daily Tasks

```bash
# Morning routine (9 AM)
python scripts/daily_optimization.py

# Review dashboard
python scripts/dashboard.py

# Check alerts
python scripts/monitor_campaigns.py
```

### Weekly Tasks

```bash
# Monday: Review last week
python -m src.cli analytics report --days 7

# Analyze A/B tests
python -m src.cli test analyze --test-id <id>

# Weekly backup
python scripts/weekly_backup.py
```

### Monthly Tasks

```bash
# Monthly report
python -m src.cli analytics report --days 30 --format csv

# Review all campaigns
python scripts/monthly_review.py

# Update targeting based on data
```

---

## Next Steps

- [Tutorials](tutorials.md) - Step-by-step guides
- [API Reference](api-reference.md) - Complete API documentation
- [Architecture Guide](architecture.md) - System design
