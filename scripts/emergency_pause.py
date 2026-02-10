#!/usr/bin/env python3
"""
Emergency Pause Script

Immediately pause all active campaigns.
Use this in emergency situations (e.g., billing issues, wrong targeting, etc.)

Usage:
    python scripts/emergency_pause.py --reason "Billing issue" [--dry-run]

CAUTION: This will pause ALL active campaigns!
"""

import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api_client import FacebookAdsClient
from src.automation.workflows import WorkflowAutomation


def main(reason: str, dry_run: bool = False):
    """Emergency pause all campaigns.

    Args:
        reason: Reason for emergency pause
        dry_run: Preview without making changes
    """
    logger.info("=" * 60)
    logger.info("EMERGENCY PAUSE INITIATED")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Reason: {reason}")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    logger.info("=" * 60)

    try:
        # Initialize client
        client = FacebookAdsClient()
        workflows = WorkflowAutomation(client)

        # Execute emergency pause
        results = workflows.emergency_pause_all(reason=reason, dry_run=dry_run)

        logger.info(f"\nPaused {len(results['paused'])} campaigns:")
        for item in results['paused']:
            logger.info(f"  • {item['campaign_name']} (ID: {item['campaign_id']})")

        logger.info("\n" + "=" * 60)
        if dry_run:
            logger.info("DRY RUN COMPLETE - No changes made")
        else:
            logger.info("EMERGENCY PAUSE COMPLETE - All campaigns paused")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"Error during emergency pause: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Emergency pause all campaigns')
    parser.add_argument('--reason', required=True, help='Reason for emergency pause')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    args = parser.parse_args()

    # Confirmation for live mode
    if not args.dry_run:
        print("\n⚠️  WARNING: This will pause ALL active campaigns!")
        print(f"Reason: {args.reason}")
        response = input("\nType 'CONFIRM' to proceed: ")

        if response != 'CONFIRM':
            print("Emergency pause cancelled")
            sys.exit(0)

    sys.exit(main(reason=args.reason, dry_run=args.dry_run))
