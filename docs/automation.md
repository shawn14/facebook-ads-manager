# Automation Guide

Complete guide to automation features in Facebook Ads Manager.

## Table of Contents

1. [Rules Engine](#rules-engine)
2. [Campaign Scheduler](#campaign-scheduler)
3. [Pre-built Workflows](#pre-built-workflows)
4. [Automation Scripts](#automation-scripts)
5. [Best Practices](#best-practices)

---

## Rules Engine

The rules engine allows you to define automated actions based on campaign performance metrics.

### Creating Rules

Rules consist of:
- **Conditions**: Metric thresholds to evaluate (e.g., CTR < 0.5%)
- **Actions**: What to do when conditions are met (e.g., pause campaign)
- **Schedule**: When to check the rule (cron expression)

### Configuration

Edit `config/rules.yaml`:

```yaml
rules:
  - name: "Pause Low CTR Campaigns"
    enabled: true
    entity_type: "campaign"
    all_conditions: true  # AND all conditions
    conditions:
      - metric: "ctr"
        operator: "<"
        value: 0.5
      - metric: "spend"
        operator: ">"
        value: 100
    actions:
      - action_type: "pause_campaign"
      - action_type: "send_alert"
        parameters:
          message: "Campaign paused due to low CTR"
    schedule: "0 9 * * *"  # Daily at 9 AM
```

### Available Operators

- `>` - Greater than
- `<` - Less than
- `>=` - Greater than or equal
- `<=` - Less than or equal
- `==` - Equal
- `!=` - Not equal
- `contains` - String contains
- `not_contains` - String does not contain

### Available Actions

- `pause_campaign` - Pause the campaign
- `activate_campaign` - Activate the campaign
- `update_budget` - Set budget to specific value
- `increase_budget` - Increase budget by percentage
- `decrease_budget` - Decrease budget by percentage
- `send_alert` - Send notification
- `pause_adset` - Pause ad set
- `activate_adset` - Activate ad set

### Available Metrics

- `spend` - Total spend
- `impressions` - Number of impressions
- `clicks` - Number of clicks
- `ctr` - Click-through rate (%)
- `cpc` - Cost per click
- `conversions` - Number of conversions
- `cost_per_conversion` - Cost per conversion
- `roas` - Return on ad spend
- `reach` - Unique reach
- `frequency` - Average frequency

### Using Rules via CLI

```bash
# List all rules
python -m fbads automate list-rules

# Execute rules (dry run)
python -m fbads automate run-rules --dry-run

# Execute rules (live)
python -m fbads automate run-rules
```

---

## Campaign Scheduler

Schedule campaigns to start/pause at specific times or on recurring schedules.

### Schedule Types

- **One-time**: Execute once at specified time
- **Daily**: Repeat every day
- **Weekly**: Repeat every week
- **Monthly**: Repeat every month
- **Cron**: Custom schedule using cron expression

### CLI Commands

```bash
# List scheduled events
python -m fbads automate schedule-list

# View upcoming events (next 24 hours)
python -m fbads automate schedule-list --upcoming 24

# View calendar
python -m fbads automate calendar --days 30

# Execute pending scheduled events
python -m fbads automate run-scheduled --dry-run
python -m fbads automate run-scheduled  # Live
```

### Programmatic Usage

```python
from src.automation.scheduler import CampaignScheduler, ScheduleType
from datetime import datetime, timedelta

scheduler = CampaignScheduler(client)

# Schedule campaign to start tomorrow at 9 AM
start_time = datetime.now().replace(hour=9, minute=0) + timedelta(days=1)
scheduler.schedule_campaign_start(
    campaign_id="123456",
    start_time=start_time,
    name="Launch Q1 Campaign"
)

# Schedule recurring daily rules execution
scheduler.schedule_recurring_rules(
    schedule_type=ScheduleType.RECURRING_DAILY,
    start_time=datetime.now().replace(hour=8, minute=0),
    name="Daily automation rules"
)

# View calendar
calendar = scheduler.get_calendar_view(days=30)
for date, events in calendar.items():
    print(f"{date}: {len(events)} events")
```

---

## Pre-built Workflows

Ready-to-use workflows for common automation tasks.

### 1. Daily Performance Check

Automatically checks campaigns daily and:
- Pauses campaigns with very low CTR
- Reduces budget for low ROAS campaigns
- Increases budget for high performers
- Alerts on spending anomalies

```bash
# CLI
python -m fbads workflow daily-check --dry-run

# Python
from src.automation.workflows import WorkflowAutomation

workflows = WorkflowAutomation(client)
results = workflows.daily_performance_check(dry_run=False)
```

### 2. Campaign Health Report

Generates comprehensive health scores and recommendations:

```bash
python -m fbads workflow health-report
```

### 3. Scale Winners

Automatically scale up budget for high-performing campaigns:

```bash
python -m fbads workflow scale-winners \
    --min-roas 2.0 \
    --scale-factor 1.5 \
    --dry-run
```

### 4. Emergency Pause

Immediately pause all active campaigns:

```bash
python -m fbads workflow emergency-pause \
    --reason "Emergency maintenance" \
    --dry-run
```

### 5. Smart Budget Rebalance

Reallocate budget across campaigns based on performance:

```python
workflows = WorkflowAutomation(client)
results = workflows.smart_budget_rebalance(
    total_budget=10000,  # $10k daily budget
    dry_run=False
)
```

### 6. Campaign Refresh

Duplicate and replace campaign to combat ad fatigue:

```python
results = workflows.campaign_refresh(
    campaign_id="123456",
    dry_run=False
)
```

---

## Automation Scripts

Production-ready scripts for scheduled execution.

### Daily Automation Script

**File**: `scripts/daily_automation.py`

Runs daily to:
1. Execute scheduled events
2. Run automation rules
3. Perform performance checks
4. Generate health reports

```bash
# Manual execution
python scripts/daily_automation.py --dry-run

# Cron setup (daily at 9 AM)
0 9 * * * cd /path/to/facebook-ads-manager && \
  python scripts/daily_automation.py >> logs/automation.log 2>&1
```

### Weekly Optimization Script

**File**: `scripts/weekly_optimization.py`

Runs weekly for deeper optimization:
1. Generate comprehensive health report
2. Scale winning campaigns
3. Rebalance portfolio budgets
4. Optimize individual campaigns

```bash
# Manual execution
python scripts/weekly_optimization.py --total-budget 10000 --dry-run

# Cron setup (every Monday at 9 AM)
0 9 * * 1 cd /path/to/facebook-ads-manager && \
  python scripts/weekly_optimization.py --total-budget 10000 >> logs/weekly.log 2>&1
```

### Emergency Pause Script

**File**: `scripts/emergency_pause.py`

Immediately pause all campaigns:

```bash
python scripts/emergency_pause.py --reason "Billing issue" --dry-run
```

---

## Best Practices

### 1. Always Test with Dry Run First

```bash
# Test before applying
python -m fbads automate run-rules --dry-run
```

### 2. Start with Conservative Thresholds

Example rules configuration:

```yaml
# Good: Conservative thresholds
conditions:
  - metric: "ctr"
    operator: "<"
    value: 0.3  # Very low threshold
  - metric: "spend"
    operator: ">"
    value: 200  # Significant spend

# Avoid: Too aggressive
conditions:
  - metric: "ctr"
    operator: "<"
    value: 1.0  # May pause good campaigns
  - metric: "spend"
    operator: ">"
    value: 10   # Too early to judge
```

### 3. Monitor Rule Execution

Check logs regularly:

```bash
tail -f logs/rule_executions.json
tail -f logs/daily_automation.log
```

### 4. Use Alerts for Critical Actions

Always include alerts for important actions:

```yaml
actions:
  - action_type: "pause_campaign"
  - action_type: "send_alert"
    parameters:
      message: "Campaign paused - review needed"
```

### 5. Schedule Rules at Off-Peak Times

Avoid running automation during high-traffic periods:

```yaml
schedule: "0 2 * * *"  # 2 AM (off-peak)
```

### 6. Combine Multiple Conditions

Use `all_conditions: true` for AND logic:

```yaml
all_conditions: true  # All must be true
conditions:
  - metric: "ctr"
    operator: "<"
    value: 0.5
  - metric: "spend"
    operator: ">"
    value: 100
  - metric: "conversions"
    operator: "=="
    value: 0
```

### 7. Regular Backup

Backup your configuration:

```bash
cp config/rules.yaml config/rules.backup.yaml
cp config/schedule.json config/schedule.backup.json
```

### 8. Gradual Budget Changes

Avoid sudden large changes:

```yaml
# Good: 20% increase
- action_type: "increase_budget"
  parameters:
    percent: 20

# Avoid: 200% increase
- action_type: "increase_budget"
  parameters:
    percent: 200
```

### 9. Set Budget Caps

Always enforce maximum budgets in config:

```yaml
campaigns:
  max_daily_budget: 5000  # $5k daily cap
```

### 10. Review Automation Performance

Weekly review checklist:
- [ ] Review execution logs
- [ ] Check paused campaigns
- [ ] Verify budget changes
- [ ] Adjust thresholds as needed
- [ ] Test new rules in dry-run mode

---

## Troubleshooting

### Rules Not Triggering

1. Check rule is enabled: `enabled: true`
2. Verify schedule is correct
3. Check if conditions are met
4. Review logs: `logs/rule_executions.json`

### Scheduled Events Not Running

1. Verify `next_run` is in the past
2. Check event is enabled
3. Ensure script is running via cron
4. Check logs for errors

### Actions Not Applied

1. Confirm not in dry-run mode
2. Check API credentials
3. Verify campaign/adset IDs
4. Review error logs

### Performance Issues

1. Limit number of campaigns evaluated
2. Use entity filters
3. Reduce rule execution frequency
4. Optimize condition logic

---

## Examples

### Example 1: Pause Weekend B2B Campaigns

```yaml
- name: "Pause B2B Campaigns on Weekend"
  enabled: true
  entity_type: "campaign"
  entity_filter:
    name_contains: "B2B"
  all_conditions: true
  conditions:
    - metric: "status"
      operator: "=="
      value: "ACTIVE"
  actions:
    - action_type: "pause_campaign"
  schedule: "0 0 * * 6"  # Every Saturday
```

### Example 2: Auto-scale Black Friday Campaign

```python
from datetime import datetime, timedelta
from src.automation.scheduler import CampaignScheduler, ScheduleType, ScheduleAction, ScheduledEvent

scheduler = CampaignScheduler(client)

# Increase budget on Black Friday
black_friday = datetime(2026, 11, 27, 0, 0)
event = ScheduledEvent(
    id="bf_2026",
    name="Black Friday Budget Increase",
    action=ScheduleAction.UPDATE_BUDGET,
    entity_id="campaign_123",
    schedule_type=ScheduleType.ONE_TIME,
    start_time=black_friday,
    parameters={'budget': 10000}
)
scheduler.add_event(event)
```

### Example 3: Multi-stage Campaign Launch

```python
from datetime import datetime, timedelta

# Stage 1: Start with low budget (Day 1)
scheduler.add_event(ScheduledEvent(
    id="launch_s1",
    name="Campaign Launch - Stage 1",
    action=ScheduleAction.START_CAMPAIGN,
    entity_id="new_campaign_123",
    schedule_type=ScheduleType.ONE_TIME,
    start_time=datetime(2026, 3, 1, 9, 0),
    parameters={'budget': 100}
))

# Stage 2: Increase if performing well (Day 3)
scheduler.add_event(ScheduledEvent(
    id="launch_s2",
    name="Campaign Launch - Stage 2",
    action=ScheduleAction.UPDATE_BUDGET,
    entity_id="new_campaign_123",
    schedule_type=ScheduleType.ONE_TIME,
    start_time=datetime(2026, 3, 3, 9, 0),
    parameters={'budget': 500}
))

# Stage 3: Full scale (Day 7)
scheduler.add_event(ScheduledEvent(
    id="launch_s3",
    name="Campaign Launch - Stage 3",
    action=ScheduleAction.UPDATE_BUDGET,
    entity_id="new_campaign_123",
    schedule_type=ScheduleType.ONE_TIME,
    start_time=datetime(2026, 3, 7, 9, 0),
    parameters={'budget': 2000}
))
```

---

## Advanced Topics

### Custom Action Handlers

Extend the rules engine with custom actions:

```python
from src.automation.rules_engine import RulesEngine, ActionType

def custom_action_handler(entity, entity_type, params, dry_run):
    # Your custom logic here
    return f"Custom action performed on {entity['name']}"

# Register custom handler
engine = RulesEngine(client)
engine.action_handlers[ActionType.CUSTOM] = custom_action_handler
```

### Integration with External Systems

Send alerts to Slack, email, or other systems:

```python
def send_slack_alert(entity, entity_type, params, dry_run):
    import requests
    webhook_url = "YOUR_SLACK_WEBHOOK"
    message = params.get('message')

    if not dry_run:
        requests.post(webhook_url, json={'text': message})

    return f"Sent Slack alert: {message}"

engine.action_handlers[ActionType.SEND_ALERT] = send_slack_alert
```

---

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review configuration files
- Test with `--dry-run` flag first
- See main README for general troubleshooting
