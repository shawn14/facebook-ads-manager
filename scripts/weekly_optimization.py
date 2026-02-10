#!/usr/bin/env python3
"""
Weekly Optimization Script

Run this script weekly to perform deeper optimization:
- Rebalance budgets across portfolio
- Scale winning campaigns
- Generate comprehensive reports
- Archive old data

Usage:
    python scripts/weekly_optimization.py [--dry-run] [--total-budget AMOUNT]

Cron example (run every Monday at 9 AM):
    0 9 * * 1 cd /path/to/facebook-ads-manager && python scripts/weekly_optimization.py --total-budget 10000 >> logs/weekly.log 2>&1
"""

import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api_client import FacebookAdsClient
from src.automation.workflows import WorkflowAutomation
from src.optimization.optimizer import BudgetOptimizer


def setup_logging():
    """Setup logging configuration."""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    logger.add(
        log_dir / "weekly_optimization.log",
        rotation="10 MB",
        retention="60 days",
        level="INFO"
    )


def main(dry_run: bool = False, total_budget: float = None):
    """Run weekly optimization tasks.

    Args:
        dry_run: Preview without making changes
        total_budget: Total budget to allocate across campaigns
    """
    setup_logging()

    logger.info("=" * 60)
    logger.info(f"Starting weekly optimization - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    logger.info("=" * 60)

    try:
        # Initialize client
        client = FacebookAdsClient()
        logger.info("✓ API client initialized")

        workflows = WorkflowAutomation(client)
        optimizer = BudgetOptimizer(client)

        # Task 1: Generate comprehensive health report
        logger.info("\n[1/4] Generating comprehensive health report...")
        health_report = workflows.campaign_health_report()

        logger.info(f"  Total campaigns analyzed: {len(health_report['campaigns'])}")
        logger.info(f"  Healthy: {health_report['summary']['healthy']}")
        logger.info(f"  Warning: {health_report['summary']['warning']}")
        logger.info(f"  Critical: {health_report['summary']['critical']}")

        # Export health report
        report_dir = Path('reports')
        report_dir.mkdir(exist_ok=True)
        report_file = report_dir / f"health_report_{datetime.now().strftime('%Y%m%d')}.json"

        import json
        with open(report_file, 'w') as f:
            json.dump(health_report, f, indent=2)
        logger.info(f"  ✓ Report saved to {report_file}")

        # Task 2: Scale winning campaigns
        logger.info("\n[2/4] Scaling winning campaigns...")
        scale_results = workflows.scale_winners(
            min_roas=2.0,
            scale_factor=1.5,
            dry_run=dry_run
        )

        if scale_results['scaled']:
            logger.info(f"  Scaled {len(scale_results['scaled'])} campaigns:")
            total_increase = 0
            for item in scale_results['scaled']:
                increase = item['new_budget'] - item['old_budget']
                total_increase += increase
                logger.info(
                    f"    • {item['campaign_name']}: "
                    f"${item['old_budget']:.2f} → ${item['new_budget']:.2f} "
                    f"(+${increase:.2f}, ROAS: {item['roas']}x)"
                )
            logger.info(f"  Total budget increase: ${total_increase:.2f}")
        else:
            logger.info("  No campaigns qualified for scaling")

        # Task 3: Rebalance portfolio (if total budget specified)
        if total_budget:
            logger.info(f"\n[3/4] Rebalancing portfolio with ${total_budget} total budget...")
            rebalance_results = workflows.smart_budget_rebalance(
                total_budget=total_budget,
                dry_run=dry_run
            )

            if rebalance_results['allocations']:
                logger.info(f"  Rebalanced {len(rebalance_results['allocations'])} campaigns:")
                for alloc in rebalance_results['allocations']:
                    if alloc['new_budget'] > 0:
                        change = alloc['new_budget'] - alloc['old_budget']
                        logger.info(
                            f"    • {alloc['campaign_name']}: "
                            f"${alloc['old_budget']:.2f} → ${alloc['new_budget']:.2f} "
                            f"({change:+.2f}, ROAS: {alloc['roas']:.2f}x)"
                        )
        else:
            logger.info("\n[3/4] Skipping portfolio rebalance (no total budget specified)")

        # Task 4: Optimize individual campaign budgets
        logger.info("\n[4/4] Optimizing campaign budgets...")
        opt_results = optimizer.optimize_budgets(dry_run=dry_run)

        if opt_results:
            logger.info(f"  Optimized {len(opt_results)} campaigns:")
            for change in opt_results:
                logger.info(
                    f"    • {change['campaign_name']}: "
                    f"${change['old_budget']:.2f} → ${change['new_budget']:.2f} "
                    f"({change['change_pct']:+.1f}%) - {change['reason']}"
                )
        else:
            logger.info("  No budget changes needed")

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("Weekly optimization complete!")

        # Calculate totals
        total_actions = (
            len(scale_results.get('scaled', [])) +
            len(opt_results)
        )

        logger.info(f"  Total actions: {total_actions}")
        logger.info(f"  Mode: {'DRY RUN - No changes made' if dry_run else 'LIVE - Changes applied'}")
        logger.info(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"Error running weekly optimization: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Weekly optimization for Facebook Ads Manager')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    parser.add_argument('--total-budget', type=float, help='Total budget to allocate across campaigns')
    args = parser.parse_args()

    sys.exit(main(dry_run=args.dry_run, total_budget=args.total_budget))
