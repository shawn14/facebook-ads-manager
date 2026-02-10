#!/usr/bin/env python3
"""
Daily Automation Script

Run this script daily (via cron or task scheduler) to:
- Execute automation rules
- Run performance checks
- Generate health reports
- Execute scheduled events

Usage:
    python scripts/daily_automation.py [--dry-run]

Cron example (run daily at 9 AM):
    0 9 * * * cd /path/to/facebook-ads-manager && python scripts/daily_automation.py >> logs/automation.log 2>&1
"""

import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api_client import FacebookAdsClient
from src.automation.rules_engine import RulesEngine
from src.automation.scheduler import CampaignScheduler
from src.automation.workflows import WorkflowAutomation


def setup_logging():
    """Setup logging configuration."""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    logger.add(
        log_dir / "daily_automation.log",
        rotation="10 MB",
        retention="30 days",
        level="INFO"
    )


def main(dry_run: bool = False):
    """Run daily automation tasks.

    Args:
        dry_run: Preview without making changes
    """
    setup_logging()

    logger.info("=" * 60)
    logger.info(f"Starting daily automation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    logger.info("=" * 60)

    try:
        # Initialize client
        client = FacebookAdsClient()
        logger.info("✓ API client initialized")

        # Task 1: Execute scheduled events
        logger.info("\n[1/4] Running scheduled events...")
        scheduler = CampaignScheduler(client)
        scheduled_results = scheduler.run_pending_events(dry_run=dry_run)

        if scheduled_results:
            logger.info(f"  Executed {len(scheduled_results)} scheduled events")
            for result in scheduled_results:
                if result['success']:
                    logger.info(f"  ✓ {result['event_name']}: {result['result']}")
                else:
                    logger.error(f"  ✗ {result['event_name']}: {result.get('error', 'Unknown error')}")
        else:
            logger.info("  No scheduled events pending")

        # Task 2: Execute automation rules
        logger.info("\n[2/4] Executing automation rules...")
        engine = RulesEngine(client)
        rule_logs = engine.execute_rules(dry_run=dry_run)

        if rule_logs:
            logger.info(f"  Triggered {len(rule_logs)} rules")
            for log in rule_logs:
                logger.info(f"  ✓ {log['rule_name']} → {log['entity_name']}")
                for action in log['actions_performed']:
                    logger.info(f"    - {action}")

            # Save execution logs
            if not dry_run:
                engine.save_execution_logs()
        else:
            logger.info("  No rules triggered")

        # Task 3: Run daily performance check
        logger.info("\n[3/4] Running daily performance check...")
        workflows = WorkflowAutomation(client)
        perf_results = workflows.daily_performance_check(dry_run=dry_run)

        logger.info(f"  Paused: {len(perf_results['paused'])} campaigns")
        logger.info(f"  Budget increased: {len(perf_results['budget_increased'])} campaigns")
        logger.info(f"  Budget decreased: {len(perf_results['budget_decreased'])} campaigns")
        logger.info(f"  Alerts: {len(perf_results['alerts'])} issues")

        if perf_results['alerts']:
            logger.warning("  Alerts detected:")
            for alert in perf_results['alerts']:
                logger.warning(f"    ⚠ {alert['message']}")

        # Task 4: Generate health report
        logger.info("\n[4/4] Generating health report...")
        health_report = workflows.campaign_health_report()

        logger.info(f"  Healthy: {health_report['summary']['healthy']} campaigns")
        logger.info(f"  Warning: {health_report['summary']['warning']} campaigns")
        logger.info(f"  Critical: {health_report['summary']['critical']} campaigns")

        # Log critical campaigns
        critical = [c for c in health_report['campaigns'] if c['status'] == 'critical']
        if critical:
            logger.warning("  Critical campaigns requiring attention:")
            for campaign in critical:
                logger.warning(f"    • {campaign['campaign_name']} (score: {campaign['health_score']})")
                for rec in campaign['recommendations']:
                    logger.warning(f"      - {rec}")

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("Daily automation complete!")
        logger.info(f"  Mode: {'DRY RUN - No changes made' if dry_run else 'LIVE - Changes applied'}")
        logger.info(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"Error running daily automation: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Daily automation for Facebook Ads Manager')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    args = parser.parse_args()

    sys.exit(main(dry_run=args.dry_run))
