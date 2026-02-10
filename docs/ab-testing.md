# A/B Testing Guide

Complete guide to running A/B tests for Facebook ad campaigns.

## Table of Contents

1. [Overview](#overview)
2. [Creating A/B Tests](#creating-ab-tests)
3. [Analyzing Results](#analyzing-results)
4. [Statistical Significance](#statistical-significance)
5. [Best Practices](#best-practices)
6. [Common Test Types](#common-test-types)

---

## Overview

A/B testing (also called split testing) helps you identify which variations of your ads perform better by comparing them in a controlled experiment.

### What You Can Test

- **Creative**: Images, videos, ad formats
- **Copy**: Headlines, descriptions, calls-to-action
- **Audience**: Different targeting parameters
- **Placement**: Facebook vs Instagram, feed vs stories
- **Bidding**: Manual vs automatic bidding

### Benefits

- Data-driven decisions
- Improved campaign performance
- Reduced cost per acquisition
- Better understanding of your audience

---

## Creating A/B Tests

### Using the CLI

```bash
python -m src.cli test create \
  --campaign-id 123456789 \
  --variants 3 \
  --name "Creative Test - February 2026"
```

This creates 3 variant campaigns based on your base campaign.

### Using Python

```python
from src.api_client import FacebookAdsClient
from src.optimization.ab_testing import ABTestManager

client = FacebookAdsClient()
ab_test = ABTestManager(client)

# Create test with 2 variants
test = ab_test.create_test(
    base_campaign_id="123456789",
    num_variants=2,
    test_name="Headline Test - Feb 2026"
)

print(f"Test created: {test['id']}")
print(f"Variants: {len(test['variants'])}")

for variant in test['variants']:
    print(f"  - {variant['name']} (ID: {variant['id']})")
```

### Test Structure

When you create a test, the system:

1. **Creates variant campaigns** based on your base campaign
2. **Splits budget evenly** across variants
3. **Maintains targeting** from the base campaign
4. **Sets campaigns to PAUSED** for you to configure

**Example:**

```python
# Base campaign: $100/day budget
# Test with 4 variants

test = ab_test.create_test(
    base_campaign_id="123456789",
    num_variants=4,
    test_name="Video vs Image Test"
)

# Each variant gets: $100 / 4 = $25/day
```

### Configuring Variants

After creating the test, configure each variant with different creative:

```python
# Get variant IDs
variants = test['variants']

# Variant 1: Image ad
variant_1_id = variants[0]['id']
# Add image ad creative to this campaign

# Variant 2: Video ad
variant_2_id = variants[1]['id']
# Add video ad creative to this campaign

# Activate all variants
for variant in variants:
    client.activate_campaign(variant['id'])
```

---

## Analyzing Results

### Wait for Sufficient Data

**Minimum requirements:**
- At least 100 conversions per variant
- At least 7 days of data
- Statistical significance > 95%

### Using the CLI

```bash
python -m src.cli test analyze --test-id test_123456789_2
```

Output:
```
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┓
┃ Variant               ┃ Impressions┃ Clicks ┃ CTR   ┃ Conversions┃ CVR   ┃ Winner ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━┩
│ Image - Variant 1     │    45,230  │  1,234 │ 2.73% │    156     │ 12.6% │        │
│ Video - Variant 2     │    46,102  │  1,567 │ 3.40% │    203     │ 13.0% │   🏆   │
└───────────────────────┴────────────┴────────┴───────┴────────────┴───────┴────────┘

Winner detected with 96.2% confidence
```

### Using Python

```python
# Analyze test
results = ab_test.analyze_test(
    test_id="test_123456789_2",
    metric="conversions"  # or "ctr"
)

# Display formatted results
ab_test.display_results(results)

# Access winner
if results['winner']:
    winner_id = results['winner']
    confidence = results['confidence']

    print(f"Winner: {winner_id}")
    print(f"Confidence: {confidence * 100:.1f}%")

    # Scale the winner
    from src.campaign.manager import CampaignManager
    manager = CampaignManager(client)
    manager.update_budget(winner_id, new_budget=200.00)

    # Pause losers
    for variant in results['variants']:
        if variant['id'] != winner_id:
            manager.pause_campaign(variant['id'])
else:
    print("No statistically significant winner yet")
    print(f"Current confidence: {results['confidence'] * 100:.1f}%")
    print("Continue running the test")
```

### Detailed Analysis

```python
# Get full test data
results = ab_test.analyze_test("test_123456789_2")

# Analyze each variant
for variant in results['variants']:
    print(f"\n{variant['name']}:")
    print(f"  Impressions: {variant['impressions']:,}")
    print(f"  Clicks: {variant['clicks']:,}")
    print(f"  CTR: {variant['ctr']:.2f}%")
    print(f"  Conversions: {variant['conversions']}")
    print(f"  CVR: {variant['cvr']:.2f}%")

    # Calculate efficiency
    if variant['clicks'] > 0:
        cost_per_click = variant.get('spend', 0) / variant['clicks']
        print(f"  CPC: ${cost_per_click:.2f}")
```

---

## Statistical Significance

### Understanding Confidence Levels

The test uses statistical methods to determine if differences are real or due to chance.

**Confidence Level:**
- **< 90%**: Not significant, continue testing
- **90-95%**: Marginally significant
- **> 95%**: Statistically significant (standard threshold)
- **> 99%**: Highly significant

**Example:**

```
Variant A: 150 conversions from 1,200 clicks = 12.5% CVR
Variant B: 180 conversions from 1,200 clicks = 15.0% CVR

Confidence: 97.3%

Interpretation: There's a 97.3% probability that Variant B
truly performs better (not due to random chance).
```

### How It Works

The system uses a **Z-test for proportions**:

1. Calculate conversion rates for each variant
2. Compute pooled proportion
3. Calculate standard error
4. Compute Z-score
5. Determine p-value
6. Calculate confidence (1 - p-value)

**Minimum Sample Size:**

For reliable results, each variant needs:
- At least 30 clicks (absolute minimum)
- Preferably 100+ conversions
- Similar impression counts

### Configuring Confidence Threshold

Edit `config/config.yaml`:

```yaml
optimization:
  confidence_level: 0.95  # 95% confidence required
  min_sample_size: 100    # Minimum conversions before declaring winner
```

---

## Best Practices

### 1. Test One Variable at a Time

**Good:**

```python
# Test A: Different headlines
test_headlines = ab_test.create_test(
    base_campaign_id="123456789",
    num_variants=2,
    test_name="Headline Test"
)

# Variant 1: "Save 50% Today"
# Variant 2: "Limited Time Offer"
# Everything else is identical
```

**Bad:**

```python
# Test B: Multiple variables
test_everything = ab_test.create_test(
    base_campaign_id="123456789",
    num_variants=2,
    test_name="Everything Test"
)

# Variant 1: Image + Headline A + CTA A
# Variant 2: Video + Headline B + CTA B
# Can't tell which change caused the difference!
```

### 2. Run Tests Long Enough

```python
# Minimum test duration
MIN_TEST_DAYS = 7
MIN_CONVERSIONS = 100

# Check if test is ready
results = ab_test.analyze_test("test_123456789_2")

total_conversions = sum(v['conversions'] for v in results['variants'])

if total_conversions < MIN_CONVERSIONS:
    print(f"Not enough data yet: {total_conversions}/{MIN_CONVERSIONS} conversions")
    print("Continue running test")
elif results['confidence'] < 0.95:
    print(f"Not statistically significant yet: {results['confidence']*100:.1f}%")
    print("Continue running test")
else:
    print("Test complete! Winner found.")
    # Implement winner
```

### 3. Equal Budget Split

Ensure fair comparison:

```python
# Create test with even budget split
test = ab_test.create_test(
    base_campaign_id="123456789",
    num_variants=3,
    test_name="Creative Test",
    budget_split="even"  # Default behavior
)

# Each variant gets equal budget
# Base budget: $150/day
# Each variant: $150 / 3 = $50/day
```

### 4. Consistent Targeting

Use identical targeting for all variants:

```python
# Get base campaign targeting
base_campaign = client.get_campaigns()[0]  # Your base campaign
adsets = client.get_adsets(campaign_id=base_campaign['id'])
base_targeting = adsets[0] if adsets else {}

# Create test
test = ab_test.create_test(
    base_campaign_id=base_campaign['id'],
    num_variants=2,
    test_name="Image vs Video"
)

# Apply same targeting to all variants
for variant in test['variants']:
    # Create adset with same targeting
    client.create_adset(
        campaign_id=variant['id'],
        name="Ad Set 1",
        daily_budget=5000,  # $50
        targeting=base_targeting,
        optimization_goal="CONVERSIONS"
    )
```

### 5. Document Your Tests

```python
# Create a test log
import json
from datetime import datetime

test_log = {
    'test_id': test['id'],
    'test_name': test['name'],
    'created_at': datetime.now().isoformat(),
    'hypothesis': 'Video ads will have higher CTR than image ads',
    'variants': [
        {'id': test['variants'][0]['id'], 'description': 'Static image ad'},
        {'id': test['variants'][1]['id'], 'description': 'Video ad (15 sec)'}
    ],
    'target_metric': 'CTR',
    'min_confidence': 0.95,
    'notes': 'Testing for Q1 campaign'
}

# Save log
with open(f"tests/test_{test['id']}.json", 'w') as f:
    json.dump(test_log, f, indent=2)
```

### 6. Implement Winners Quickly

```python
def implement_winner(test_id):
    """Scale winning variant and pause losers"""

    results = ab_test.analyze_test(test_id)

    if not results['winner']:
        print("No winner yet")
        return

    winner_id = results['winner']
    confidence = results['confidence']

    print(f"Winner: {winner_id}")
    print(f"Confidence: {confidence * 100:.1f}%")

    # Scale winner to original budget
    from src.campaign.manager import CampaignManager
    manager = CampaignManager(client)

    # Get original budget
    original_budget = 100.00  # From base campaign

    # Update winner
    manager.update_budget(winner_id, new_budget=original_budget)
    print(f"Scaled winner to ${original_budget}/day")

    # Pause losers
    for variant in results['variants']:
        if variant['id'] != winner_id:
            manager.pause_campaign(variant['id'])
            print(f"Paused: {variant['name']}")

    # Log result
    with open('tests/winners.log', 'a') as f:
        f.write(f"{datetime.now()}: Test {test_id} - Winner: {winner_id} ({confidence*100:.1f}%)\n")

# Usage
implement_winner("test_123456789_2")
```

---

## Common Test Types

### 1. Creative Testing (Image vs Video)

```python
# Create test
test = ab_test.create_test(
    base_campaign_id="123456789",
    num_variants=2,
    test_name="Creative Format Test - Feb 2026"
)

# Configure variants
# Variant 1: Upload image creative
# Variant 2: Upload video creative

# Run for 7 days
# Analyze
results = ab_test.analyze_test(test['id'], metric='conversions')
```

**What to look for:**
- Video often has higher CTR but may have lower CVR
- Images may have lower CPC
- Consider both CTR and conversion rate

### 2. Headline Testing

```python
test = ab_test.create_test(
    base_campaign_id="123456789",
    num_variants=3,
    test_name="Headline Test - Feb 2026"
)

# Variants:
# 1. "Save 50% This Weekend Only"
# 2. "Limited Time: Half Off Everything"
# 3. "Weekend Sale - 50% Off"

# All use same image, targeting, etc.
```

**What to look for:**
- CTR differences
- Conversion rate differences
- Message-market fit

### 3. Audience Testing

```python
test = ab_test.create_test(
    base_campaign_id="123456789",
    num_variants=3,
    test_name="Audience Test - Feb 2026"
)

# Configure different targeting for each variant

# Variant 1: Broad interest-based
targeting_broad = {
    'geo_locations': {'countries': ['US']},
    'interests': [{'id': '6003107902433', 'name': 'Technology'}],
    'age_min': 25,
    'age_max': 65
}

# Variant 2: Narrow interest-based
targeting_narrow = {
    'geo_locations': {'countries': ['US']},
    'interests': [
        {'id': '6003107902433', 'name': 'Technology'},
        {'id': '6003139266461', 'name': 'Shopping'}
    ],
    'age_min': 30,
    'age_max': 50
}

# Variant 3: Lookalike audience
targeting_lookalike = {
    'geo_locations': {'countries': ['US']},
    'custom_audiences': [{'id': 'lookalike_123'}],
    'age_min': 25,
    'age_max': 65
}

# Apply targeting to each variant's ad set
```

**What to look for:**
- Cost per acquisition differences
- ROAS differences
- Audience size vs performance trade-off

### 4. Call-to-Action Testing

```python
test = ab_test.create_test(
    base_campaign_id="123456789",
    num_variants=4,
    test_name="CTA Test - Feb 2026"
)

# Variants:
# 1. "Shop Now"
# 2. "Learn More"
# 3. "Get Started"
# 4. "Sign Up"
```

**What to look for:**
- Click-through rate
- Conversion rate (different CTAs may attract different intent)

### 5. Placement Testing

```python
test = ab_test.create_test(
    base_campaign_id="123456789",
    num_variants=3,
    test_name="Placement Test - Feb 2026"
)

# Variant 1: Facebook Feed only
# Variant 2: Instagram Feed only
# Variant 3: Stories only

# Configure publisher_platforms in targeting
```

**What to look for:**
- CPC differences by platform
- Conversion rate by platform
- Audience behavior differences

---

## Advanced Testing

### Sequential Testing

Test iteratively:

```python
def sequential_test():
    """Run multiple rounds of testing"""

    # Round 1: Test 3 images
    test_round_1 = ab_test.create_test(
        base_campaign_id="123456789",
        num_variants=3,
        test_name="Image Test - Round 1"
    )

    # Wait 7 days...
    results_1 = ab_test.analyze_test(test_round_1['id'])
    winner_1 = results_1['winner']

    # Round 2: Test winning image with 3 headlines
    test_round_2 = ab_test.create_test(
        base_campaign_id=winner_1,
        num_variants=3,
        test_name="Headline Test - Round 2"
    )

    # Wait 7 days...
    results_2 = ab_test.analyze_test(test_round_2['id'])
    final_winner = results_2['winner']

    print(f"Final optimized campaign: {final_winner}")

sequential_test()
```

### Multi-Armed Bandit

Automatically allocate more budget to winning variants:

```python
def bandit_optimization(test_id):
    """Dynamically adjust budgets based on performance"""

    results = ab_test.analyze_test(test_id)

    # Calculate performance scores
    variants_with_scores = []
    for variant in results['variants']:
        # Score = CVR (or any metric)
        score = variant['cvr']
        variants_with_scores.append({
            'id': variant['id'],
            'name': variant['name'],
            'score': score
        })

    # Sort by score
    variants_with_scores.sort(key=lambda x: x['score'], reverse=True)

    # Allocate budget proportionally
    total_budget = 100.00  # Total test budget
    total_score = sum(v['score'] for v in variants_with_scores)

    for variant in variants_with_scores:
        if total_score > 0:
            budget = (variant['score'] / total_score) * total_budget
        else:
            budget = total_budget / len(variants_with_scores)

        # Update budget
        from src.campaign.manager import CampaignManager
        manager = CampaignManager(client)
        manager.update_budget(variant['id'], budget)

        print(f"{variant['name']}: ${budget:.2f}/day (score: {variant['score']:.2f}%)")

# Run daily
bandit_optimization("test_123456789_2")
```

---

## Troubleshooting

### Test Not Reaching Significance

**Problem:** Running for weeks but confidence < 95%

**Solutions:**

1. **Increase budget** to get more data faster
   ```python
   for variant in test['variants']:
       manager.update_budget(variant['id'], new_budget=100.00)
   ```

2. **Check if differences are too small**
   ```python
   results = ab_test.analyze_test(test_id)
   for i, var1 in enumerate(results['variants']):
       for var2 in results['variants'][i+1:]:
           diff = abs(var1['cvr'] - var2['cvr'])
           print(f"{var1['name']} vs {var2['name']}: {diff:.2f}% difference")
   # If differences < 0.5%, may need larger sample size
   ```

3. **Run longer** (up to 30 days)

### Inconsistent Results

**Problem:** Winner changes when re-analyzing

**Cause:** Not enough data, random variance

**Solution:** Wait for more conversions (100+ per variant)

### High Cost During Testing

**Problem:** Test is expensive

**Solution:** Use smaller budgets during testing phase

```python
# Testing phase: $25/day per variant
test = ab_test.create_test(
    base_campaign_id="123456789",
    num_variants=4,
    test_name="Budget-Friendly Test"
)

for variant in test['variants']:
    manager.update_budget(variant['id'], new_budget=25.00)

# After finding winner, scale up
# Winner gets full budget
```

---

## Next Steps

- [Campaign Management Guide](campaign-management.md) - Setup campaigns
- [Analytics Guide](analytics.md) - Track test performance
- [Budget Optimization](optimization.md) - Scale winning tests
- [API Reference](api-reference.md) - Complete API documentation
