# API Reference

Complete reference documentation for the Facebook Ads Manager Python library.

## Table of Contents

- [FacebookAdsClient](#facebookadsclient)
- [CampaignManager](#campaignmanager)
- [AnalyticsReporter](#analyticsreporter)
- [BudgetOptimizer](#budgetoptimizer)
- [ABTestManager](#abtestmanager)

---

## FacebookAdsClient

Core client for interacting with the Facebook Marketing API.

### Initialization

```python
from src.api_client import FacebookAdsClient

# Initialize with default config path
client = FacebookAdsClient()

# Initialize with custom config
client = FacebookAdsClient(config_path="path/to/config.yaml")
```

### Methods

#### Campaign Management

##### `create_campaign(name, objective, status='PAUSED', special_ad_categories=None)`

Create a new ad campaign.

**Parameters:**
- `name` (str): Campaign name
- `objective` (str): Campaign objective. Valid values:
  - `LINK_CLICKS` - Drive traffic to website
  - `CONVERSIONS` - Optimize for conversions
  - `BRAND_AWARENESS` - Increase brand awareness
  - `REACH` - Maximize reach
  - `APP_INSTALLS` - Drive app installations
- `status` (str, optional): Initial status. Default: `'PAUSED'`
  - `'ACTIVE'` - Campaign is running
  - `'PAUSED'` - Campaign is paused
- `special_ad_categories` (List[str], optional): Required for certain ad types (e.g., housing, employment)

**Returns:** Campaign object

**Example:**
```python
campaign = client.create_campaign(
    name="Q1 2026 Lead Gen",
    objective="CONVERSIONS",
    status="PAUSED"
)
print(f"Created campaign ID: {campaign['id']}")
```

##### `get_campaigns(fields=None, filtering=None)`

Retrieve campaigns for the ad account.

**Parameters:**
- `fields` (List[str], optional): Fields to retrieve. Defaults to standard fields
- `filtering` (List[Dict], optional): Filter conditions

**Returns:** List of Campaign objects

**Example:**
```python
# Get all campaigns
campaigns = client.get_campaigns()

# Get active campaigns only
active_campaigns = client.get_campaigns(
    filtering=[{
        'field': 'status',
        'operator': 'EQUAL',
        'value': 'ACTIVE'
    }]
)
```

##### `update_campaign(campaign_id, updates)`

Update a campaign.

**Parameters:**
- `campaign_id` (str): Campaign ID
- `updates` (Dict[str, Any]): Dictionary of fields to update

**Returns:** Updated Campaign object

**Example:**
```python
client.update_campaign(
    campaign_id="123456789",
    updates={
        'name': 'Updated Campaign Name',
        'status': 'ACTIVE'
    }
)
```

##### `pause_campaign(campaign_id)`

Pause a campaign.

**Parameters:**
- `campaign_id` (str): Campaign ID

**Returns:** Updated Campaign object

**Example:**
```python
client.pause_campaign("123456789")
```

##### `activate_campaign(campaign_id)`

Activate a campaign.

**Parameters:**
- `campaign_id` (str): Campaign ID

**Returns:** Updated Campaign object

**Example:**
```python
client.activate_campaign("123456789")
```

##### `delete_campaign(campaign_id)`

Delete a campaign.

**Parameters:**
- `campaign_id` (str): Campaign ID

**Returns:** None

**Example:**
```python
client.delete_campaign("123456789")
```

#### Ad Set Management

##### `create_adset(campaign_id, name, daily_budget, targeting, optimization_goal='LINK_CLICKS', billing_event='IMPRESSIONS', bid_strategy='LOWEST_COST_WITHOUT_CAP', status='PAUSED')`

Create a new ad set.

**Parameters:**
- `campaign_id` (str): Parent campaign ID
- `name` (str): Ad set name
- `daily_budget` (int): Daily budget in cents (e.g., 5000 = $50.00)
- `targeting` (Dict): Targeting specification (see Targeting section below)
- `optimization_goal` (str, optional): Optimization goal. Default: `'LINK_CLICKS'`
- `billing_event` (str, optional): Billing event. Default: `'IMPRESSIONS'`
- `bid_strategy` (str, optional): Bid strategy. Default: `'LOWEST_COST_WITHOUT_CAP'`
- `status` (str, optional): Initial status. Default: `'PAUSED'`

**Returns:** AdSet object

**Example:**
```python
targeting = {
    'geo_locations': {'countries': ['US']},
    'age_min': 25,
    'age_max': 65,
    'genders': [1, 2],  # 1=Male, 2=Female
    'interests': [{'id': '6003107902433', 'name': 'Technology'}]
}

adset = client.create_adset(
    campaign_id="123456789",
    name="Ad Set 1",
    daily_budget=5000,  # $50.00
    targeting=targeting,
    optimization_goal="CONVERSIONS",
    status="ACTIVE"
)
```

##### `get_adsets(campaign_id=None, fields=None)`

Get ad sets.

**Parameters:**
- `campaign_id` (str, optional): Filter by campaign ID
- `fields` (List[str], optional): Fields to retrieve

**Returns:** List of AdSet objects

**Example:**
```python
# Get all ad sets for a campaign
adsets = client.get_adsets(campaign_id="123456789")
```

#### Analytics and Insights

##### `get_campaign_insights(campaign_id, date_preset='last_7d', fields=None)`

Get performance insights for a campaign.

**Parameters:**
- `campaign_id` (str): Campaign ID
- `date_preset` (str, optional): Date range preset. Default: `'last_7d'`
  - `'today'` - Today
  - `'yesterday'` - Yesterday
  - `'last_7d'` - Last 7 days
  - `'last_14d'` - Last 14 days
  - `'last_30d'` - Last 30 days
  - `'last_90d'` - Last 90 days
  - `'lifetime'` - All time
- `fields` (List[str], optional): Metrics to retrieve

**Returns:** List of insight dictionaries

**Example:**
```python
insights = client.get_campaign_insights(
    campaign_id="123456789",
    date_preset="last_30d",
    fields=['impressions', 'clicks', 'spend', 'ctr', 'conversions']
)

if insights:
    data = insights[0]
    print(f"Impressions: {data['impressions']}")
    print(f"Clicks: {data['clicks']}")
    print(f"Spend: ${data['spend']}")
```

##### `get_account_insights(date_preset='last_7d', level='campaign', fields=None)`

Get account-level insights.

**Parameters:**
- `date_preset` (str, optional): Date range preset. Default: `'last_7d'`
- `level` (str, optional): Aggregation level. Default: `'campaign'`
  - `'account'` - Account level
  - `'campaign'` - Campaign level
  - `'adset'` - Ad set level
  - `'ad'` - Ad level
- `fields` (List[str], optional): Metrics to retrieve

**Returns:** List of insight dictionaries

**Example:**
```python
insights = client.get_account_insights(
    date_preset="last_7d",
    level="campaign"
)

for insight in insights:
    print(f"{insight['campaign_name']}: ${insight['spend']}")
```

#### Utility Methods

##### `get_account_info()`

Get ad account information.

**Returns:** Dictionary with account information

**Example:**
```python
account = client.get_account_info()
print(f"Account: {account['name']}")
print(f"Currency: {account['currency']}")
print(f"Balance: ${account['balance']}")
```

##### `validate_credentials()`

Validate API credentials.

**Returns:** Boolean indicating success

**Example:**
```python
if client.validate_credentials():
    print("Credentials are valid!")
else:
    print("Invalid credentials")
```

---

## CampaignManager

Higher-level campaign management with convenience methods.

### Initialization

```python
from src.api_client import FacebookAdsClient
from src.campaign.manager import CampaignManager

client = FacebookAdsClient()
manager = CampaignManager(client)
```

### Methods

##### `create_campaign(name, objective, daily_budget, status='PAUSED', special_ad_categories=None)`

Create a campaign with simplified budget handling.

**Parameters:**
- `name` (str): Campaign name
- `objective` (str): Campaign objective
- `daily_budget` (float): Daily budget in USD (automatically converted to cents)
- `status` (str, optional): Initial status. Default: `'PAUSED'`
- `special_ad_categories` (List[str], optional): Special ad categories

**Returns:** Campaign dictionary

**Example:**
```python
campaign = manager.create_campaign(
    name="Spring Sale 2026",
    objective="CONVERSIONS",
    daily_budget=100.00,  # $100 USD
    status="ACTIVE"
)
```

##### `list_campaigns(status_filter=None, include_insights=False)`

List campaigns with optional filtering.

**Parameters:**
- `status_filter` (str, optional): Filter by status
- `include_insights` (bool, optional): Include performance data. Default: `False`

**Returns:** List of campaign dictionaries

**Example:**
```python
# Get all active campaigns with insights
campaigns = manager.list_campaigns(
    status_filter="ACTIVE",
    include_insights=True
)

for camp in campaigns:
    print(f"{camp['name']}: ROAS = {camp['insights'].get('roas', 0):.2f}")
```

##### `update_budget(campaign_id, new_budget)`

Update campaign budget.

**Parameters:**
- `campaign_id` (str): Campaign ID
- `new_budget` (float): New daily budget in USD

**Example:**
```python
manager.update_budget("123456789", 150.00)  # Increase to $150/day
```

##### `duplicate_campaign(campaign_id, new_name=None)`

Duplicate an existing campaign.

**Parameters:**
- `campaign_id` (str): Source campaign ID
- `new_name` (str, optional): Name for duplicated campaign

**Returns:** New campaign dictionary

**Example:**
```python
new_campaign = manager.duplicate_campaign(
    campaign_id="123456789",
    new_name="Q2 2026 Campaign"
)
```

---

## AnalyticsReporter

Generate analytics reports and dashboards.

### Initialization

```python
from src.api_client import FacebookAdsClient
from src.analytics.reporter import AnalyticsReporter

client = FacebookAdsClient()
reporter = AnalyticsReporter(client)
```

### Methods

##### `campaign_report(campaign_id, days=7)`

Generate a performance report for a single campaign.

**Parameters:**
- `campaign_id` (str): Campaign ID
- `days` (int, optional): Number of days to analyze. Default: `7`

**Returns:** Report dictionary

**Example:**
```python
report = reporter.campaign_report("123456789", days=30)

print(f"Campaign: {report['campaign_name']}")
print(f"Impressions: {report['impressions']:,}")
print(f"Clicks: {report['clicks']:,}")
print(f"CTR: {report['ctr']:.2f}%")
print(f"Spend: ${report['spend']:.2f}")
print(f"ROAS: {report['roas']:.2f}x")
```

##### `account_report(days=7)`

Generate account-level performance report.

**Parameters:**
- `days` (int, optional): Number of days to analyze. Default: `7`

**Returns:** List of campaign report dictionaries

**Example:**
```python
reports = reporter.account_report(days=7)

for report in reports:
    print(f"{report['campaign_name']}: ${report['spend']:.2f} spent, {report['roas']:.2f}x ROAS")
```

##### `display_report(data)`

Display report in terminal with formatted table.

**Parameters:**
- `data` (Dict or List[Dict]): Report data to display

**Example:**
```python
report = reporter.account_report(days=7)
reporter.display_report(report)
```

##### `show_dashboard()`

Display live performance dashboard in terminal.

**Example:**
```python
reporter.show_dashboard()
```

##### `export_csv(data, filename=None)`

Export report data to CSV file.

**Parameters:**
- `data` (Dict or List[Dict]): Report data
- `filename` (str, optional): Output filename (auto-generated if not provided)

**Returns:** Path to exported file

**Example:**
```python
report = reporter.account_report(days=30)
filepath = reporter.export_csv(report, filename="monthly_report.csv")
print(f"Report saved to: {filepath}")
```

##### `detect_anomalies(campaign_id)`

Detect performance anomalies for a campaign.

**Parameters:**
- `campaign_id` (str): Campaign ID

**Returns:** List of detected anomalies

**Example:**
```python
anomalies = reporter.detect_anomalies("123456789")

for anomaly in anomalies:
    print(f"{anomaly['severity'].upper()}: {anomaly['message']}")
```

---

## BudgetOptimizer

Optimize budget allocation based on performance.

### Initialization

```python
from src.api_client import FacebookAdsClient
from src.optimization.optimizer import BudgetOptimizer

client = FacebookAdsClient()
optimizer = BudgetOptimizer(client)
```

### Methods

##### `optimize_budgets(min_roas=None, dry_run=True)`

Optimize budget allocation across campaigns.

**Parameters:**
- `min_roas` (float, optional): Minimum ROAS threshold. Uses config default if not specified
- `dry_run` (bool, optional): Preview changes without applying. Default: `True`

**Returns:** List of budget change dictionaries

**Example:**
```python
# Preview optimization
changes = optimizer.optimize_budgets(min_roas=2.0, dry_run=True)

for change in changes:
    print(f"{change['campaign_name']}:")
    print(f"  Current: ${change['old_budget']:.2f}")
    print(f"  New: ${change['new_budget']:.2f}")
    print(f"  Change: {change['change_pct']:+.1f}%")
    print(f"  Reason: {change['reason']}")

# Apply optimization
optimizer.optimize_budgets(min_roas=2.0, dry_run=False)
```

##### `pause_underperformers(min_ctr=0.5, min_spend=100, dry_run=True)`

Automatically pause underperforming campaigns.

**Parameters:**
- `min_ctr` (float, optional): Minimum CTR threshold (%). Default: `0.5`
- `min_spend` (float, optional): Minimum spend to evaluate. Default: `100`
- `dry_run` (bool, optional): Preview without pausing. Default: `True`

**Returns:** List of paused campaign dictionaries

**Example:**
```python
# Pause campaigns with CTR < 0.3% and spend > $200
paused = optimizer.pause_underperformers(
    min_ctr=0.3,
    min_spend=200,
    dry_run=False
)

for item in paused:
    print(f"Paused: {item['campaign_name']}")
    print(f"  CTR: {item['ctr']:.2f}%")
    print(f"  Reason: {item['reason']}")
```

##### `rebalance_portfolio(total_budget, dry_run=True)`

Rebalance budget across all campaigns to maximize ROI.

**Parameters:**
- `total_budget` (float): Total budget to allocate (USD)
- `dry_run` (bool, optional): Preview without applying. Default: `True`

**Returns:** List of allocation dictionaries

**Example:**
```python
# Allocate $1000/day across all campaigns based on ROAS
allocations = optimizer.rebalance_portfolio(
    total_budget=1000.00,
    dry_run=False
)

for allocation in allocations:
    print(f"{allocation['campaign_name']}: ${allocation['new_budget']:.2f} (ROAS: {allocation['roas']:.2f}x)")
```

---

## ABTestManager

Manage A/B tests for ad campaigns.

### Initialization

```python
from src.api_client import FacebookAdsClient
from src.optimization.ab_testing import ABTestManager

client = FacebookAdsClient()
ab_test = ABTestManager(client)
```

### Methods

##### `create_test(base_campaign_id, num_variants, test_name, budget_split='even')`

Create a new A/B test.

**Parameters:**
- `base_campaign_id` (str): Base campaign to test
- `num_variants` (int): Number of variants to create
- `test_name` (str): Name for the test
- `budget_split` (str, optional): Budget allocation strategy. Default: `'even'`

**Returns:** Test configuration dictionary

**Example:**
```python
test = ab_test.create_test(
    base_campaign_id="123456789",
    num_variants=3,
    test_name="Creative Test - February 2026"
)

print(f"Test ID: {test['id']}")
print(f"Created {len(test['variants'])} variants")
```

##### `analyze_test(test_id, metric='conversions')`

Analyze A/B test results with statistical significance.

**Parameters:**
- `test_id` (str): Test ID
- `metric` (str, optional): Metric to analyze. Default: `'conversions'`
  - `'conversions'` - Conversion rate
  - `'ctr'` - Click-through rate

**Returns:** Analysis results dictionary

**Example:**
```python
results = ab_test.analyze_test("test_123456789_3", metric="conversions")

if results['winner']:
    print(f"Winner: {results['winner']}")
    print(f"Confidence: {results['confidence'] * 100:.1f}%")
else:
    print("No statistically significant winner yet")
```

##### `display_results(results)`

Display test results in formatted table.

**Parameters:**
- `results` (Dict): Test analysis results

**Example:**
```python
results = ab_test.analyze_test("test_123456789_3")
ab_test.display_results(results)
```

---

## Targeting Specification

Targeting parameters for ad sets:

```python
targeting = {
    # Geographic targeting
    'geo_locations': {
        'countries': ['US', 'CA'],  # Country codes
        'regions': [{'key': '3847'}],  # Region IDs
        'cities': [{'key': '2418779', 'radius': 10, 'distance_unit': 'mile'}],
        'zips': [{'key': 'US:90210'}]
    },

    # Demographics
    'age_min': 25,
    'age_max': 65,
    'genders': [1, 2],  # 1=Male, 2=Female

    # Interests
    'interests': [
        {'id': '6003107902433', 'name': 'Technology'},
        {'id': '6003139266461', 'name': 'Shopping'}
    ],

    # Behaviors
    'behaviors': [
        {'id': '6002714895372', 'name': 'Early adopters'}
    ],

    # Exclusions
    'excluded_geo_locations': {
        'countries': ['CN']
    },

    # Custom audiences
    'custom_audiences': [{'id': '123456789'}],
    'excluded_custom_audiences': [{'id': '987654321'}],

    # Device targeting
    'device_platforms': ['mobile', 'desktop'],
    'publisher_platforms': ['facebook', 'instagram', 'messenger']
}
```

---

## Error Handling

All methods may raise exceptions. Wrap API calls in try-except blocks:

```python
from facebook_business.exceptions import FacebookRequestError

try:
    campaign = client.create_campaign(
        name="Test Campaign",
        objective="CONVERSIONS"
    )
except FacebookRequestError as e:
    print(f"API Error: {e.api_error_message()}")
    print(f"Error Code: {e.api_error_code()}")
except FileNotFoundError as e:
    print(f"Config error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Configuration Reference

See `config/config.example.yaml` for all available configuration options:

- **facebook**: API credentials
- **campaigns**: Default campaign settings
- **targeting**: Default targeting parameters
- **optimization**: Auto-pause and budget optimization settings
- **analytics**: Reporting defaults
- **reporting**: Alert settings

---

## Next Steps

- [Campaign Management Guide](campaign-management.md)
- [Analytics Guide](analytics.md)
- [Budget Optimization Guide](optimization.md)
- [A/B Testing Guide](ab-testing.md)
