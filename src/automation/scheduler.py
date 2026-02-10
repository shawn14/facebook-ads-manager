"""Campaign scheduling and calendar management."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
from pathlib import Path
import json


class ScheduleType(Enum):
    """Types of campaign schedules."""
    ONE_TIME = "one_time"
    RECURRING_DAILY = "daily"
    RECURRING_WEEKLY = "weekly"
    RECURRING_MONTHLY = "monthly"
    CUSTOM_CRON = "cron"


class ScheduleAction(Enum):
    """Actions that can be scheduled."""
    START_CAMPAIGN = "start_campaign"
    PAUSE_CAMPAIGN = "pause_campaign"
    UPDATE_BUDGET = "update_budget"
    DUPLICATE_CAMPAIGN = "duplicate_campaign"
    RUN_RULES = "run_rules"


@dataclass
class ScheduledEvent:
    """Represents a scheduled event."""
    id: str
    name: str
    action: ScheduleAction
    entity_id: Optional[str]  # Campaign/adset ID
    schedule_type: ScheduleType
    start_time: datetime
    end_time: Optional[datetime] = None
    recurrence_pattern: Optional[Dict] = None
    parameters: Dict[str, Any] = None
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        self._calculate_next_run()

    def _calculate_next_run(self):
        """Calculate the next run time for this event."""
        now = datetime.now()

        if not self.enabled:
            self.next_run = None
            return

        # One-time event
        if self.schedule_type == ScheduleType.ONE_TIME:
            if self.start_time > now:
                self.next_run = self.start_time
            else:
                self.next_run = None
            return

        # Check if past end time
        if self.end_time and now > self.end_time:
            self.next_run = None
            return

        # For recurring events, calculate based on last run or start time
        base_time = self.last_run if self.last_run else self.start_time

        if self.schedule_type == ScheduleType.RECURRING_DAILY:
            next_time = base_time + timedelta(days=1)
            while next_time <= now:
                next_time += timedelta(days=1)
            self.next_run = next_time

        elif self.schedule_type == ScheduleType.RECURRING_WEEKLY:
            next_time = base_time + timedelta(weeks=1)
            while next_time <= now:
                next_time += timedelta(weeks=1)
            self.next_run = next_time

        elif self.schedule_type == ScheduleType.RECURRING_MONTHLY:
            # Add one month
            year = base_time.year
            month = base_time.month + 1
            if month > 12:
                month = 1
                year += 1
            day = min(base_time.day, self._days_in_month(year, month))
            next_time = base_time.replace(year=year, month=month, day=day)
            while next_time <= now:
                month += 1
                if month > 12:
                    month = 1
                    year += 1
                day = min(base_time.day, self._days_in_month(year, month))
                next_time = next_time.replace(year=year, month=month, day=day)
            self.next_run = next_time

        elif self.schedule_type == ScheduleType.CUSTOM_CRON:
            # For cron, we'll use croniter library if available
            try:
                from croniter import croniter
                cron_expr = self.recurrence_pattern.get('expression', '0 0 * * *')
                iter_obj = croniter(cron_expr, now)
                self.next_run = iter_obj.get_next(datetime)
            except ImportError:
                logger.warning("croniter not installed, cannot parse cron expression")
                self.next_run = None
            except Exception as e:
                logger.error(f"Error parsing cron expression: {e}")
                self.next_run = None

    def _days_in_month(self, year: int, month: int) -> int:
        """Get number of days in a month."""
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        else:
            # February
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                return 29
            return 28

    def should_run(self) -> bool:
        """Check if this event should run now.

        Returns:
            True if event should execute
        """
        if not self.enabled:
            return False

        if not self.next_run:
            return False

        return datetime.now() >= self.next_run

    def mark_executed(self):
        """Mark event as executed and calculate next run."""
        self.last_run = datetime.now()
        self._calculate_next_run()

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'action': self.action.value,
            'entity_id': self.entity_id,
            'schedule_type': self.schedule_type.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'recurrence_pattern': self.recurrence_pattern,
            'parameters': self.parameters,
            'enabled': self.enabled,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ScheduledEvent':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            action=ScheduleAction(data['action']),
            entity_id=data.get('entity_id'),
            schedule_type=ScheduleType(data['schedule_type']),
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            recurrence_pattern=data.get('recurrence_pattern'),
            parameters=data.get('parameters', {}),
            enabled=data.get('enabled', True),
            last_run=datetime.fromisoformat(data['last_run']) if data.get('last_run') else None,
            next_run=datetime.fromisoformat(data['next_run']) if data.get('next_run') else None
        )


class CampaignScheduler:
    """Manages scheduled campaign events and calendar."""

    def __init__(self, api_client, schedule_file: str = "config/schedule.json"):
        """Initialize scheduler.

        Args:
            api_client: FacebookAdsClient instance
            schedule_file: Path to schedule storage file
        """
        self.client = api_client
        self.schedule_file = schedule_file
        self.events: List[ScheduledEvent] = []
        self._load_schedule()

    def _load_schedule(self):
        """Load schedule from file."""
        path = Path(self.schedule_file)
        if not path.exists():
            logger.info(f"Schedule file not found at {self.schedule_file}, starting with empty schedule")
            return

        try:
            with open(path) as f:
                data = json.load(f)
                self.events = [ScheduledEvent.from_dict(event) for event in data.get('events', [])]
                logger.info(f"Loaded {len(self.events)} scheduled events")
        except Exception as e:
            logger.error(f"Error loading schedule: {e}")

    def save_schedule(self):
        """Save schedule to file."""
        path = Path(self.schedule_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(path, 'w') as f:
                json.dump(
                    {'events': [event.to_dict() for event in self.events]},
                    f,
                    indent=2
                )
            logger.info(f"Saved {len(self.events)} scheduled events")
        except Exception as e:
            logger.error(f"Error saving schedule: {e}")

    def add_event(self, event: ScheduledEvent):
        """Add a scheduled event.

        Args:
            event: Event to add
        """
        self.events.append(event)
        logger.info(f"Added scheduled event: {event.name} (next run: {event.next_run})")
        self.save_schedule()

    def remove_event(self, event_id: str) -> bool:
        """Remove a scheduled event.

        Args:
            event_id: ID of event to remove

        Returns:
            True if event was found and removed
        """
        initial_count = len(self.events)
        self.events = [e for e in self.events if e.id != event_id]
        removed = len(self.events) < initial_count

        if removed:
            logger.info(f"Removed scheduled event: {event_id}")
            self.save_schedule()

        return removed

    def get_event(self, event_id: str) -> Optional[ScheduledEvent]:
        """Get event by ID.

        Args:
            event_id: Event ID

        Returns:
            Event if found
        """
        return next((e for e in self.events if e.id == event_id), None)

    def list_events(
        self,
        include_disabled: bool = False,
        action_filter: Optional[ScheduleAction] = None
    ) -> List[ScheduledEvent]:
        """List scheduled events.

        Args:
            include_disabled: Include disabled events
            action_filter: Filter by action type

        Returns:
            List of events
        """
        events = self.events

        if not include_disabled:
            events = [e for e in events if e.enabled]

        if action_filter:
            events = [e for e in events if e.action == action_filter]

        return sorted(events, key=lambda e: e.next_run if e.next_run else datetime.max)

    def get_upcoming_events(self, hours: int = 24) -> List[ScheduledEvent]:
        """Get events scheduled in the next N hours.

        Args:
            hours: Number of hours to look ahead

        Returns:
            List of upcoming events
        """
        now = datetime.now()
        cutoff = now + timedelta(hours=hours)

        upcoming = []
        for event in self.events:
            if event.enabled and event.next_run and now <= event.next_run <= cutoff:
                upcoming.append(event)

        return sorted(upcoming, key=lambda e: e.next_run)

    def run_pending_events(self, dry_run: bool = False) -> List[Dict]:
        """Execute all pending scheduled events.

        Args:
            dry_run: Preview without executing

        Returns:
            List of execution results
        """
        results = []

        for event in self.events:
            if event.should_run():
                logger.info(f"Executing scheduled event: {event.name}")

                try:
                    result = self._execute_event(event, dry_run)
                    results.append({
                        'event_id': event.id,
                        'event_name': event.name,
                        'action': event.action.value,
                        'success': True,
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    })

                    if not dry_run:
                        event.mark_executed()

                except Exception as e:
                    logger.error(f"Error executing event {event.name}: {e}")
                    results.append({
                        'event_id': event.id,
                        'event_name': event.name,
                        'action': event.action.value,
                        'success': False,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })

        if results and not dry_run:
            self.save_schedule()

        return results

    def _execute_event(self, event: ScheduledEvent, dry_run: bool) -> str:
        """Execute a single scheduled event.

        Args:
            event: Event to execute
            dry_run: Preview mode

        Returns:
            Result description
        """
        if event.action == ScheduleAction.START_CAMPAIGN:
            if not dry_run:
                self.client.activate_campaign(event.entity_id)
            return f"Started campaign {event.entity_id}"

        elif event.action == ScheduleAction.PAUSE_CAMPAIGN:
            if not dry_run:
                self.client.pause_campaign(event.entity_id)
            return f"Paused campaign {event.entity_id}"

        elif event.action == ScheduleAction.UPDATE_BUDGET:
            new_budget = event.parameters.get('budget')
            if not new_budget:
                raise ValueError("No budget specified in parameters")

            if not dry_run:
                from src.campaign.manager import CampaignManager
                manager = CampaignManager(self.client)
                manager.update_budget(event.entity_id, new_budget)

            return f"Updated budget for campaign {event.entity_id} to ${new_budget}"

        elif event.action == ScheduleAction.DUPLICATE_CAMPAIGN:
            new_name = event.parameters.get('new_name')

            if not dry_run:
                from src.campaign.manager import CampaignManager
                manager = CampaignManager(self.client)
                new_campaign = manager.duplicate_campaign(event.entity_id, new_name)
                return f"Duplicated campaign {event.entity_id} as {new_campaign['id']}"
            else:
                return f"Would duplicate campaign {event.entity_id}"

        elif event.action == ScheduleAction.RUN_RULES:
            if not dry_run:
                from src.automation.rules_engine import RulesEngine
                engine = RulesEngine(self.client)
                logs = engine.execute_rules(dry_run=False)
                return f"Executed rules, {len(logs)} actions performed"
            else:
                return "Would execute automation rules"

        else:
            raise ValueError(f"Unknown action: {event.action}")

    def schedule_campaign_start(
        self,
        campaign_id: str,
        start_time: datetime,
        name: Optional[str] = None
    ) -> ScheduledEvent:
        """Schedule a campaign to start at a specific time.

        Args:
            campaign_id: Campaign ID
            start_time: When to start
            name: Event name

        Returns:
            Created event
        """
        import uuid

        event = ScheduledEvent(
            id=str(uuid.uuid4()),
            name=name or f"Start campaign {campaign_id}",
            action=ScheduleAction.START_CAMPAIGN,
            entity_id=campaign_id,
            schedule_type=ScheduleType.ONE_TIME,
            start_time=start_time
        )

        self.add_event(event)
        return event

    def schedule_campaign_pause(
        self,
        campaign_id: str,
        pause_time: datetime,
        name: Optional[str] = None
    ) -> ScheduledEvent:
        """Schedule a campaign to pause at a specific time.

        Args:
            campaign_id: Campaign ID
            pause_time: When to pause
            name: Event name

        Returns:
            Created event
        """
        import uuid

        event = ScheduledEvent(
            id=str(uuid.uuid4()),
            name=name or f"Pause campaign {campaign_id}",
            action=ScheduleAction.PAUSE_CAMPAIGN,
            entity_id=campaign_id,
            schedule_type=ScheduleType.ONE_TIME,
            start_time=pause_time
        )

        self.add_event(event)
        return event

    def schedule_recurring_rules(
        self,
        schedule_type: ScheduleType,
        start_time: datetime,
        name: str = "Recurring automation rules"
    ) -> ScheduledEvent:
        """Schedule recurring rule execution.

        Args:
            schedule_type: How often to run (daily, weekly, etc.)
            start_time: When to start
            name: Event name

        Returns:
            Created event
        """
        import uuid

        event = ScheduledEvent(
            id=str(uuid.uuid4()),
            name=name,
            action=ScheduleAction.RUN_RULES,
            entity_id=None,
            schedule_type=schedule_type,
            start_time=start_time
        )

        self.add_event(event)
        return event

    def get_calendar_view(self, days: int = 30) -> Dict[str, List[Dict]]:
        """Get calendar view of scheduled events.

        Args:
            days: Number of days to include

        Returns:
            Dictionary with dates as keys and events as values
        """
        calendar = {}
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        for day in range(days):
            date = now + timedelta(days=day)
            date_key = date.strftime('%Y-%m-%d')
            calendar[date_key] = []

            for event in self.events:
                if not event.enabled or not event.next_run:
                    continue

                event_date = event.next_run.replace(hour=0, minute=0, second=0, microsecond=0)

                if event_date == date:
                    calendar[date_key].append({
                        'id': event.id,
                        'name': event.name,
                        'action': event.action.value,
                        'time': event.next_run.strftime('%H:%M'),
                        'entity_id': event.entity_id
                    })

        return calendar
