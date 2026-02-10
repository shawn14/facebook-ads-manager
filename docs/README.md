# Facebook Ads Manager Documentation

Complete documentation for the Facebook Ads Manager Python toolkit.

## Quick Links

- **New Users**: Start with [Quick Start Guide](QUICKSTART.md)
- **Developers**: See [API Reference](api-reference.md)
- **Tutorials**: Follow [Step-by-Step Tutorials](tutorials.md)

---

## Documentation Index

### Getting Started

**[Quick Start Guide](QUICKSTART.md)**
- Installation and setup
- First campaign
- Basic usage
- Troubleshooting

**[Tutorials](tutorials.md)**
- Tutorial 1: Your First Campaign
- Tutorial 2: Performance Analysis
- Tutorial 3: Budget Optimization
- Tutorial 4: A/B Testing
- Tutorial 5: Automated Monitoring
- Tutorial 6: Scaling a Winner

### Core Guides

**[Campaign Management](campaign-management.md)**
- Creating and managing campaigns
- Campaign objectives
- Budget management
- Best practices
- Common workflows

**[Analytics & Reporting](analytics.md)**
- Performance metrics
- Generating reports
- Dashboard
- Anomaly detection
- Exporting data
- Advanced analytics

**[Budget Optimization](optimization.md)**
- Automated budget optimization
- Auto-pause underperformers
- Portfolio rebalancing
- Optimization strategies

**[A/B Testing](ab-testing.md)**
- Creating A/B tests
- Statistical significance
- Analyzing results
- Common test types
- Best practices

### Reference

**[API Reference](api-reference.md)**
- FacebookAdsClient
- CampaignManager
- AnalyticsReporter
- BudgetOptimizer
- ABTestManager
- Complete method documentation

**[Architecture Guide](architecture.md)**
- System overview
- Project structure
- Core components
- Data flow
- Configuration
- Extending the system

**[Best Practices](best-practices.md)**
- Campaign setup
- Budget management
- Creative & copy
- Targeting
- Optimization
- Testing
- Monitoring & alerts
- Security
- Team workflows

---

## Documentation by Use Case

### I want to...

