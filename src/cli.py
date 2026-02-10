"""Command-line interface for Facebook Ads Manager."""

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api_client import FacebookAdsClient
from src.campaign.manager import CampaignManager
from src.analytics.reporter import AnalyticsReporter
from src.optimization.optimizer import BudgetOptimizer
from src.optimization.ab_testing import ABTestManager
from src.automation.rules_engine import RulesEngine, Rule, Condition, Action, ConditionOperator, ActionType
from src.automation.scheduler import CampaignScheduler, ScheduledEvent, ScheduleType, ScheduleAction
from src.automation.workflows import WorkflowAutomation

console = Console()


@click.group()
@click.pass_context
def cli(ctx):
    """Facebook Ads Manager - Comprehensive campaign management tool."""
    try:
        ctx.obj = {
            'client': FacebookAdsClient(),
            'campaign_manager': None,  # Lazy init
            'analytics': None,
            'optimizer': None,
            'ab_test': None
        }
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


# Campaign Commands

@cli.group()
def campaign():
    """Manage ad campaigns."""
    pass


@campaign.command()
@click.option('--name', required=True, help='Campaign name')
@click.option('--objective', default='LINK_CLICKS', help='Campaign objective')
@click.option('--budget', type=int, required=True, help='Daily budget in USD')
@click.option('--status', default='PAUSED', help='Initial status (ACTIVE/PAUSED)')
@click.pass_context
def create(ctx, name, objective, budget, status):
    """Create a new campaign."""
    client = ctx.obj['client']
    manager = CampaignManager(client)

    try:
        campaign = manager.create_campaign(
            name=name,
            objective=objective,
            daily_budget=budget,
            status=status
        )
        console.print(f"[green]✓[/green] Campaign created: {campaign['name']} (ID: {campaign['id']})")
    except Exception as e:
        console.print(f"[red]Error creating campaign:[/red] {e}")
        sys.exit(1)


