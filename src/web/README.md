# Facebook Ads Manager Web Dashboard

Modern web dashboard for managing Facebook advertising campaigns with real-time analytics and optimization.

## Features

- **Live Dashboard** - Real-time campaign metrics with interactive charts
- **Campaign Management** - Create, edit, pause, and delete campaigns
- **Advanced Analytics** - Detailed performance metrics with anomaly detection
- **Budget Optimization** - Automated budget allocation and optimization
- **Creative Library** - Manage ad creatives and copy variations

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the Dashboard

```bash
# From the project root
python -m src.web.app

# Or use the convenience script
python run_web.py
```

The dashboard will be available at http://localhost:8000

## API Endpoints

### Account
- `GET /api/health` - Health check
- `GET /api/account` - Get account information

### Campaigns
- `GET /api/campaigns` - List all campaigns
- `POST /api/campaigns` - Create a new campaign
- `PUT /api/campaigns/{id}/status` - Update campaign status
- `PUT /api/campaigns/{id}/budget` - Update campaign budget
- `DELETE /api/campaigns/{id}` - Delete a campaign

### Analytics
- `GET /api/analytics/overview` - Account-level analytics
- `GET /api/analytics/campaign/{id}` - Campaign-specific analytics
- `GET /api/analytics/anomalies/{id}` - Detect performance anomalies

### Optimization
- `POST /api/optimization/budgets` - Optimize budget allocation
- `POST /api/optimization/pause-underperformers` - Pause low-performing campaigns
- `POST /api/optimization/rebalance` - Rebalance portfolio

## Pages

### Dashboard (`/`)
- Overview of all campaign performance
- Key metrics (spend, impressions, clicks, ROAS)
- Interactive charts showing spend and ROAS by campaign
- Campaign performance table

### Campaigns (`/campaigns`)
- List all campaigns with filtering
- Create new campaigns
- Edit campaign budgets
- Pause/activate campaigns
- Delete campaigns

### Analytics (`/analytics`)
- Detailed campaign analytics
- Performance anomaly detection
- Conversion funnel visualization
- Time-series performance charts

### Optimization (`/optimization`)
- Budget optimization with preview mode
- Pause underperforming campaigns
- Portfolio rebalancing
- Performance-based budget allocation

### Creative Library (`/creatives`)
- Browse ad creatives
- Upload new creatives
- View creative performance
- Duplicate and edit creatives

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, Tailwind CSS, Alpine.js
- **Charts**: Chart.js
- **API**: Facebook Marketing API

## Configuration

Ensure your `config/config.yaml` is properly configured with:
- Facebook App ID
- Facebook App Secret
- Access Token
- Ad Account ID

## Development

### Running in Development Mode

```bash
# With auto-reload
uvicorn src.web.app:app --reload --host 0.0.0.0 --port 8000
```

### Project Structure

```
src/web/
├── app.py              # FastAPI application
├── templates/          # Jinja2 templates
│   ├── base.html       # Base template
│   ├── index.html      # Dashboard
│   ├── campaigns.html  # Campaign management
│   ├── analytics.html  # Analytics
│   ├── optimization.html # Optimization
│   └── creatives.html  # Creative library
└── static/             # Static files
    └── img/            # Images
```

## CLI Integration

The web dashboard uses the same backend modules as the CLI:
- All API endpoints can be used by the CLI
- REST API allows for programmatic access
- Shared configuration and authentication

## Notes

- The dashboard requires valid Facebook API credentials
- Ensure your ad account has appropriate permissions
- Budget changes can be previewed before applying
- All optimization actions support dry-run mode
