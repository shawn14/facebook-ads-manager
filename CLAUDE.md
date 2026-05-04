# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Facebook Ads Manager is a Python-based tool (Python 3.9+) for programmatically managing Facebook/Meta ad campaigns. It wraps the `facebook-business` SDK and exposes capabilities through three interfaces: a Click-based CLI, a FastAPI web dashboard, and an MCP server.

## Key Commands

```bash
# Setup
source venv/bin/activate
pip install -r requirements.txt

# Web dashboard (http://localhost:8000)
python run_web.py

# CLI (development)
python -m src.cli <command>

# CLI (after pip install -e .)
fbads <command>

# MCP server
python src/mcp_server.py

# Tests
pytest tests/
pytest tests/test_api_client.py::TestCampaignManagement::test_create_campaign_basic
pytest --cov=src --cov-report=term tests/

# Code quality
black src/ tests/
flake8 src/ tests/
mypy src/
```

## Architecture

### Three-tier layered design
1. **Core** (`src/api_client.py`): `FacebookAdsClient` — single source of truth for all Meta API calls. Reads `config/config.yaml` on init. `FB_CONFIG_PATH` env var overrides the config path.
2. **Application layer** (manager modules): business logic wrapping the client
3. **Interfaces**: CLI (`src/cli.py`), web app (`src/web/app.py`), MCP server (`src/mcp_server.py`)

### Key modules

**`src/campaign/manager.py`** — `CampaignManager`: CRUD, budget operations. Input budgets are USD; the API requires cents — manager multiplies by 100 on write, divides on display.

**`src/analytics/reporter.py`** — `AnalyticsReporter`: fetches insights, calculates CTR/CPC/ROAS, generates reports.

**`src/analytics/advanced_analytics.py`** — `AdvancedAnalytics`: time-series analysis, trend detection, anomaly detection, forecasting, and chart exports (matplotlib/seaborn). Caches to `cache/`, exports to `exports/`.

**`src/optimization/optimizer.py`** — `BudgetOptimizer`: performance-based budget rebalancing, pausing underperformers. All mutation methods support `dry_run=True`.

**`src/optimization/ab_testing.py`** — `ABTestManager`: A/B testing with scipy statistical analysis.

**`src/optimization/ml_optimizer.py`** — ML-based campaign optimization (scikit-learn).

**`src/creative/image_generator.py`** — `AIImageGenerator`: generates ad images. Default provider is **Google Gemini 2.5 Flash Image** (`provider: "google"` in config). Falls back to OpenAI DALL-E 3. Factory function `create_image_generator_from_config(config)` reads `ai_image.provider` from config.

**`src/creative/ai_ad_generator.py`** — `AIAdGenerator`: GPT-4-powered ad copy generation (separate from image generation).

**`src/conversion/tracker.py`** — `ConversionTracker`: server-side conversion tracking via Facebook Conversions API. Hashes PII (email, phone, name) with SHA-256. Requires `pixel_id` from Facebook Events Manager.

**`src/targeting/builder.py`** — fluent API for building custom targeting specs.

**`src/targeting/presets.py`** — 14 pre-built targeting presets (e.g., `ecommerce_shoppers`, `tech_enthusiasts`).

**`src/automation/`** — `RulesEngine` (condition-based), `CampaignScheduler` (time-based), `WorkflowAutomation` (multi-step).

**`src/database/`** — SQLAlchemy models and `DatabaseManager` for local caching and historical metrics.

**`src/mcp_server.py`** — MCP server exposing ~25 tools for full Meta Ads account management (campaigns, ad sets, ads, creatives, optimization, reporting). Uses `FastMCP` from `mcp` package. Entry point: `if __name__ == "__main__": mcp.run()`.

### Data flow
```
User → CLI / Web / MCP → Manager → FacebookAdsClient → Meta Marketing API
```

## Configuration

Copy `config/config.example.yaml` → `config/config.yaml` (gitignored).

Critical keys:
- `facebook.app_id/app_secret/access_token/ad_account_id/page_id/pixel_id`
- `facebook.api_version`: currently `v19.0`
- `ai_image.provider`: `"google"` (default) or `"openai"`
- `openai.api_key` / `google.api_key` (or set `OPENAI_API_KEY` / `GOOGLE_API_KEY` env vars)
- `optimization.min_roas/min_ctr/max_cpa`: thresholds used by BudgetOptimizer and RulesEngine
- `analytics.cache_ttl_hours`

**Ad Account ID must include the `act_` prefix**: `act_XXXXXXXXXX`.

## Testing

All tests mock `FacebookAdsClient` — no real credentials or network needed. Fixtures are in `tests/conftest.py`. Tests in `tests/test_integration.py` test complete workflows end-to-end against mocks.

## Automation scripts

`scripts/daily_automation.py`, `scripts/weekly_optimization.py`, `scripts/emergency_pause.py` — designed for cron. All support `--dry-run`.

The root directory contains many one-off setup and diagnostic scripts (`create_*.py`, `configure_*.py`, `check_*.py`, etc.) that were used during initial setup and are not part of the application proper.