**Manage campaigns:**
- [Create a campaign](campaign-management.md#creating-campaigns)
- [Update budget](campaign-management.md#budget-management)
- [Pause/activate campaigns](campaign-management.md#managing-campaigns)
- [Duplicate campaigns](campaign-management.md#duplicating-campaigns)

**Analyze performance:**
- [Generate reports](analytics.md#generating-reports)
- [View dashboard](analytics.md#dashboard)
- [Detect anomalies](analytics.md#anomaly-detection)
- [Export to CSV](analytics.md#exporting-data)

**Optimize campaigns:**
- [Optimize budgets](optimization.md#budget-optimization)
- [Auto-pause underperformers](optimization.md#auto-pause-underperformers)
- [Rebalance portfolio](optimization.md#portfolio-rebalancing)

**Run A/B tests:**
- [Create A/B test](ab-testing.md#creating-ab-tests)
- [Analyze test results](ab-testing.md#analyzing-results)
- [Implement winner](ab-testing.md#best-practices)

**Build automation:**
- [Daily optimization script](tutorials.md#tutorial-5-automated-monitoring)
- [Monitoring & alerts](best-practices.md#monitoring--alerts)
- [Scheduled tasks](optimization.md#strategy-4-scheduled-optimization)

**Learn the system:**
- [Architecture overview](architecture.md#system-overview)
- [Extending the system](architecture.md#extending-the-system)
- [Complete API reference](api-reference.md)

---

## Quick Reference

### Command-Line Examples

```bash
# Campaign Management
python -m src.cli campaign create --name "Campaign Name" --objective CONVERSIONS --budget 100
python -m src.cli campaign list
python -m src.cli campaign pause --id <campaign_id>
python -m src.cli campaign activate --id <campaign_id>

# Analytics
python -m src.cli analytics report --days 7
python -m src.cli analytics report --campaign-id <id> --days 30
python -m src.cli analytics dashboard
python -m src.cli analytics report --format csv

# Optimization
python -m src.cli optimize budgets --min-roas 2.0 --dry-run
python -m src.cli optimize budgets --min-roas 2.0 --no-dry-run
python -m src.cli optimize pause-underperformers --threshold 0.5 --dry-run

# A/B Testing
python -m src.cli test create --campaign-id <id> --variants 3 --name "Test Name"
python -m src.cli test analyze --test-id <id>

# Validation
python -m src.cli validate
```

### Python API Examples

```python
from src.api_client import FacebookAdsClient
from src.campaign.manager import CampaignManager
from src.analytics.reporter import AnalyticsReporter
from src.optimization.optimizer import BudgetOptimizer
from src.optimization.ab_testing import ABTestManager

# Initialize
client = FacebookAdsClient()
manager = CampaignManager(client)
reporter = AnalyticsReporter(client)
optimizer = BudgetOptimizer(client)
ab_test = ABTestManager(client)

# Create campaign
campaign = manager.create_campaign(
    name="My Campaign",
    objective="CONVERSIONS",
    daily_budget=100.00
)

# Get report
report = reporter.campaign_report(campaign['id'], days=7)
reporter.display_report(report)

# Optimize budgets
changes = optimizer.optimize_budgets(min_roas=2.0, dry_run=False)

# Create A/B test
test = ab_test.create_test(
    base_campaign_id=campaign['id'],
    num_variants=2,
    test_name="Creative Test"
)
```

---

## Key Concepts

### Campaign Hierarchy

```
Campaign (Objective: CONVERSIONS)
  ├── Ad Set 1 (Targeting: US 25-45, Budget: $50/day)
  │   ├── Ad 1 (Image ad)
  │   └── Ad 2 (Video ad)
  └── Ad Set 2 (Targeting: US 45-65, Budget: $50/day)
      └── Ad 1 (Carousel ad)
```

### Performance Metrics

- **Impressions**: Times ad was shown
- **Clicks**: Times ad was clicked
- **CTR**: Click-through rate (Clicks / Impressions × 100)
- **Spend**: Total amount spent
- **CPC**: Cost per click (Spend / Clicks)
- **Conversions**: Number of conversion events
- **CPA**: Cost per acquisition (Spend / Conversions)
- **ROAS**: Return on ad spend (Revenue / Spend)

### Optimization Flow

```
1. Create campaigns → 2. Collect data → 3. Analyze performance →
4. Optimize budgets → 5. Test variations → 6. Scale winners →
7. Repeat
```

---

## Configuration

### File Structure

```
facebook-ads-manager/
├── config/
│   ├── config.yaml          # Your configuration (gitignored)
│   └── config.example.yaml  # Template
└── ...
```

### Key Configuration Options

```yaml
facebook:
  app_id: "..."
  app_secret: "..."
  access_token: "..."
  ad_account_id: "act_..."

campaigns:
  min_daily_budget: 10
  max_daily_budget: 5000

optimization:
  min_roas: 1.5      # Minimum ROAS threshold
  min_ctr: 0.5       # Minimum CTR (%)
  max_cpa: 50        # Maximum cost per acquisition
  confidence_level: 0.95  # For A/B testing
```

See [config.example.yaml](../config/config.example.yaml) for complete configuration options.

---

## Common Workflows

### Daily Routine

1. **Morning Check** (9 AM)
   ```bash
   python scripts/daily_optimization.py
   ```

2. **Review Dashboard**
   ```bash
   python scripts/dashboard.py
   ```

3. **Check Alerts**
   ```bash
   python scripts/monitor_campaigns.py
   ```

### Weekly Tasks

1. **Monday: Review Performance**
   ```bash
   python -m src.cli analytics report --days 7
   ```

2. **Wednesday: Analyze A/B Tests**
   ```bash
   python -m src.cli test analyze --test-id <id>
   ```

3. **Friday: Weekly Backup**
   ```bash
   python scripts/weekly_backup.py
   ```

### Monthly Review

1. **Generate Monthly Report**
   ```bash
   python -m src.cli analytics report --days 30 --format csv
   ```

2. **Review All Campaigns**
   - Pause non-performers
   - Scale winners
   - Plan new tests

---

## Troubleshooting

### Common Issues

**"Config file not found"**
```bash
cp config/config.example.yaml config/config.yaml
# Edit config/config.yaml with your credentials
```

**"Invalid credentials"**
- Verify access token hasn't expired
- Check App ID and App Secret
- Ensure Ad Account ID format: `act_XXXXXXXXXX`

**"Campaign not delivering"**
- Check budget (minimum $10/day)
- Verify campaign is ACTIVE
- Review audience size (too small?)
- Check ad approval status

**"Low performance"**
- Review creative quality
- Test different audiences
- Adjust bidding strategy
- Check frequency (< 3 recommended)

See individual guides for more specific troubleshooting.

---

## Support

### Getting Help

1. **Documentation**: Check relevant guide above
2. **Examples**: See [Tutorials](tutorials.md)
3. **API Reference**: [api-reference.md](api-reference.md)
4. **Best Practices**: [best-practices.md](best-practices.md)

### Reporting Issues

For bugs or feature requests:
1. Check documentation first
2. Review [Architecture Guide](architecture.md)
3. Submit issue with details:
   - What you tried
   - Expected behavior
   - Actual behavior
   - Error messages

---

## Version Information

- **Current Version**: 1.0.0
- **API Version**: Facebook Marketing API v19.0
- **Python**: 3.9+
- **Last Updated**: February 2026

---

## Next Steps

**New to the system?**
1. Start with [Quick Start Guide](QUICKSTART.md)
2. Follow [Tutorial 1: Your First Campaign](tutorials.md#tutorial-1-your-first-campaign)
3. Read [Campaign Management Guide](campaign-management.md)

**Ready to optimize?**
1. Review [Analytics Guide](analytics.md)
2. Follow [Budget Optimization Guide](optimization.md)
3. Read [Best Practices](best-practices.md)

**Building automation?**
1. Study [Architecture Guide](architecture.md)
2. Review [API Reference](api-reference.md)
3. Follow [Tutorial 5: Automated Monitoring](tutorials.md#tutorial-5-automated-monitoring)

---

## Contributing

When extending the system:
1. Follow [Architecture Guide](architecture.md#extending-the-system)
2. Add tests
3. Update documentation
4. Follow [Best Practices](best-practices.md)

---

© 2026 Facebook Ads Manager - Internal Use Only
