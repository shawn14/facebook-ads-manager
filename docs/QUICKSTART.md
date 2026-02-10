# Facebook Ads Manager - Quick Start Guide

## Installation

1. **Clone/Navigate to the project**:
   ```bash
   cd ~/projects/facebook-ads-manager
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure credentials**:
   ```bash
   cp config/config.example.yaml config/config.yaml
   ```

5. **Edit `config/config.yaml`** with your Facebook credentials from:
   https://developers.facebook.com/apps/2648986878795029/marketing-api/tools/

## Getting Your Facebook Credentials

1. Go to https://developers.facebook.com/apps/2648986878795029/marketing-api/tools/
2. Copy your:
   - **App ID**: Found in app dashboard
   - **App Secret**: In Settings > Basic
   - **Access Token**: Generate in Marketing API Tools
   - **Ad Account ID**: Format `act_XXXXXXXXXX` from Ads Manager

## Validate Setup

```bash
python -m src.cli validate
```

You should see: ✓ Credentials validated successfully

## Basic Usage

### Campaign Management

```bash
# Create a campaign
python -m src.cli campaign create \
  --name "Q1 2026 Campaign" \
  --objective LINK_CLICKS \
  --budget 100

# List campaigns
python -m src.cli campaign list

# Pause a campaign
python -m src.cli campaign pause --id <campaign_id>

# Activate a campaign
python -m src.cli campaign activate --id <campaign_id>
```

### Analytics

```bash
# Account-level report (last 7 days)
python -m src.cli analytics report

# Campaign-specific report
python -m src.cli analytics report --campaign-id <id> --days 30

# Live dashboard
python -m src.cli analytics dashboard

# Export to CSV
python -m src.cli analytics report --format csv
```

### Budget Optimization

```bash
# Optimize budgets (dry run)
python -m src.cli optimize budgets --min-roas 2.0 --dry-run

# Apply budget optimization
python -m src.cli optimize budgets --min-roas 2.0 --no-dry-run

# Pause underperformers
python -m src.cli optimize pause-underperformers \
  --threshold 0.5 \
  --min-spend 100 \
  --dry-run
```

### A/B Testing

```bash
# Create A/B test
python -m src.cli test create \
  --campaign-id <base_campaign_id> \
  --variants 3 \
  --name "Creative Test Jan 2026"

# Analyze test results
python -m src.cli test analyze --test-id <test_id>
```

## Configuration

Edit `config/config.yaml` to customize:

- Default campaign objectives
- Budget limits (min/max)
- Optimization thresholds (ROAS, CTR, CPA)
- A/B test settings
- Alert preferences

## Next Steps

- Read [Campaign Management Guide](campaign-management.md)
- Learn about [Budget Optimization](optimization.md)
- Set up [A/B Testing](ab-testing.md)
- Explore [Analytics](analytics.md)

## Troubleshooting

### "Config file not found"
Make sure you've copied `config.example.yaml` to `config.yaml` and filled in your credentials.

### "Invalid credentials"
Verify your access token hasn't expired. Generate a new one from the Facebook Marketing API Tools.

### "Campaign not found"
Check the campaign ID format. Use `campaign list` to see all available campaigns.

## Getting Help

```bash
# General help
python -m src.cli --help

# Command-specific help
python -m src.cli campaign --help
python -m src.cli analytics --help
python -m src.cli optimize --help
```
