"""Automation module for Facebook Ads Manager."""

from .rules_engine import RulesEngine, Rule, Condition, Action
from .scheduler import CampaignScheduler
from .workflows import WorkflowAutomation

__all__ = [
    'RulesEngine',
    'Rule',
    'Condition',
    'Action',
    'CampaignScheduler',
    'WorkflowAutomation'
]
