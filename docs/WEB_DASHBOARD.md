# Web Dashboard Guide

Complete guide to using the Facebook Ads Manager web dashboard.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Campaign Management](#campaign-management)
4. [Analytics](#analytics)
5. [Budget Optimization](#budget-optimization)
6. [Creative Library](#creative-library)
7. [API Reference](#api-reference)

## Getting Started

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API credentials
cp config/config.example.yaml config/config.yaml
# Edit config/config.yaml with your Facebook API credentials
```

### Running the Dashboard

```bash
# Option 1: Using the convenience script
python run_web.py

# Option 2: Direct command
python -m src.web.app

# Option 3: Using uvicorn with auto-reload
uvicorn src.web.app:app --reload --host 0.0.0.0 --port 8000
```

Access the dashboard at: http://localhost:8000

## Dashboard Overview

The main dashboard provides a real-time overview of all your campaigns.

### Key Metrics

- **Total Spend**: Cumulative spend across all campaigns
- **Total Impressions**: Number of times ads were shown
- **Total Clicks**: Number of clicks on your ads
- **Average ROAS**: Return on ad spend across all campaigns

### Interactive Charts

#### Spend by Campaign
Bar chart showing spend distribution across campaigns. Helps identify which campaigns are consuming the most budget.

#### ROAS by Campaign
Color-coded bar chart showing ROAS performance:
- Green: ROAS >= 2.0 (Excellent)
- Yellow: ROAS >= 1.0 (Good)
- Red: ROAS < 1.0 (Needs attention)

### Campaign Performance Table

Detailed table showing:
- Campaign name
- Impressions
- Clicks
- Click-through rate (CTR)
- Total spend
- Conversions
- Return on ad spend (ROAS)

### Time Range Selection

Filter data by time period:
- Last 7 days
- Last 14 days
- Last 30 days
- Last 90 days

## Campaign Management

### Viewing Campaigns

Navigate to `/campaigns` to see all your campaigns.

**Filter Options:**
- **Status**: Filter by ACTIVE or PAUSED campaigns
- **Performance**: View with or without performance insights

### Creating a Campaign

1. Click "Create Campaign" button
2. Fill in campaign details:
   - **Name**: Descriptive campaign name
   - **Objective**: Choose from:
     - Link Clicks
     - Conversions
     - Reach
     - Brand Awareness
     - Video Views
   - **Daily Budget**: Budget in USD
   - **Status**: ACTIVE or PAUSED
3. Click "Create"

### Managing Campaigns

**Pause/Activate**
- Click the pause/play icon to toggle campaign status
- Green indicator = Active
- Yellow indicator = Paused

**Edit Budget**
- Click the edit icon
- Enter new daily budget
- Click "Update"

**Delete Campaign**
- Click the delete icon
- Confirm deletion
- Campaign and all associated data will be removed

### Campaign Status Indicators

- **Green (Active)**: Campaign is running and serving ads
- **Yellow (Paused)**: Campaign is paused, not spending budget

## Analytics

Navigate to `/analytics` for detailed performance analysis.

### Account Overview

When no campaign is selected, view account-level metrics:
- Total campaigns count
- Aggregate spend
- Total conversions
- Average ROAS across all campaigns

### Campaign Analytics

Select a specific campaign to view:

**Performance Metrics:**
- Impressions
- Clicks
- Click-through rate (CTR)
- Cost per click (CPC)
- Total spend
- Conversions
- Cost per acquisition (CPA)
- Return on ad spend (ROAS)

**Visual Analytics:**
- Performance timeline chart
- Conversion funnel visualization

### Anomaly Detection

The system automatically detects performance anomalies:

**Low ROAS Warning**
- Triggers when ROAS falls below configured threshold
- Suggests budget reduction or campaign pause

**Low CTR Alert**
- Indicates creative may need refreshing
- Suggests A/B testing new copy/images

**High CPA Warning**
- Cost per acquisition exceeds target
- May indicate targeting issues

### Time Period Selection

Analyze performance across different time ranges:
- Last 7 days (default)
- Last 14 days
- Last 30 days

## Budget Optimization

Navigate to `/optimization` for automated optimization tools.

### Optimize Budgets

Automatically adjust budgets based on ROAS performance.

**Parameters:**
- **Min ROAS**: Minimum acceptable ROAS (default: 1.5)

**How it works:**
1. High performers (ROAS >= 1.5x min): +20% budget
2. Good performers (ROAS >= 1.2x min): +10% budget
3. Meeting threshold: No change
4. Below threshold: -10% to -30% budget reduction

**Preview Mode:**
- Click "Preview Changes" to see proposed changes
- Review impact before applying
- No changes made until "Apply Changes" clicked

### Pause Underperformers

Automatically pause campaigns not meeting performance thresholds.

**Parameters:**
- **Min CTR**: Minimum click-through rate (default: 0.5%)
- **Min Spend**: Minimum spend before evaluation (default: $100)

**Criteria:**
- Campaign must have spent minimum amount
- CTR below threshold triggers pause
- Prevents wasting budget on poor performers

### Rebalance Portfolio

Redistribute total budget based on ROAS performance.

**Parameters:**
- **Total Budget**: Total daily budget to allocate

**How it works:**
1. Campaigns ranked by ROAS
2. Budget allocated proportionally
3. Higher ROAS = Larger budget share
4. Zero ROAS campaigns receive no budget

**Use Case:**
- Maintaining fixed total daily spend
- Maximizing ROI across portfolio
- Dynamic budget reallocation

## Creative Library

Navigate to `/creatives` to manage ad creatives.

### Creative Types

- **Image**: Single image ads
- **Video**: Video ads
- **Carousel**: Multi-image carousel ads

### Viewing Creatives

**Filters:**
- **Type**: Filter by creative type
- **Status**: Filter by active/paused/archived
- **Sort**: Order by created date, performance, or name

### Adding Creatives

1. Click "Add Creative"
2. Enter creative details:
   - Name
   - Type (Image/Video/Carousel)
   - Ad copy
   - Headline
   - Call to action
3. Upload media file (coming soon)
4. Click "Add Creative"

### Creative Performance

Each creative displays:
- **CTR**: Click-through rate
- **Clicks**: Total clicks
- **Conversions**: Number of conversions

### Creative Actions

**Edit**
- Modify creative copy and settings
- Update headline and CTA

**Duplicate**
- Create copy for A/B testing
- Test variations quickly

## API Reference

### REST API Endpoints

#### Health Check
```
GET /api/health
```
Returns server status and timestamp.

#### Account Information
```
GET /api/account
```
Returns ad account details including name, currency, balance.

#### List Campaigns
```
GET /api/campaigns?status=ACTIVE&include_insights=true
```

**Parameters:**
- `status` (optional): Filter by status
- `include_insights` (optional): Include performance data

#### Create Campaign
```
POST /api/campaigns?name=Campaign&objective=CONVERSIONS&daily_budget=100&status=PAUSED
```

**Parameters:**
- `name`: Campaign name
- `objective`: Campaign objective
- `daily_budget`: Daily budget in USD
- `status`: ACTIVE or PAUSED

#### Update Campaign Status
```
PUT /api/campaigns/{campaign_id}/status?status=ACTIVE
```

#### Update Campaign Budget
```
PUT /api/campaigns/{campaign_id}/budget?budget=150
```

#### Delete Campaign
```
DELETE /api/campaigns/{campaign_id}
```

#### Analytics Overview
```
GET /api/analytics/overview?days=7
```

Returns account-level analytics for specified time period.

#### Campaign Analytics
```
GET /api/analytics/campaign/{campaign_id}?days=7
```

Returns detailed analytics for specific campaign.

#### Detect Anomalies
```
GET /api/analytics/anomalies/{campaign_id}
```

Returns list of detected performance anomalies.

#### Optimize Budgets
```
POST /api/optimization/budgets?min_roas=1.5&dry_run=true
```

**Parameters:**
- `min_roas`: Minimum ROAS threshold
- `dry_run`: Preview mode (true/false)

#### Pause Underperformers
```
POST /api/optimization/pause-underperformers?min_ctr=0.5&min_spend=100&dry_run=true
```

**Parameters:**
- `min_ctr`: Minimum CTR threshold
- `min_spend`: Minimum spend requirement
- `dry_run`: Preview mode (true/false)

#### Rebalance Portfolio
```
POST /api/optimization/rebalance?total_budget=1000&dry_run=true
```

**Parameters:**
- `total_budget`: Total budget to allocate
- `dry_run`: Preview mode (true/false)

### Using the API with CLI

The REST API can be integrated with command-line tools:

```bash
# Get account info
curl http://localhost:8000/api/account

# List campaigns
curl http://localhost:8000/api/campaigns

# Get analytics
curl http://localhost:8000/api/analytics/overview?days=30

# Optimize budgets (preview)
curl -X POST http://localhost:8000/api/optimization/budgets?dry_run=true&min_roas=2.0
```

### API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Best Practices

### Performance Monitoring

1. **Check Dashboard Daily**
   - Review key metrics each morning
   - Look for unexpected changes
   - Act on anomaly alerts

2. **Weekly Optimization**
   - Run budget optimization weekly
   - Review underperforming campaigns
   - Rebalance portfolio if needed

3. **Monthly Review**
   - Analyze 30-day trends
   - Archive old campaigns
   - Refresh creative library

### Budget Management

1. **Start Conservative**
   - Begin with lower daily budgets
   - Scale up proven performers
   - Use preview mode before applying changes

2. **Set Thresholds**
   - Define minimum acceptable ROAS
   - Set CTR benchmarks for your industry
   - Configure max CPA limits

3. **Monitor Spend**
   - Track spend vs. budget
   - Alert on overspend
   - Pause if budget depleted

### Creative Strategy

1. **Test Variations**
   - A/B test different copy
   - Try multiple images
   - Test various CTAs

2. **Refresh Regularly**
   - Update creatives monthly
   - Rotate images to prevent fatigue
   - Keep messaging fresh

3. **Learn from Data**
   - Identify top performers
   - Duplicate winning creatives
   - Archive poor performers

## Troubleshooting

### Cannot Connect to Dashboard

**Problem**: Browser shows "Connection refused"

**Solution**:
```bash
# Check if server is running
ps aux | grep uvicorn

# Restart server
python run_web.py
```

### API Credentials Error

**Problem**: "Failed to initialize Facebook API client"

**Solution**:
1. Verify `config/config.yaml` exists
2. Check credentials are valid
3. Test with CLI: `python -m fbads campaign list`

### No Data Showing

**Problem**: Dashboard loads but shows no campaigns

**Solution**:
1. Check ad account has campaigns
2. Verify API permissions
3. Check date range selection
4. Review browser console for errors

### Charts Not Displaying

**Problem**: Charts show empty or don't render

**Solution**:
1. Clear browser cache
2. Check JavaScript console for errors
3. Ensure Chart.js is loading
4. Try different browser

## Support

For issues or questions:
1. Check the main README
2. Review QUICKSTART.md
3. Check API documentation at `/docs`
4. Review server logs for errors