@campaign.command()
@click.option('--status', help='Filter by status')
@click.option('--format', default='table', help='Output format (table/json)')
@click.pass_context
def list(ctx, status, format):
    """List all campaigns."""
    client = ctx.obj['client']
    manager = CampaignManager(client)

    try:
        campaigns = manager.list_campaigns(status_filter=status)

        if format == 'json':
            rprint(campaigns)
        else:
            table = Table(title="Campaigns")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Objective")
            table.add_column("Status")
            table.add_column("Budget")

            for camp in campaigns:
                table.add_row(
                    camp['id'],
                    camp['name'],
                    camp.get('objective', 'N/A'),
                    camp.get('status', 'N/A'),
                    f"${camp.get('daily_budget', 0) / 100:.2f}"
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing campaigns:[/red] {e}")
        sys.exit(1)


@campaign.command()
@click.option('--id', 'campaign_id', required=True, help='Campaign ID')
@click.pass_context
def pause(ctx, campaign_id):
    """Pause a campaign."""
    client = ctx.obj['client']
    manager = CampaignManager(client)

    try:
        manager.pause_campaign(campaign_id)
        console.print(f"[green]✓[/green] Campaign {campaign_id} paused")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@campaign.command()
@click.option('--id', 'campaign_id', required=True, help='Campaign ID')
@click.pass_context
def activate(ctx, campaign_id):
    """Activate a campaign."""
    client = ctx.obj['client']
    manager = CampaignManager(client)

    try:
        manager.activate_campaign(campaign_id)
        console.print(f"[green]✓[/green] Campaign {campaign_id} activated")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


# Analytics Commands

@cli.group()
def analytics():
    """Analytics and reporting."""
    pass


@analytics.command()
@click.option('--campaign-id', help='Campaign ID (optional, defaults to account-level)')
@click.option('--days', default=7, help='Number of days to analyze')
@click.option('--format', default='table', help='Output format (table/json/csv)')
@click.pass_context
def report(ctx, campaign_id, days, format):
    """Generate performance report."""
    client = ctx.obj['client']
    reporter = AnalyticsReporter(client)

    try:
        if campaign_id:
            data = reporter.campaign_report(campaign_id, days=days)
        else:
            data = reporter.account_report(days=days)

        if format == 'table':
            reporter.display_report(data)
        elif format == 'json':
            rprint(data)
        elif format == 'csv':
            filename = reporter.export_csv(data)
            console.print(f"[green]✓[/green] Report exported to {filename}")

    except Exception as e:
        console.print(f"[red]Error generating report:[/red] {e}")
        sys.exit(1)


@analytics.command()
@click.pass_context
def dashboard(ctx):
    """Show live performance dashboard."""
    client = ctx.obj['client']
    reporter = AnalyticsReporter(client)

    try:
        reporter.show_dashboard()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


# Optimization Commands

@cli.group()
def optimize():
    """Budget and performance optimization."""
    pass


@optimize.command()
@click.option('--min-roas', type=float, help='Minimum ROAS threshold')
@click.option('--dry-run', is_flag=True, help='Preview changes without applying')
@click.pass_context
def budgets(ctx, min_roas, dry_run):
    """Optimize budget allocation across campaigns."""
    client = ctx.obj['client']
    optimizer = BudgetOptimizer(client)

    try:
        changes = optimizer.optimize_budgets(min_roas=min_roas, dry_run=dry_run)

        table = Table(title="Budget Optimization" + (" (DRY RUN)" if dry_run else ""))
        table.add_column("Campaign")
        table.add_column("Current Budget")
        table.add_column("New Budget")
        table.add_column("Change")
        table.add_column("Reason")

        for change in changes:
            table.add_row(
                change['campaign_name'],
                f"${change['old_budget']:.2f}",
                f"${change['new_budget']:.2f}",
                f"{change['change_pct']:+.1f}%",
                change['reason']
            )

        console.print(table)

        if dry_run:
            console.print("\n[yellow]ℹ[/yellow] This was a dry run. Use --no-dry-run to apply changes.")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@optimize.command('pause-underperformers')
@click.option('--threshold', type=float, default=0.5, help='Min CTR threshold (%)')
@click.option('--min-spend', type=float, default=100, help='Min spend to evaluate ($)')
@click.option('--dry-run', is_flag=True, help='Preview without pausing')
@click.pass_context
def pause_underperformers(ctx, threshold, min_spend, dry_run):
    """Automatically pause underperforming campaigns."""
    client = ctx.obj['client']
    optimizer = BudgetOptimizer(client)

    try:
        paused = optimizer.pause_underperformers(
            min_ctr=threshold,
            min_spend=min_spend,
            dry_run=dry_run
        )

        if paused:
            table = Table(title="Underperforming Campaigns" + (" (DRY RUN)" if dry_run else " - PAUSED"))
            table.add_column("Campaign")
            table.add_column("CTR")
            table.add_column("Spend")
            table.add_column("Reason")

            for item in paused:
                table.add_row(
                    item['campaign_name'],
                    f"{item['ctr']:.2f}%",
                    f"${item['spend']:.2f}",
                    item['reason']
                )

            console.print(table)
        else:
            console.print("[green]✓[/green] No underperforming campaigns found")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


# A/B Testing Commands

@cli.group()
def test():
    """A/B testing and experiments."""
    pass


@test.command()
@click.option('--campaign-id', required=True, help='Base campaign ID')
@click.option('--variants', type=int, default=2, help='Number of variants to test')
@click.option('--name', required=True, help='Test name')
@click.pass_context
def create(ctx, campaign_id, variants, name):
    """Create a new A/B test."""
    client = ctx.obj['client']
    ab_test = ABTestManager(client)

    try:
        test = ab_test.create_test(
            base_campaign_id=campaign_id,
            num_variants=variants,
            test_name=name
        )
        console.print(f"[green]✓[/green] A/B test created: {test['name']} (ID: {test['id']})")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@test.command()
@click.option('--test-id', required=True, help='Test ID')
@click.pass_context
def analyze(ctx, test_id):
    """Analyze A/B test results."""
    client = ctx.obj['client']
    ab_test = ABTestManager(client)

    try:
        results = ab_test.analyze_test(test_id)
        ab_test.display_results(results)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


# Automation Commands

@cli.group()
def automate():
    """Automation and rules management."""
    pass


@automate.command('run-rules')
@click.option('--dry-run', is_flag=True, help='Preview without executing')
@click.pass_context
def run_rules(ctx, dry_run):
    """Execute automation rules."""
    client = ctx.obj['client']
    engine = RulesEngine(client)

    try:
        logs = engine.execute_rules(dry_run=dry_run)

        if logs:
            table = Table(title="Rule Execution Results" + (" (DRY RUN)" if dry_run else ""))
            table.add_column("Rule")
            table.add_column("Entity")
            table.add_column("Actions")

            for log in logs:
                table.add_row(
                    log['rule_name'],
                    log['entity_name'],
                    "\n".join(log['actions_performed'])
                )

            console.print(table)
            console.print(f"\n[green]✓[/green] Executed {len(logs)} rules")
        else:
            console.print("[yellow]ℹ[/yellow] No rules triggered")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@automate.command('list-rules')
@click.pass_context
def list_rules(ctx):
    """List all automation rules."""
    client = ctx.obj['client']
    engine = RulesEngine(client)

    try:
        if not engine.rules:
            console.print("[yellow]ℹ[/yellow] No rules configured")
            return

        table = Table(title="Automation Rules")
        table.add_column("Name", style="cyan")
        table.add_column("Entity Type")
        table.add_column("Conditions")
        table.add_column("Actions")
        table.add_column("Enabled")
        table.add_column("Last Run")

        for rule in engine.rules:
            table.add_row(
                rule.name,
                rule.entity_type,
                str(len(rule.conditions)),
                str(len(rule.actions)),
                "✓" if rule.enabled else "✗",
                rule.last_run.strftime("%Y-%m-%d %H:%M") if rule.last_run else "Never"
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@automate.command('schedule-list')
@click.option('--upcoming', type=int, help='Show events in next N hours')
@click.pass_context
def schedule_list(ctx, upcoming):
    """List scheduled events."""
    client = ctx.obj['client']
    scheduler = CampaignScheduler(client)

    try:
        if upcoming:
            events = scheduler.get_upcoming_events(hours=upcoming)
            title = f"Events in Next {upcoming} Hours"
        else:
            events = scheduler.list_events()
            title = "Scheduled Events"

        if not events:
            console.print("[yellow]ℹ[/yellow] No scheduled events")
            return

        table = Table(title=title)
        table.add_column("Name", style="cyan")
        table.add_column("Action")
        table.add_column("Next Run")
        table.add_column("Schedule Type")
        table.add_column("Enabled")

        for event in events:
            table.add_row(
                event.name,
                event.action.value,
                event.next_run.strftime("%Y-%m-%d %H:%M") if event.next_run else "N/A",
                event.schedule_type.value,
                "✓" if event.enabled else "✗"
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@automate.command('run-scheduled')
@click.option('--dry-run', is_flag=True, help='Preview without executing')
@click.pass_context
def run_scheduled(ctx, dry_run):
    """Execute pending scheduled events."""
    client = ctx.obj['client']
    scheduler = CampaignScheduler(client)

    try:
        results = scheduler.run_pending_events(dry_run=dry_run)

        if results:
            table = Table(title="Scheduled Events Executed" + (" (DRY RUN)" if dry_run else ""))
            table.add_column("Event")
            table.add_column("Action")
            table.add_column("Status")
            table.add_column("Result")

            for result in results:
                status = "✓" if result['success'] else "✗"
                message = result.get('result', result.get('error', ''))

                table.add_row(
                    result['event_name'],
                    result['action'],
                    status,
                    message
                )

            console.print(table)
        else:
            console.print("[yellow]ℹ[/yellow] No pending events to execute")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@automate.command('calendar')
@click.option('--days', default=30, help='Number of days to show')
@click.pass_context
def calendar_view(ctx, days):
    """View calendar of scheduled events."""
    client = ctx.obj['client']
    scheduler = CampaignScheduler(client)

    try:
        calendar = scheduler.get_calendar_view(days=days)

        has_events = any(len(events) > 0 for events in calendar.values())

        if not has_events:
            console.print(f"[yellow]ℹ[/yellow] No events scheduled in next {days} days")
            return

        for date, events in sorted(calendar.items()):
            if events:
                console.print(f"\n[bold cyan]{date}[/bold cyan]")
                for event in events:
                    console.print(f"  {event['time']} - {event['name']} ({event['action']})")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


# Workflow Commands

@cli.group()
def workflow():
    """Pre-built workflow automation."""
    pass


@workflow.command('daily-check')
@click.option('--dry-run', is_flag=True, help='Preview without executing')
@click.pass_context
def daily_check(ctx, dry_run):
    """Run daily performance check workflow."""
    client = ctx.obj['client']
    workflows = WorkflowAutomation(client)

    try:
        console.print("[bold]Running daily performance check...[/bold]")
        results = workflows.daily_performance_check(dry_run=dry_run)

        # Display paused campaigns
        if results['paused']:
            table = Table(title="Campaigns Paused")
            table.add_column("Campaign")
            table.add_column("CTR")
            table.add_column("Reason")

            for item in results['paused']:
                table.add_row(
                    item['campaign_name'],
                    f"{item['ctr']:.2f}%",
                    item['reason']
                )

            console.print(table)

        # Display budget increases
        if results['budget_increased']:
            table = Table(title="Budget Increased")
            table.add_column("Campaign")
            table.add_column("Old Budget")
            table.add_column("New Budget")
            table.add_column("ROAS")

            for item in results['budget_increased']:
                table.add_row(
                    item['campaign_name'],
                    f"${item['old_budget']:.2f}",
                    f"${item['new_budget']:.2f}",
                    f"{item['roas']:.2f}x"
                )

            console.print(table)

        # Display budget decreases
        if results['budget_decreased']:
            table = Table(title="Budget Decreased")
            table.add_column("Campaign")
            table.add_column("Old Budget")
            table.add_column("New Budget")
            table.add_column("ROAS")

            for item in results['budget_decreased']:
                table.add_row(
                    item['campaign_name'],
                    f"${item['old_budget']:.2f}",
                    f"${item['new_budget']:.2f}",
                    f"{item['roas']:.2f}x"
                )

            console.print(table)

        # Display alerts
        if results['alerts']:
            console.print("\n[yellow]Alerts:[/yellow]")
            for alert in results['alerts']:
                console.print(f"  [yellow]⚠[/yellow] {alert['message']}")

        console.print(f"\n[green]✓[/green] Daily check complete")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@workflow.command('health-report')
@click.option('--format', default='table', help='Output format (table/json)')
@click.pass_context
def health_report(ctx, format):
    """Generate campaign health report."""
    client = ctx.obj['client']
    workflows = WorkflowAutomation(client)

    try:
        report = workflows.campaign_health_report()

        if format == 'json':
            rprint(report)
        else:
            # Display summary
            console.print(f"\n[bold]Campaign Health Summary[/bold]")
            console.print(f"Healthy: [green]{report['summary']['healthy']}[/green]")
            console.print(f"Warning: [yellow]{report['summary']['warning']}[/yellow]")
            console.print(f"Critical: [red]{report['summary']['critical']}[/red]\n")

            # Display campaign details
            if report['campaigns']:
                table = Table(title="Campaign Health Details")
                table.add_column("Campaign", style="cyan")
                table.add_column("Score")
                table.add_column("Status")
                table.add_column("CTR")
                table.add_column("ROAS")
                table.add_column("Spend")

                for campaign in report['campaigns']:
                    status_color = {
                        'healthy': 'green',
                        'warning': 'yellow',
                        'critical': 'red'
                    }.get(campaign['status'], 'white')

                    table.add_row(
                        campaign['campaign_name'],
                        str(campaign['health_score']),
                        f"[{status_color}]{campaign['status']}[/{status_color}]",
                        f"{campaign['metrics']['ctr']}%",
                        f"{campaign['metrics']['roas']}x",
                        f"${campaign['metrics']['spend']:.2f}"
                    )

                console.print(table)

                # Show recommendations for critical campaigns
                critical = [c for c in report['campaigns'] if c['status'] == 'critical']
                if critical:
                    console.print("\n[bold red]Critical Campaign Recommendations:[/bold red]")
                    for campaign in critical[:3]:  # Show top 3
                        console.print(f"\n[red]• {campaign['campaign_name']}[/red]")
                        for rec in campaign['recommendations']:
                            console.print(f"  - {rec}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@workflow.command('scale-winners')
@click.option('--min-roas', type=float, default=2.0, help='Minimum ROAS threshold')
@click.option('--scale-factor', type=float, default=1.5, help='Budget multiplier')
@click.option('--dry-run', is_flag=True, help='Preview without executing')
@click.pass_context
def scale_winners(ctx, min_roas, scale_factor, dry_run):
    """Scale up budget for winning campaigns."""
    client = ctx.obj['client']
    workflows = WorkflowAutomation(client)

    try:
        results = workflows.scale_winners(
            min_roas=min_roas,
            scale_factor=scale_factor,
            dry_run=dry_run
        )

        if results['scaled']:
            table = Table(title="Campaigns Scaled" + (" (DRY RUN)" if dry_run else ""))
            table.add_column("Campaign")
            table.add_column("ROAS")
            table.add_column("Old Budget")
            table.add_column("New Budget")
            table.add_column("Increase")

            for item in results['scaled']:
                table.add_row(
                    item['campaign_name'],
                    f"{item['roas']}x",
                    f"${item['old_budget']:.2f}",
                    f"${item['new_budget']:.2f}",
                    f"+{item['increase']:.1f}%"
                )

            console.print(table)
            console.print(f"\n[green]✓[/green] Scaled {len(results['scaled'])} campaigns")
        else:
            console.print("[yellow]ℹ[/yellow] No campaigns qualify for scaling")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@workflow.command('emergency-pause')
@click.option('--reason', default='Emergency pause', help='Reason for pause')
@click.option('--dry-run', is_flag=True, help='Preview without executing')
@click.confirmation_option(prompt='Are you sure you want to pause ALL campaigns?')
@click.pass_context
def emergency_pause(ctx, reason, dry_run):
    """Emergency pause all active campaigns."""
    client = ctx.obj['client']
    workflows = WorkflowAutomation(client)

    try:
        results = workflows.emergency_pause_all(reason=reason, dry_run=dry_run)

        console.print(f"\n[bold red]Emergency Pause Executed[/bold red]")
        console.print(f"Reason: {results['reason']}")
        console.print(f"Campaigns paused: {len(results['paused'])}")

        if results['paused']:
            console.print("\n[red]Paused campaigns:[/red]")
            for item in results['paused']:
                console.print(f"  • {item['campaign_name']}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


# Utility Commands

@cli.command()
@click.pass_context
def validate(ctx):
    """Validate API credentials."""
    client = ctx.obj['client']

    if client.validate_credentials():
        info = client.get_account_info()
        console.print("[green]✓[/green] Credentials validated successfully")
        console.print(f"\nAccount: {info['name']}")
        console.print(f"ID: {info['id']}")
        console.print(f"Currency: {info['currency']}")
        console.print(f"Status: {info['account_status']}")
    else:
        console.print("[red]✗[/red] Credential validation failed")
        sys.exit(1)


if __name__ == '__main__':
    cli()
