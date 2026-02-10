"""Automated rules engine for campaign management."""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from loguru import logger
import json
from pathlib import Path


class ConditionOperator(Enum):
    """Operators for rule conditions."""
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    EQUAL = "=="
    NOT_EQUAL = "!="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"


class ActionType(Enum):
    """Types of actions that can be performed."""
    PAUSE_CAMPAIGN = "pause_campaign"
    ACTIVATE_CAMPAIGN = "activate_campaign"
    UPDATE_BUDGET = "update_budget"
    INCREASE_BUDGET = "increase_budget"
    DECREASE_BUDGET = "decrease_budget"
    SEND_ALERT = "send_alert"
    PAUSE_ADSET = "pause_adset"
    ACTIVATE_ADSET = "activate_adset"


@dataclass
class Condition:
    """Represents a single condition in a rule."""
    metric: str
    operator: ConditionOperator
    value: Any

    def evaluate(self, data: Dict[str, Any]) -> bool:
        """Evaluate condition against data.

        Args:
            data: Dictionary containing metric values

        Returns:
            True if condition is met
        """
        if self.metric not in data:
            logger.warning(f"Metric '{self.metric}' not found in data")
            return False

        actual_value = data[self.metric]

        try:
            if self.operator == ConditionOperator.GREATER_THAN:
                return float(actual_value) > float(self.value)
            elif self.operator == ConditionOperator.LESS_THAN:
                return float(actual_value) < float(self.value)
            elif self.operator == ConditionOperator.GREATER_EQUAL:
                return float(actual_value) >= float(self.value)
            elif self.operator == ConditionOperator.LESS_EQUAL:
                return float(actual_value) <= float(self.value)
            elif self.operator == ConditionOperator.EQUAL:
                return actual_value == self.value
            elif self.operator == ConditionOperator.NOT_EQUAL:
                return actual_value != self.value
            elif self.operator == ConditionOperator.CONTAINS:
                return str(self.value) in str(actual_value)
            elif self.operator == ConditionOperator.NOT_CONTAINS:
                return str(self.value) not in str(actual_value)
            else:
                logger.error(f"Unknown operator: {self.operator}")
                return False
        except (ValueError, TypeError) as e:
            logger.error(f"Error evaluating condition: {e}")
            return False

    def to_dict(self) -> Dict:
        """Convert condition to dictionary."""
        return {
            'metric': self.metric,
            'operator': self.operator.value,
            'value': self.value
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Condition':
        """Create condition from dictionary."""
        return cls(
            metric=data['metric'],
            operator=ConditionOperator(data['operator']),
            value=data['value']
        )


@dataclass
class Action:
    """Represents an action to perform when rule conditions are met."""
    action_type: ActionType
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert action to dictionary."""
        return {
            'action_type': self.action_type.value,
            'parameters': self.parameters
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Action':
        """Create action from dictionary."""
        return cls(
            action_type=ActionType(data['action_type']),
            parameters=data.get('parameters', {})
        )


@dataclass
class Rule:
    """Represents an automated rule with conditions and actions."""
    name: str
    conditions: List[Condition]
    actions: List[Action]
    enabled: bool = True
    entity_type: str = "campaign"  # campaign, adset, ad
    entity_filter: Optional[Dict] = None
    all_conditions: bool = True  # True = AND, False = OR
    schedule: Optional[str] = None  # Cron expression
    last_run: Optional[datetime] = None
    run_count: int = 0

    def evaluate(self, data: Dict[str, Any]) -> bool:
        """Evaluate all conditions against data.

        Args:
            data: Dictionary containing metric values

        Returns:
            True if rule conditions are met
        """
        if not self.enabled:
            return False

        if not self.conditions:
            return False

        results = [condition.evaluate(data) for condition in self.conditions]

        if self.all_conditions:
            # AND - all conditions must be true
            return all(results)
        else:
            # OR - at least one condition must be true
            return any(results)

    def to_dict(self) -> Dict:
        """Convert rule to dictionary."""
        return {
            'name': self.name,
            'conditions': [c.to_dict() for c in self.conditions],
            'actions': [a.to_dict() for a in self.actions],
            'enabled': self.enabled,
            'entity_type': self.entity_type,
            'entity_filter': self.entity_filter,
            'all_conditions': self.all_conditions,
            'schedule': self.schedule,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'run_count': self.run_count
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Rule':
        """Create rule from dictionary."""
        return cls(
            name=data['name'],
            conditions=[Condition.from_dict(c) for c in data['conditions']],
            actions=[Action.from_dict(a) for a in data['actions']],
            enabled=data.get('enabled', True),
            entity_type=data.get('entity_type', 'campaign'),
            entity_filter=data.get('entity_filter'),
            all_conditions=data.get('all_conditions', True),
            schedule=data.get('schedule'),
            last_run=datetime.fromisoformat(data['last_run']) if data.get('last_run') else None,
            run_count=data.get('run_count', 0)
        )


class RuleExecutionLog:
    """Log entry for rule execution."""

    def __init__(
        self,
        rule_name: str,
        entity_id: str,
        entity_name: str,
        triggered: bool,
        actions_performed: List[str],
        timestamp: datetime,
        dry_run: bool = False
    ):
        self.rule_name = rule_name
        self.entity_id = entity_id
        self.entity_name = entity_name
        self.triggered = triggered
        self.actions_performed = actions_performed
        self.timestamp = timestamp
        self.dry_run = dry_run

    def to_dict(self) -> Dict:
        """Convert log entry to dictionary."""
        return {
            'rule_name': self.rule_name,
            'entity_id': self.entity_id,
            'entity_name': self.entity_name,
            'triggered': self.triggered,
            'actions_performed': self.actions_performed,
            'timestamp': self.timestamp.isoformat(),
            'dry_run': self.dry_run
        }


class RulesEngine:
    """Automated rules engine for campaign management."""

    def __init__(self, api_client, config_path: str = "config/rules.yaml"):
        """Initialize rules engine.

        Args:
            api_client: FacebookAdsClient instance
            config_path: Path to rules configuration file
        """
        self.client = api_client
        self.config_path = config_path
        self.rules: List[Rule] = []
        self.execution_log: List[RuleExecutionLog] = []
        self.action_handlers: Dict[ActionType, Callable] = self._register_action_handlers()

        # Load rules from config
        self._load_rules()

    def _register_action_handlers(self) -> Dict[ActionType, Callable]:
        """Register handlers for each action type."""
        return {
            ActionType.PAUSE_CAMPAIGN: self._action_pause_campaign,
            ActionType.ACTIVATE_CAMPAIGN: self._action_activate_campaign,
            ActionType.UPDATE_BUDGET: self._action_update_budget,
            ActionType.INCREASE_BUDGET: self._action_increase_budget,
            ActionType.DECREASE_BUDGET: self._action_decrease_budget,
            ActionType.SEND_ALERT: self._action_send_alert,
            ActionType.PAUSE_ADSET: self._action_pause_adset,
            ActionType.ACTIVATE_ADSET: self._action_activate_adset,
        }

    def _load_rules(self):
        """Load rules from configuration file."""
        path = Path(self.config_path)
        if not path.exists():
            logger.info(f"Rules config not found at {self.config_path}, starting with empty rules")
            return

        try:
            with open(path) as f:
                import yaml
                config = yaml.safe_load(f)

            if config and 'rules' in config:
                self.rules = [Rule.from_dict(rule_data) for rule_data in config['rules']]
                logger.info(f"Loaded {len(self.rules)} rules from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading rules: {e}")

    def save_rules(self):
        """Save rules to configuration file."""
        path = Path(self.config_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            import yaml
            config = {
                'rules': [rule.to_dict() for rule in self.rules]
            }

            with open(path, 'w') as f:
                yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Saved {len(self.rules)} rules to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving rules: {e}")

    def add_rule(self, rule: Rule):
        """Add a new rule.

        Args:
            rule: Rule to add
        """
        self.rules.append(rule)
        logger.info(f"Added rule: {rule.name}")

    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name.

        Args:
            rule_name: Name of rule to remove

        Returns:
            True if rule was found and removed
        """
        initial_count = len(self.rules)
        self.rules = [r for r in self.rules if r.name != rule_name]
        removed = len(self.rules) < initial_count

        if removed:
            logger.info(f"Removed rule: {rule_name}")

        return removed

    def get_rule(self, rule_name: str) -> Optional[Rule]:
        """Get a rule by name.

        Args:
            rule_name: Rule name

        Returns:
            Rule if found, None otherwise
        """
        return next((r for r in self.rules if r.name == rule_name), None)

    def execute_rules(self, dry_run: bool = True) -> List[RuleExecutionLog]:
        """Execute all enabled rules.

        Args:
            dry_run: If True, preview actions without executing

        Returns:
            List of execution logs
        """
        execution_logs = []

        logger.info(f"Executing {len(self.rules)} rules (dry_run={dry_run})")

        for rule in self.rules:
            if not rule.enabled:
                continue

            # Get entities based on rule type
            entities = self._get_entities_for_rule(rule)

            for entity in entities:
                # Get metrics for entity
                metrics = self._get_entity_metrics(entity, rule.entity_type)

                # Evaluate rule conditions
                if rule.evaluate(metrics):
                    logger.info(f"Rule '{rule.name}' triggered for {rule.entity_type} {entity['name']}")

                    # Execute actions
                    actions_performed = []
                    for action in rule.actions:
                        action_result = self._execute_action(
                            action,
                            entity,
                            rule.entity_type,
                            dry_run
                        )
                        actions_performed.append(action_result)

                    # Log execution
                    log_entry = RuleExecutionLog(
                        rule_name=rule.name,
                        entity_id=entity['id'],
                        entity_name=entity['name'],
                        triggered=True,
                        actions_performed=actions_performed,
                        timestamp=datetime.now(),
                        dry_run=dry_run
                    )
                    execution_logs.append(log_entry)

                    # Update rule stats
                    if not dry_run:
                        rule.last_run = datetime.now()
                        rule.run_count += 1

        # Save execution logs
        self.execution_log.extend(execution_logs)

        if not dry_run:
            self.save_rules()

        return execution_logs

    def _get_entities_for_rule(self, rule: Rule) -> List[Dict]:
        """Get entities to evaluate for a rule.

        Args:
            rule: Rule to get entities for

        Returns:
            List of entities
        """
        if rule.entity_type == "campaign":
            entities = self.client.get_campaigns()
        elif rule.entity_type == "adset":
            entities = self.client.get_adsets()
        else:
            logger.warning(f"Unsupported entity type: {rule.entity_type}")
            return []

        # Apply entity filter if specified
        if rule.entity_filter:
            entities = self._filter_entities(entities, rule.entity_filter)

        return list(entities)

    def _filter_entities(self, entities: List[Dict], entity_filter: Dict) -> List[Dict]:
        """Filter entities based on filter criteria.

        Args:
            entities: List of entities
            entity_filter: Filter criteria

        Returns:
            Filtered entities
        """
        filtered = []
        for entity in entities:
            match = True
            for key, value in entity_filter.items():
                if key not in entity or entity[key] != value:
                    match = False
                    break
            if match:
                filtered.append(entity)
        return filtered

    def _get_entity_metrics(self, entity: Dict, entity_type: str) -> Dict[str, Any]:
        """Get performance metrics for an entity.

        Args:
            entity: Entity object
            entity_type: Type of entity

        Returns:
            Dictionary of metrics
        """
        metrics = {
            'id': entity['id'],
            'name': entity['name'],
            'status': entity.get('status', 'UNKNOWN')
        }

        # Get insights
        try:
            if entity_type == "campaign":
                insights = self.client.get_campaign_insights(entity['id'], date_preset='last_7d')
            elif entity_type == "adset":
                insights = self.client.get_campaign_insights(entity['id'], date_preset='last_7d')
            else:
                insights = []

            if insights and len(insights) > 0:
                insight = insights[0]

                # Add common metrics
                metrics['spend'] = float(insight.get('spend', 0))
                metrics['impressions'] = int(insight.get('impressions', 0))
                metrics['clicks'] = int(insight.get('clicks', 0))
                metrics['ctr'] = float(insight.get('ctr', 0))
                metrics['cpc'] = float(insight.get('cpc', 0))
                metrics['reach'] = int(insight.get('reach', 0))
                metrics['frequency'] = float(insight.get('frequency', 0))

                # Calculate additional metrics
                if 'actions' in insight:
                    conversions = self._extract_conversions(insight)
                    metrics['conversions'] = conversions

                    if metrics['spend'] > 0 and conversions > 0:
                        metrics['cost_per_conversion'] = metrics['spend'] / conversions

                        # Calculate ROAS if we have revenue data
                        avg_order_value = self.client.config.get('analytics', {}).get('avg_order_value', 50)
                        revenue = conversions * avg_order_value
                        metrics['roas'] = revenue / metrics['spend']

        except Exception as e:
            logger.error(f"Error getting metrics for {entity_type} {entity['id']}: {e}")

        return metrics

    def _extract_conversions(self, insight: Dict) -> int:
        """Extract conversion count from insights."""
        if 'actions' not in insight:
            return 0

        for action in insight['actions']:
            action_type = action.get('action_type', '').lower()
            if 'purchase' in action_type or 'conversion' in action_type:
                return int(action.get('value', 0))

        return 0

    def _execute_action(
        self,
        action: Action,
        entity: Dict,
        entity_type: str,
        dry_run: bool
    ) -> str:
        """Execute a single action.

        Args:
            action: Action to execute
            entity: Entity to perform action on
            entity_type: Type of entity
            dry_run: Preview mode

        Returns:
            Description of action performed
        """
        handler = self.action_handlers.get(action.action_type)

        if not handler:
            logger.error(f"No handler for action type: {action.action_type}")
            return f"ERROR: Unknown action type {action.action_type.value}"

        try:
            return handler(entity, entity_type, action.parameters, dry_run)
        except Exception as e:
            logger.error(f"Error executing action {action.action_type.value}: {e}")
            return f"ERROR: {str(e)}"

    # Action Handlers

    def _action_pause_campaign(
        self,
        entity: Dict,
        entity_type: str,
        params: Dict,
        dry_run: bool
    ) -> str:
        """Pause a campaign."""
        if not dry_run:
            self.client.pause_campaign(entity['id'])
        return f"Paused {entity_type} '{entity['name']}'"

    def _action_activate_campaign(
        self,
        entity: Dict,
        entity_type: str,
        params: Dict,
        dry_run: bool
    ) -> str:
        """Activate a campaign."""
        if not dry_run:
            self.client.activate_campaign(entity['id'])
        return f"Activated {entity_type} '{entity['name']}'"

    def _action_update_budget(
        self,
        entity: Dict,
        entity_type: str,
        params: Dict,
        dry_run: bool
    ) -> str:
        """Update budget to specific value."""
        new_budget = params.get('budget')
        if not new_budget:
            return "ERROR: No budget specified"

        if not dry_run:
            from src.campaign.manager import CampaignManager
            manager = CampaignManager(self.client)
            manager.update_budget(entity['id'], new_budget)

        return f"Updated budget for '{entity['name']}' to ${new_budget}"

    def _action_increase_budget(
        self,
        entity: Dict,
        entity_type: str,
        params: Dict,
        dry_run: bool
    ) -> str:
        """Increase budget by percentage."""
        percent = params.get('percent', 10)
        current_budget = int(entity.get('daily_budget', 0)) / 100
        new_budget = current_budget * (1 + percent / 100)

        if not dry_run:
            from src.campaign.manager import CampaignManager
            manager = CampaignManager(self.client)
            manager.update_budget(entity['id'], new_budget)

        return f"Increased budget for '{entity['name']}' by {percent}% (${current_budget} → ${new_budget:.2f})"

    def _action_decrease_budget(
        self,
        entity: Dict,
        entity_type: str,
        params: Dict,
        dry_run: bool
    ) -> str:
        """Decrease budget by percentage."""
        percent = params.get('percent', 10)
        current_budget = int(entity.get('daily_budget', 0)) / 100
        new_budget = current_budget * (1 - percent / 100)

        if not dry_run:
            from src.campaign.manager import CampaignManager
            manager = CampaignManager(self.client)
            manager.update_budget(entity['id'], new_budget)

        return f"Decreased budget for '{entity['name']}' by {percent}% (${current_budget} → ${new_budget:.2f})"

    def _action_send_alert(
        self,
        entity: Dict,
        entity_type: str,
        params: Dict,
        dry_run: bool
    ) -> str:
        """Send alert notification."""
        message = params.get('message', f'Alert for {entity_type} {entity["name"]}')

        if not dry_run:
            # TODO: Implement actual alert sending (email, Slack, etc.)
            logger.warning(f"ALERT: {message}")

        return f"Sent alert: {message}"

    def _action_pause_adset(
        self,
        entity: Dict,
        entity_type: str,
        params: Dict,
        dry_run: bool
    ) -> str:
        """Pause an ad set."""
        if not dry_run:
            from facebook_business.adobjects.adset import AdSet
            adset = AdSet(entity['id'])
            adset.api_update(params={'status': 'PAUSED'})

        return f"Paused ad set '{entity['name']}'"

    def _action_activate_adset(
        self,
        entity: Dict,
        entity_type: str,
        params: Dict,
        dry_run: bool
    ) -> str:
        """Activate an ad set."""
        if not dry_run:
            from facebook_business.adobjects.adset import AdSet
            adset = AdSet(entity['id'])
            adset.api_update(params={'status': 'ACTIVE'})

        return f"Activated ad set '{entity['name']}'"

    def get_execution_logs(
        self,
        limit: Optional[int] = None,
        rule_name: Optional[str] = None
    ) -> List[Dict]:
        """Get execution logs.

        Args:
            limit: Maximum number of logs to return
            rule_name: Filter by rule name

        Returns:
            List of log entries
        """
        logs = self.execution_log

        if rule_name:
            logs = [log for log in logs if log.rule_name == rule_name]

        # Sort by timestamp descending
        logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)

        if limit:
            logs = logs[:limit]

        return [log.to_dict() for log in logs]

    def save_execution_logs(self, filepath: str = "logs/rule_executions.json"):
        """Save execution logs to file.

        Args:
            filepath: Path to save logs
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(path, 'w') as f:
                json.dump(
                    [log.to_dict() for log in self.execution_log],
                    f,
                    indent=2
                )
            logger.info(f"Saved {len(self.execution_log)} execution logs to {filepath}")
        except Exception as e:
            logger.error(f"Error saving execution logs: {e}")
