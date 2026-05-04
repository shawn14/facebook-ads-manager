# Creative Performance Stats ✅

## Overview

The Creatives page now shows **real performance metrics** from Facebook for each creative.

## What's Displayed

### Performance Metrics (Per Creative)

**Top Row:**
- **Impressions** - How many times the ad was shown
- **Clicks** - How many clicks it received
- **CTR** - Click-through rate (%)
  - Green if ≥ 1%
  - Shows actual performance

**Bottom Row:**
- **Spend** - Total money spent ($)
- **CPC** - Cost per click ($)
- **Conv.** - Total conversions
  - Green if > 0

## How It Works

### Data Source

Stats are aggregated from **all ads using each creative**:

1. Finds all active/paused ads
2. Matches ads to creatives
3. Aggregates performance data
4. Calculates metrics

### Metrics Calculated

```javascript
{
  impressions: total across all ads using this creative
  clicks: total clicks
  spend: total spend in dollars
  conversions: purchase/lead/registration actions
  ctr: (clicks / impressions) * 100
  cpc: spend / clicks
}
```

## Example

**Creative:** "Stock Alarm - Free Trial V1"

```
Impressions: 12,450
Clicks: 156
CTR: 1.25% (green - good performance!)

Spend: $45.80
CPC: $0.29
Conv.: 8 (green - has conversions!)
```

## Visual Indicators

### CTR Color Coding
- **Green** (≥ 1.0%) - Good performance
- **Gray** (< 1.0%) - Below average

### Conversions Color Coding
- **Green** (> 0) - Has conversions!
- **Gray** (0) - No conversions yet

## Performance Sorting

Use the **Sort By** dropdown:
- **Performance** - Sorts by CTR (highest first)
- **Name** - Alphabetical
- **Created** - Newest first

## API Endpoint

```bash
# Get creatives with stats
GET /api/creatives?include_stats=true

# Response
{
  "creatives": [
    {
      "id": "23857123456789012",
      "name": "Stock Alarm Ad",
      "stats": {
        "impressions": 12450,
        "clicks": 156,
        "spend": 45.80,
        "conversions": 8,
        "ctr": 1.25,
        "cpc": 0.29
      }
    }
  ]
}
```

## Use Cases

### 1. Identify Top Performers
- Sort by Performance
- Look for high CTR (green)
- Scale winning creatives

### 2. Find Underperformers
- Low CTR < 0.5%
- High CPC > $2.00
- Zero conversions

### 3. Calculate ROI
- Compare spend vs conversions
- Identify best creative styles
- A/B test variations

### 4. Optimize Budget
- Pause low CTR creatives
- Increase budget on high converters
- Test new variations

## Example Analysis

**Your Creatives:**

| Creative | CTR | CPC | Conv. | Action |
|----------|-----|-----|-------|--------|
| Trial V1 | 1.25% | $0.29 | 8 | ✅ Scale |
| Trial V2 | 0.45% | $1.20 | 2 | ⚠️ Test |
| Trial V3 | 2.10% | $0.18 | 15 | 🔥 Winner! |
| Trial V4 | 0.12% | $3.50 | 0 | ❌ Pause |

**Recommended Actions:**
1. **Trial V3** - Increase budget, create variations
2. **Trial V1** - Keep running, monitor
3. **Trial V2** - Test new image/copy
4. **Trial V4** - Pause, analyze why it failed

## Refresh Stats

Stats update automatically when you:
1. Load the Creatives page
2. Refresh the browser

**Note:** Facebook insights may have a delay of 1-2 hours for the latest data.

## Troubleshooting

### All Stats Show Zero

**Possible reasons:**
1. New creative with no impressions yet
2. No ads using this creative
3. Ads are paused/archived
4. Insights delay from Facebook

**Solution:** Wait 24 hours for new creatives to gather data

### Stats Seem Wrong

**Check:**
1. Are ads still active?
2. Did you recently pause campaigns?
3. Check Facebook Ads Manager for comparison

## Summary

The Creatives page now shows:
- ✅ Real performance data from Facebook
- ✅ 6 key metrics per creative
- ✅ Color-coded performance indicators
- ✅ Sortable by performance
- ✅ Updated on page load

Use this to identify winners, optimize budget, and improve campaign performance! 📊
