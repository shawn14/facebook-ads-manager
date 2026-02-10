# Facebook Ads Manager

Comprehensive Python-based tool for managing Facebook ad campaigns with automation, analytics, and optimization.

## Features

- 🚀 **Campaign Management** - Create, update, and manage ad campaigns programmatically
- 📊 **Analytics & Reporting** - Track performance metrics, ROI, and conversions
- 🧪 **A/B Testing** - Automated creative and copy testing with statistical analysis
- 💰 **Budget Optimization** - Automatic budget allocation based on performance
- 📈 **Performance Insights** - Real-time dashboards and detailed reports
- 🤖 **Automation** - Schedule campaigns, auto-pause underperformers, smart bidding
- 🌐 **Web Dashboard** - Modern web interface with live metrics and interactive charts

## Quick Start

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Facebook API credentials
cp config/config.example.yaml config/config.yaml
# Edit config/config.yaml with your credentials
```

### Configuration

1. Get your Facebook App credentials from: https://developers.facebook.com/apps/2648986878795029/marketing-api/tools/
2. Add to `config/config.yaml`:
   - App ID
   - App Secret
   - Access Token
   - Ad Account ID

### Web Dashboard

Launch the modern web interface:

```bash
python run_web.py
```

Access at: http://localhost:8000

Features:
- Live campaign metrics and charts
- Campaign management UI
- Budget optimization controls
- Analytics dashboards
- Creative library

### CLI Usage

```bash
# Campaign management
python -m src.cli campaign create --name "Q1 Campaign" --budget 1000
python -m src.cli campaign list
python -m src.cli campaign pause --id <campaign_id>

# Analytics
python -m src.cli analytics report --campaign-id <id> --days 7
python -m src.cli analytics dashboard

# A/B Testing
python -m src.cli test create --campaign-id <id> --variants 3
python -m src.cli test analyze --test-id <id>

# Budget optimization
python -m src.cli optimize budgets --min-roas 2.0
python -m src.cli optimize pause-underperformers --threshold 0.5
```

**Note:** After running `pip install -e .`, you can use `fbads` instead of `python -m src.cli`.

## Project Structure

```
facebook-ads-manager/
├── src/
│   ├── campaign/          # Campaign creation and management
│   ├── creative/          # Ad creative and copy management
│   ├── analytics/         # Performance tracking and reporting
│   ├── optimization/      # Budget and bid optimization
│   ├── web/               # Web dashboard (FastAPI)
│   │   ├── app.py         # FastAPI application
│   │   ├── templates/     # HTML templates
│   │   └── static/        # CSS, JS, images
│   ├── api_client.py      # Facebook Marketing API wrapper
│   ├── cli.py             # Command-line interface
│   └── utils.py           # Shared utilities
├── config/
│   ├── config.yaml        # Main configuration (gitignored)
│   └── config.example.yaml # Example configuration
├── scripts/               # Automation scripts
├── docs/                  # Documentation
├── tests/                 # Unit and integration tests
├── requirements.txt       # Python dependencies
├── run_web.py             # Web dashboard launcher
└── README.md
```

## Documentation

See `docs/` for detailed guides:
- [Quick Start Guide](docs/QUICKSTART.md)
- [Web Dashboard Guide](docs/WEB_DASHBOARD.md)
- [Campaign Management](docs/campaign-management.md)
- [Analytics Guide](docs/analytics.md)
- [A/B Testing](docs/ab-testing.md)
- [Budget Optimization](docs/optimization.md)
- [API Reference](docs/api-reference.md)

## Requirements

- Python 3.9+
- Facebook Business Manager account
- Facebook App with Marketing API access
- Ad account with appropriate permissions

## License

Private - Internal use only
