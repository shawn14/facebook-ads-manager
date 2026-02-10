# Architecture Guide

Technical overview of the Facebook Ads Manager system architecture.

## Table of Contents

1. [System Overview](#system-overview)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Configuration](#configuration)
6. [Extending the System](#extending-the-system)

---

## System Overview

The Facebook Ads Manager is a Python-based tool that provides a comprehensive interface for managing Facebook ad campaigns programmatically.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
├──────────────────────┬──────────────────────────────────────┤
│   CLI (cli.py)       │   Python API (Direct Import)         │
└──────────┬───────────┴───────────────┬──────────────────────┘
           │                           │
           │        Application Layer  │
           │                           │
┌──────────▼───────────────────────────▼──────────────────────┐
│                    Manager Modules                           │
├──────────────┬──────────────┬──────────────┬────────────────┤
│ Campaign     │ Analytics    │ Budget       │ A/B Test       │
│ Manager      │ Reporter     │ Optimizer    │ Manager        │
└──────────────┴──────────────┴──────────────┴────────────────┘
           │                           │
           │        Core Layer         │
           │                           │
┌──────────▼───────────────────────────▼──────────────────────┐
│              FacebookAdsClient (api_client.py)               │
│           Wrapper for Facebook Marketing API                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │  External API
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                   Facebook Marketing API                     │
│            (facebook-business Python SDK)                    │
└──────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **API Abstraction**: Low-level Facebook API details are abstracted in FacebookAdsClient
3. **Configuration-Driven**: Behavior controlled through YAML configuration
4. **Type Safety**: Type hints throughout for better IDE support
5. **Error Handling**: Comprehensive error handling and logging
6. **Testability**: Modular design allows for easy unit testing

---

## Project Structure

```
facebook-ads-manager/
├── config/
│   ├── config.yaml              # User configuration (gitignored)
│   └── config.example.yaml      # Example configuration template
│
├── src/
│   ├── __init__.py
│   ├── __main__.py              # Entry point for python -m src
│   │
│   ├── api_client.py            # Core: Facebook API wrapper
│   ├── cli.py                   # CLI interface
│   │
│   ├── campaign/
│   │   ├── __init__.py
│   │   └── manager.py           # Campaign management logic
│   │
│   ├── analytics/
│   │   ├── __init__.py
│   │   └── reporter.py          # Analytics and reporting
│   │
│   └── optimization/
│       ├── __init__.py
│       ├── optimizer.py         # Budget optimization
│       └── ab_testing.py        # A/B test management
│
├── docs/                        # Documentation
│   ├── QUICKSTART.md
│   ├── api-reference.md
│   ├── campaign-management.md
│   ├── analytics.md
│   ├── optimization.md
│   ├── ab-testing.md
│   └── architecture.md
│
├── tests/                       # Unit and integration tests
│   ├── test_api_client.py
│   ├── test_campaign_manager.py
│   └── ...
│
├── scripts/                     # Automation scripts
│   └── daily_optimization.py
│
├── exports/                     # CSV/JSON exports (auto-created)
├── logs/                        # Log files (auto-created)
│
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
└── README.md                    # Project overview
```

---

## Core Components

### 1. FacebookAdsClient (`src/api_client.py`)

**Purpose**: Low-level wrapper for the Facebook Marketing API

**Key Responsibilities:**
- Initialize Facebook API connection
- Manage authentication
- Provide CRUD operations for campaigns, ad sets, and ads
- Fetch insights and analytics data
- Handle API errors

**Design:**
```python
class FacebookAdsClient:
    def __init__(self, config_path: str = "config/config.yaml"):
        # Load configuration
        # Initialize Facebook API
        # Set up ad account

    # Campaign methods
    def create_campaign(...) -> Campaign
    def get_campaigns(...) -> List[Campaign]
    def update_campaign(...) -> Campaign

    # Ad Set methods
    def create_adset(...) -> AdSet
    def get_adsets(...) -> List[AdSet]

    # Insights methods
    def get_campaign_insights(...) -> List[Dict]
    def get_account_insights(...) -> List[Dict]

    # Utility methods
    def get_account_info() -> Dict
    def validate_credentials() -> bool
```

**Why this design:**
- Single source of truth for API interactions
- Centralized error handling
- Easier to mock for testing
- Abstraction layer if we need to switch providers

### 2. CampaignManager (`src/campaign/manager.py`)

**Purpose**: High-level campaign management with business logic

**Key Responsibilities:**
- Simplify campaign creation (handle budget conversion, defaults)
- Provide convenience methods (duplicate, bulk operations)
- Implement campaign-related business rules
- Manage campaign lifecycle

**Design:**
```python
class CampaignManager:
    def __init__(self, api_client: FacebookAdsClient):
        self.client = api_client
        self.config = api_client.config

    def create_campaign(...) -> Dict
    def list_campaigns(...) -> List[Dict]
    def update_budget(...) -> None
    def duplicate_campaign(...) -> Dict
    def pause_campaign(...) -> None
    def activate_campaign(...) -> None
```

**Why this design:**
- Separates business logic from API logic
- Handles currency conversion (USD to cents)
- Provides user-friendly interface
- Encapsulates complex workflows

### 3. AnalyticsReporter (`src/analytics/reporter.py`)

**Purpose**: Generate reports and analyze campaign performance

**Key Responsibilities:**
- Fetch and format performance data
- Calculate derived metrics (CTR, CPC, ROAS)
- Detect performance anomalies
- Export data (CSV, JSON)
- Display formatted reports

**Design:**
```python
class AnalyticsReporter:
    def __init__(self, api_client: FacebookAdsClient):
        self.client = api_client
        self.config = api_client.config
        self.console = Console()  # Rich console for formatting

    def campaign_report(...) -> Dict
    def account_report(...) -> List[Dict]
    def display_report(...) -> None
    def export_csv(...) -> str
    def detect_anomalies(...) -> List[Dict]
    def show_dashboard() -> None
```

**Why this design:**
- Separates data fetching from presentation
- Reusable formatting logic
- Multiple output formats (terminal, CSV, JSON)
- Extensible for new metrics

### 4. BudgetOptimizer (`src/optimization/optimizer.py`)

**Purpose**: Automate budget allocation and campaign optimization

**Key Responsibilities:**
- Calculate optimal budgets based on performance
- Pause underperforming campaigns
- Rebalance portfolio budgets
- Enforce budget constraints

**Design:**
```python
class BudgetOptimizer:
    def __init__(self, api_client: FacebookAdsClient):
        self.client = api_client
        self.config = api_client.config

    def optimize_budgets(...) -> List[Dict]
    def pause_underperformers(...) -> List[Dict]
    def rebalance_portfolio(...) -> List[Dict]

    # Private helper methods
    def _calculate_optimal_budget(...) -> float
    def _update_campaign_budget(...) -> None
    def _extract_conversions(...) -> int
```

**Why this design:**
- Encapsulates optimization algorithms
- Dry-run mode for safety
- Configurable thresholds
- Stateless (can be run repeatedly)

### 5. ABTestManager (`src/optimization/ab_testing.py`)

**Purpose**: Manage A/B tests with statistical analysis

**Key Responsibilities:**
- Create test variants
- Collect performance data
- Perform statistical significance testing
- Determine winners

**Design:**
```python
class ABTestManager:
    def __init__(self, api_client: FacebookAdsClient):
        self.client = api_client
        self.config = api_client.config

    def create_test(...) -> Dict
    def analyze_test(...) -> Dict
    def display_results(...) -> None

    # Private helper methods
    def _determine_winner(...) -> Tuple[Optional[str], float]
    def _extract_conversions(...) -> int
```

**Why this design:**
- Statistical rigor (scipy for hypothesis testing)
- Clear separation of test creation and analysis
- Configurable confidence thresholds

### 6. CLI (`src/cli.py`)

**Purpose**: Command-line interface using Click framework

**Key Responsibilities:**
- Parse command-line arguments
- Route commands to appropriate modules
- Format output for terminal
- Handle errors gracefully

**Design:**
```python
@click.group()
def cli():
    """Main CLI group"""

@cli.group()
def campaign():
    """Campaign commands"""

@campaign.command()
def create(...):
    """Create campaign"""

@campaign.command()
def list(...):
    """List campaigns"""

# Similar groups for analytics, optimize, test
```

**Why this design:**
- Click provides excellent UX (help, autocomplete, validation)
- Group-based organization matches domain structure
- Easy to add new commands
- Consistent error handling

---

## Data Flow

### Campaign Creation Flow

```
User Input
    │
    ▼
CLI Command (cli.py)
    │
    ├─> Parse arguments
    ├─> Validate input
    │
    ▼
CampaignManager.create_campaign()
    │
    ├─> Convert budget (USD → cents)
    ├─> Apply defaults from config
    │
    ▼
FacebookAdsClient.create_campaign()
    │
    ├─> Build API request
    ├─> Call Facebook API
    ├─> Handle errors
    │
    ▼
Facebook Marketing API
    │
    ▼
Campaign Created
    │
    ▼
Return campaign data
    │
    ▼
Display to user
```

### Analytics Report Flow

```
User Request
    │
    ▼
CLI/Python API
    │
    ▼
AnalyticsReporter.account_report(days=7)
    │
    ├─> Determine date preset
    │
    ▼
FacebookAdsClient.get_account_insights()
    │
    ├─> Fetch raw insights data
    │
    ▼
AnalyticsReporter._format_insights()
    │
    ├─> Calculate CTR, CPC, ROAS
    ├─> Format numbers
    │
    ▼
Return formatted report
    │
    ├─> display_report() → Terminal
    ├─> export_csv() → CSV file
    └─> Raw data → JSON
```

### Budget Optimization Flow

```
Scheduled Job / User Command
    │
    ▼
BudgetOptimizer.optimize_budgets()
    │
    ├─> Get all ACTIVE campaigns
    │
    ▼
For each campaign:
    │
    ├─> Fetch performance insights
    ├─> Calculate ROAS
    ├─> Determine optimal budget
    ├─> Calculate change percentage
    │
    ▼
Return list of changes
    │
    ├─> dry_run=True → Preview only
    └─> dry_run=False → Apply changes
            │
            ▼
    FacebookAdsClient.update_campaign()
            │
            ▼
    Budgets updated
```

---

## Configuration

### Configuration System

Configuration is managed through YAML files:

**Structure:**
```yaml
# config/config.yaml

facebook:
  app_id: "..."
  app_secret: "..."
  access_token: "..."
  ad_account_id: "act_..."
  api_version: "v19.0"

campaigns:
  default_objective: "LINK_CLICKS"
  min_daily_budget: 10
  max_daily_budget: 5000

optimization:
  min_roas: 1.5
  min_ctr: 0.5
  max_cpa: 50
  confidence_level: 0.95

analytics:
  default_metrics: [...]
  cache_ttl_hours: 1

logging:
  level: "INFO"
  file: "logs/fbads.log"
```

**Loading Configuration:**
```python
# In FacebookAdsClient.__init__
def _load_config(self, config_path: str) -> Dict:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path) as f:
        return yaml.safe_load(f)
```

**Accessing Configuration:**
```python
# Any module can access through client
self.config['optimization']['min_roas']
```

### Environment Variables

For sensitive credentials, use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

config['facebook']['access_token'] = os.getenv('FB_ACCESS_TOKEN')
```

---

## Extending the System

### Adding a New Module

**Example: Adding a Creative Manager**

1. **Create module file:**
   ```python
   # src/creative/manager.py

   class CreativeManager:
       def __init__(self, api_client):
           self.client = api_client
           self.config = api_client.config

       def create_image_ad(self, ...):
           """Create image ad creative"""
           pass

       def create_video_ad(self, ...):
           """Create video ad creative"""
           pass
   ```

2. **Add CLI commands:**
   ```python
   # In src/cli.py

   @cli.group()
   def creative():
       """Creative management commands"""
       pass

   @creative.command()
   @click.option('--image', required=True)
   @click.pass_context
   def create_image(ctx, image):
       """Create image creative"""
       from src.creative.manager import CreativeManager
       manager = CreativeManager(ctx.obj['client'])
       manager.create_image_ad(image)
   ```

3. **Add tests:**
   ```python
   # tests/test_creative_manager.py

   def test_create_image_ad():
       # Mock API client
       # Test creative creation
       pass
   ```

4. **Update documentation:**
   ```markdown
   # docs/creative-management.md

   # Creative Management Guide
   ...
   ```

### Adding a New Metric

**Example: Adding Engagement Rate**

1. **Add to FacebookAdsClient:**
   ```python
   # In api_client.py
   def get_campaign_insights(self, ...):
       if fields is None:
           fields = [
               'impressions', 'clicks', 'spend',
               'post_engagements',  # NEW
               ...
           ]
   ```

2. **Calculate in AnalyticsReporter:**
   ```python
   # In reporter.py
   def _format_insights(self, insight: Dict, ...) -> Dict:
       ...
       # Calculate engagement rate
       impressions = int(insight.get('impressions', 0))
       engagements = int(insight.get('post_engagements', 0))
       engagement_rate = (engagements / impressions * 100) if impressions > 0 else 0

       formatted = {
           ...
           'engagement_rate': engagement_rate,
       }
   ```

3. **Display in reports:**
   ```python
   # In display_report()
   table.add_column("Engagement", justify="right")
   ...
   table.add_row(
       ...
       f"{item['engagement_rate']:.2f}%"
   )
   ```

### Adding a Custom Optimizer

**Example: Time-Based Optimizer**

```python
# src/optimization/time_optimizer.py

from datetime import datetime

class TimeBasedOptimizer:
    """Adjust budgets based on time of day/week"""

    def __init__(self, api_client):
        self.client = api_client

    def optimize_for_time(self):
        """Increase budget during peak hours"""

        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()

        # Peak hours: 9 AM - 9 PM on weekdays
        is_peak = (
            weekday < 5 and  # Monday-Friday
            9 <= hour < 21   # 9 AM - 9 PM
        )

        campaigns = self.client.get_campaigns(filtering=[{
            'field': 'status',
            'operator': 'EQUAL',
            'value': 'ACTIVE'
        }])

        for campaign in campaigns:
            current_budget = int(campaign.get('daily_budget', 0)) / 100

            if is_peak:
                new_budget = current_budget * 1.5  # Increase 50%
            else:
                new_budget = current_budget * 0.5  # Decrease 50%

            # Update budget
            # (implementation details)
```

---

## Error Handling Strategy

### Hierarchy

```
Exception
    │
    ├─> FacebookRequestError (from SDK)
    │   └─> API errors (rate limits, invalid params, etc.)
    │
    ├─> FileNotFoundError
    │   └─> Missing config file
    │
    └─> ValueError
        └─> Invalid parameters
```

### Implementation

```python
# In each module
from facebook_business.exceptions import FacebookRequestError
from loguru import logger

try:
    campaign = self.client.create_campaign(...)
except FacebookRequestError as e:
    logger.error(f"Facebook API error: {e.api_error_message()}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### Logging

```python
# Configure in __init__
from loguru import logger

logger.add(
    "logs/fbads.log",
    rotation="10 MB",
    retention="30 days",
    level="INFO"
)

# Use throughout
logger.info("Campaign created: {name}", name=campaign['name'])
logger.warning("Low ROAS detected: {roas}", roas=roas)
logger.error("Failed to update campaign: {error}", error=str(e))
```

---

## Performance Considerations

### API Rate Limits

Facebook imposes rate limits. Best practices:

1. **Batch requests** where possible
2. **Cache insights data** (config: `cache_ttl_hours`)
3. **Retry with exponential backoff**

```python
import time

def api_call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except FacebookRequestError as e:
            if e.api_error_code() == 17:  # Rate limit
                wait = 2 ** attempt  # Exponential backoff
                time.sleep(wait)
            else:
                raise
```

### Database Layer (Future Enhancement)

For better performance with large accounts:

```python
# Future: src/database/models.py

from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CampaignInsight(Base):
    __tablename__ = 'campaign_insights'

    id = Column(String, primary_key=True)
    campaign_id = Column(String)
    date = Column(DateTime)
    impressions = Column(Integer)
    clicks = Column(Integer)
    spend = Column(Float)
    # ... other metrics

# Cache insights locally
# Query for trends without hitting API
```

---

## Next Steps

- [API Reference](api-reference.md) - Complete API documentation
- [Campaign Management Guide](campaign-management.md) - Usage examples
- [Contributing Guide](../CONTRIBUTING.md) - Development guidelines
