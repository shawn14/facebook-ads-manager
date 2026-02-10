# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Facebook Ads Manager is a Python-based tool for programmatically managing Facebook ad campaigns with automation, analytics, and optimization capabilities. Built around the Facebook Marketing API (facebook-business SDK), it provides both a CLI interface and a FastAPI-based web dashboard.

**Requirements:** Python 3.9+

## Key Commands

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Launch web dashboard
python run_web.py
# Access at http://localhost:8000

# CLI usage (development mode)
python -m src.cli <command>

# CLI usage (after pip install -e .)
fbads <command>
```

**Note:** Use `python3` instead of `python` if your system requires it. The CLI has two modes:
- **Development mode**: `python -m src.cli` - works immediately after cloning
- **Installed mode**: `fbads` - available after running `pip install -e .` (editable install)

### Testing
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term tests/

# Run specific test file
pytest tests/test_api_client.py

# Run specific test class or function
pytest tests/test_api_client.py::TestCampaignManagement::test_create_campaign_basic

# Run with verbose output
pytest -v tests/

# Run with output captured (show prints)
pytest -s tests/
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Architecture

### Layered Design
The codebase follows a three-tier architecture:

1. **Core Layer** (`src/api_client.py`): Low-level Facebook Marketing API wrapper
2. **Application Layer** (manager modules): Business logic and high-level operations
3. **Interface Layer** (`src/cli.py`, `src/web/app.py`): User-facing interfaces

### Key Components

**FacebookAdsClient** (`src/api_client.py`)
- Single source of truth for all Facebook API interactions
- Handles authentication, error handling, and API initialization
- Provides CRUD operations for campaigns, ad sets, ads, and creatives
- All other modules depend on this client

**Manager Modules** (in `src/*/manager.py`)
- CampaignManager: High-level campaign operations, budget conversion (USD to cents)
- CreativeManager: Ad creative and asset management
- Each manager wraps the API client with business logic and convenience methods

**Analytics & Optimization** (`src/analytics/`, `src/optimization/`)
- AnalyticsReporter: Fetches insights, calculates metrics (CTR, CPC, ROAS), generates reports
- BudgetOptimizer: Automated budget allocation based on performance
- ABTestManager: A/B testing with statistical analysis (scipy)
- ML Optimizer: Machine learning-based campaign optimization

**Automation** (`src/automation/`)
- RulesEngine: Condition-based automation (pause underperformers, scale winners)
- CampaignScheduler: Time-based campaign scheduling
- WorkflowAutomation: Multi-step workflow orchestration

**Database** (`src/database/`)
- DatabaseManager: SQLAlchemy-based data persistence for caching and analytics
- Models: Campaign, AdSet, Ad, and metrics models for local storage
- Used for analytics caching and historical performance tracking

**Web Dashboard** (`src/web/`)
- FastAPI application with Jinja2 templates
- RESTful API endpoints for campaigns, analytics, optimization
- Lazy-loads clients to handle configuration errors gracefully

### Data Flow Pattern
```
User Input → CLI/Web Interface → Manager Module → FacebookAdsClient → Facebook Marketing API
```

## Configuration

### Structure
Configuration is managed through `config/config.yaml` (gitignored). Copy from `config/config.example.yaml` to get started.

**Critical sections:**
- `facebook`: API credentials (app_id, app_secret, access_token, ad_account_id, page_id)
- `campaigns`: Default campaign settings and budgets
- `targeting`: Default targeting parameters
- `optimization`: Thresholds for auto-pause, budget optimization, A/B testing
- `analytics`: Reporting metrics and caching settings

### Budget Handling
All budget amounts in the Facebook API are in **cents**. Manager modules handle conversion:
- User input: USD (dollars)
- Internal/API: cents
- CampaignManager.create_campaign() multiplies by 100
- Display methods divide by 100

### Accessing Configuration
All modules access config through the API client:
```python
self.client.config['optimization']['min_roas']
```

## Module Relationships

### Dependencies
- All managers depend on `FacebookAdsClient`
- CLI depends on all manager modules
- Web app depends on managers (lazy-loaded)
- Tests mock `FacebookAdsClient` to avoid real API calls

### Targeting System
The targeting system is split across two modules:
- `src/targeting/builder.py`: Fluent API for building custom targeting specs
- `src/targeting/presets.py`: Pre-configured targeting presets (14 presets including ecommerce_shoppers, tech_enthusiasts, etc.)

Usage pattern: Build targeting → Pass to create_adset()

## Important Implementation Details

### Error Handling
- Facebook API errors raise `FacebookRequestError` (from facebook-business SDK)
- All modules use loguru for logging
- Configuration errors should be caught early (in __init__ methods)
- API rate limits should be handled with exponential backoff (if implemented)

### Testing Strategy
- All tests mock the Facebook API to avoid real API calls
- Tests don't require credentials or internet connection
- Fixtures in `tests/conftest.py` provide mock data and objects
- Goal: >90% code coverage, 100% on critical paths

### CLI Structure
Built with Click framework:
- Command groups match domain structure (campaign, analytics, optimize, test, etc.)
- Context object passes shared clients between commands
- Rich library for formatted terminal output

### Web Application
- FastAPI with uvicorn server
- Templates in `src/web/templates/`, static files in `src/web/static/`
- Lazy client initialization to handle config errors gracefully
- CORS enabled for all origins (development mode)

## Development Workflow

### Adding a New Feature
1. Extend `FacebookAdsClient` with new API methods (if needed)
2. Create/update manager module with business logic
3. Add CLI commands in `src/cli.py`
4. Add web endpoints in `src/web/app.py` (if needed)
5. Write unit tests in `tests/`
6. Update documentation in `docs/`

### Adding a New Metric
1. Add field to `get_campaign_insights()` or similar method in api_client.py
2. Calculate derived metric in AnalyticsReporter._format_insights()
3. Update display methods to show new metric
4. Add to default_metrics in config.example.yaml

### Testing Changes
- Write unit tests that mock FacebookAdsClient
- Integration tests should test complete workflows
- Use existing fixtures from conftest.py
- Ensure tests remain fast and deterministic

## Special Considerations

### Credentials Security
- Never commit `config/config.yaml` (already in .gitignore)
- Access tokens expire - tokens should be long-lived (60 days)
- Use Facebook Token Debugger to extend tokens

### Facebook API Quirks
- Ad Account ID format: "act_XXXXXXXXXX" (must include "act_" prefix)
- Budgets are in cents, not dollars
- API version is important (currently v19.0)
- Rate limits apply - batch requests when possible

### Automation Scripts
Scripts in `scripts/` directory are meant to be run via cron:
- `daily_automation.py`: Daily optimization and budget adjustments
- `emergency_pause.py`: Immediately pause underperforming campaigns
- `weekly_optimization.py`: Weekly portfolio rebalancing

All automation scripts support `--dry-run` flag for testing.

## Common Patterns

### Creating a Manager Instance
```python
from src.api_client import FacebookAdsClient
from src.campaign.manager import CampaignManager

client = FacebookAdsClient()  # Loads config/config.yaml
manager = CampaignManager(client)
```

### Error Handling Pattern
```python
from facebook_business.exceptions import FacebookRequestError
from loguru import logger

try:
    result = self.client.some_method()
except FacebookRequestError as e:
    logger.error(f"Facebook API error: {e.api_error_message()}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### Lazy Loading Pattern (Web App)
```python
_client = None

def get_client():
    global _client
    if _client is None:
        _client = FacebookAdsClient()
    return _client
```
