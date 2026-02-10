"""Unit tests for BudgetOptimizer."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.optimization.optimizer import BudgetOptimizer


class TestBudgetOptimizerInit:
    """Tests for BudgetOptimizer initialization."""

    def test_init(self, mock_config):
        """Test BudgetOptimizer initialization."""
        mock_client = Mock()
        mock_client.config = mock_config

        optimizer = BudgetOptimizer(mock_client)

        assert optimizer.client == mock_client
        assert optimizer.config == mock_config


class TestOptimizeBudgets:
    """Tests for budget optimization."""

    @pytest.fixture
    def optimizer(self, mock_config):
        """Create an optimizer for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return BudgetOptimizer(mock_client)

    def test_optimize_budgets_high_performer(self, optimizer):
        """Test budget increase for high-performing campaigns."""
        campaign_data = {
            'id': '123',
            'name': 'High Performer',
            'status': 'ACTIVE',
            'daily_budget': 5000  # $50
        }

        insights_data = {
            'spend': '50.0',
            'actions': [
                {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '50'}
            ]
        }

        optimizer.client.get_campaigns = Mock(return_value=[campaign_data])
        optimizer.client.get_campaign_insights = Mock(return_value=[insights_data])

        changes = optimizer.optimize_budgets(min_roas=1.5, dry_run=True)

        # ROAS = (50 * 50) / 50 = 50, which is very high
        # Should recommend budget increase
        assert len(changes) > 0
        assert changes[0]['new_budget'] > changes[0]['old_budget']

    def test_optimize_budgets_low_performer(self, optimizer):
        """Test budget decrease for low-performing campaigns."""
        campaign_data = {
            'id': '123',
            'name': 'Low Performer',
            'status': 'ACTIVE',
            'daily_budget': 5000  # $50
        }

        insights_data = {
            'spend': '100.0',
            'actions': [
                {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '1'}
            ]
        }

        optimizer.client.get_campaigns = Mock(return_value=[campaign_data])
        optimizer.client.get_campaign_insights = Mock(return_value=[insights_data])

        changes = optimizer.optimize_budgets(min_roas=1.5, dry_run=True)

        # ROAS = (1 * 50) / 100 = 0.5, which is low
        # Should recommend budget decrease
        assert len(changes) > 0
        assert changes[0]['new_budget'] < changes[0]['old_budget']

    def test_optimize_budgets_no_changes(self, optimizer):
        """Test when no budget changes are needed."""
        campaign_data = {
            'id': '123',
            'name': 'Stable Campaign',
            'status': 'ACTIVE',
            'daily_budget': 5000
        }

        insights_data = {
            'spend': '50.0',
            'actions': [
                {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '2'}
            ]
        }

        optimizer.client.get_campaigns = Mock(return_value=[campaign_data])
        optimizer.client.get_campaign_insights = Mock(return_value=[insights_data])

        changes = optimizer.optimize_budgets(min_roas=1.5, dry_run=True)

        # ROAS = (2 * 50) / 50 = 2.0, meeting threshold
        # May or may not recommend changes depending on exact threshold
        # But should be minimal or no change
        if changes:
            change_pct = abs(changes[0]['change_pct'])
            assert change_pct <= 20  # Max 20% change

    def test_optimize_budgets_dry_run(self, optimizer):
        """Test that dry run doesn't apply changes."""
        campaign_data = {
            'id': '123',
            'name': 'Test Campaign',
            'status': 'ACTIVE',
            'daily_budget': 5000
        }

        insights_data = {
            'spend': '50.0',
            'actions': [
                {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '50'}
            ]
        }

        optimizer.client.get_campaigns = Mock(return_value=[campaign_data])
        optimizer.client.get_campaign_insights = Mock(return_value=[insights_data])
        optimizer._update_campaign_budget = Mock()

        changes = optimizer.optimize_budgets(min_roas=1.5, dry_run=True)

        # Should not update budgets in dry run
        optimizer._update_campaign_budget.assert_not_called()

    def test_optimize_budgets_apply_changes(self, optimizer):
        """Test that changes are applied when not dry run."""
        campaign_data = {
            'id': '123',
            'name': 'Test Campaign',
            'status': 'ACTIVE',
            'daily_budget': 5000
        }

        insights_data = {
            'spend': '50.0',
            'actions': [
                {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '50'}
            ]
        }

        optimizer.client.get_campaigns = Mock(return_value=[campaign_data])
        optimizer.client.get_campaign_insights = Mock(return_value=[insights_data])
        optimizer._update_campaign_budget = Mock()

        changes = optimizer.optimize_budgets(min_roas=1.5, dry_run=False)

        # Should update budgets when not dry run
        if changes:
            optimizer._update_campaign_budget.assert_called()


class TestCalculateOptimalBudget:
    """Tests for optimal budget calculation."""

    @pytest.fixture
    def optimizer(self, mock_config):
        """Create an optimizer for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return BudgetOptimizer(mock_client)

    def test_calculate_optimal_budget_high_roas(self, optimizer):
        """Test budget calculation for high ROAS."""
        current_budget = 50.0
        roas = 5.0  # High ROAS
        min_roas = 1.5

        new_budget = optimizer._calculate_optimal_budget(
            current_budget, roas, min_roas, 50.0
        )

        # Should increase budget (roas >= min_roas * 1.5)
        assert new_budget > current_budget
        assert new_budget == pytest.approx(60.0, abs=1.0)  # 20% increase

    def test_calculate_optimal_budget_low_roas(self, optimizer):
        """Test budget calculation for low ROAS."""
        current_budget = 50.0
        roas = 0.5  # Low ROAS
        min_roas = 1.5

        new_budget = optimizer._calculate_optimal_budget(
            current_budget, roas, min_roas, 50.0
        )

        # Should decrease budget significantly
        assert new_budget < current_budget

    def test_calculate_optimal_budget_respects_min_limit(self, optimizer):
        """Test that budget respects minimum limit."""
        current_budget = 15.0
        roas = 0.5
        min_roas = 1.5

        new_budget = optimizer._calculate_optimal_budget(
            current_budget, roas, min_roas, 15.0
        )

        # Should not go below min_daily_budget (10)
        assert new_budget >= 10.0

    def test_calculate_optimal_budget_respects_max_limit(self, optimizer):
        """Test that budget respects maximum limit."""
        current_budget = 4000.0
        roas = 10.0  # Very high ROAS
        min_roas = 1.5

        new_budget = optimizer._calculate_optimal_budget(
            current_budget, roas, min_roas, 4000.0
        )

        # Should not exceed max_daily_budget (5000)
        assert new_budget <= 5000.0

    def test_calculate_optimal_budget_rounding(self, optimizer):
        """Test that budget is rounded to nearest $5."""
        current_budget = 50.0
        roas = 3.0
        min_roas = 1.5

        new_budget = optimizer._calculate_optimal_budget(
            current_budget, roas, min_roas, 50.0
        )

        # Should be rounded to nearest 5
        assert new_budget % 5 == 0


class TestPauseUnderperformers:
    """Tests for pausing underperforming campaigns."""

    @pytest.fixture
    def optimizer(self, mock_config):
        """Create an optimizer for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return BudgetOptimizer(mock_client)

    def test_pause_underperformers_low_ctr(self, optimizer):
        """Test pausing campaigns with low CTR."""
        campaign_data = {
            'id': '123',
            'name': 'Low CTR Campaign',
            'status': 'ACTIVE'
        }

        insights_data = {
            'spend': '150.0',
            'impressions': '100000',
            'clicks': '100'  # 0.1% CTR
        }

        optimizer.client.get_campaigns = Mock(return_value=[campaign_data])
        optimizer.client.get_campaign_insights = Mock(return_value=[insights_data])

        paused = optimizer.pause_underperformers(min_ctr=0.5, min_spend=100, dry_run=True)

        # Should identify for pausing
        assert len(paused) > 0
        assert paused[0]['campaign_id'] == '123'

    def test_pause_underperformers_insufficient_spend(self, optimizer):
        """Test that campaigns with low spend are not paused."""
        campaign_data = {
            'id': '123',
            'name': 'New Campaign',
            'status': 'ACTIVE'
        }

        insights_data = {
            'spend': '10.0',  # Low spend
            'impressions': '1000',
            'clicks': '1'  # Very low CTR
        }

        optimizer.client.get_campaigns = Mock(return_value=[campaign_data])
        optimizer.client.get_campaign_insights = Mock(return_value=[insights_data])

        paused = optimizer.pause_underperformers(min_ctr=0.5, min_spend=100, dry_run=True)

        # Should not pause due to insufficient spend
        assert len(paused) == 0

    def test_pause_underperformers_good_performance(self, optimizer):
        """Test that well-performing campaigns are not paused."""
        campaign_data = {
            'id': '123',
            'name': 'Good Campaign',
            'status': 'ACTIVE'
        }

        insights_data = {
            'spend': '150.0',
            'impressions': '10000',
            'clicks': '500'  # 5% CTR
        }

        optimizer.client.get_campaigns = Mock(return_value=[campaign_data])
        optimizer.client.get_campaign_insights = Mock(return_value=[insights_data])

        paused = optimizer.pause_underperformers(min_ctr=0.5, min_spend=100, dry_run=True)

        # Should not pause
        assert len(paused) == 0

    def test_pause_underperformers_apply(self, optimizer):
        """Test that campaigns are actually paused when not dry run."""
        campaign_data = {
            'id': '123',
            'name': 'Bad Campaign',
            'status': 'ACTIVE'
        }

        insights_data = {
            'spend': '150.0',
            'impressions': '100000',
            'clicks': '100'
        }

        optimizer.client.get_campaigns = Mock(return_value=[campaign_data])
        optimizer.client.get_campaign_insights = Mock(return_value=[insights_data])
        optimizer.client.pause_campaign = Mock()

        paused = optimizer.pause_underperformers(min_ctr=0.5, min_spend=100, dry_run=False)

        # Should actually pause
        optimizer.client.pause_campaign.assert_called_once_with('123')


class TestRebalancePortfolio:
    """Tests for portfolio rebalancing."""

    @pytest.fixture
    def optimizer(self, mock_config):
        """Create an optimizer for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return BudgetOptimizer(mock_client)

    def test_rebalance_portfolio_proportional_allocation(self, optimizer):
        """Test that budget is allocated proportionally to ROAS."""
        campaigns = [
            {'id': '1', 'name': 'Campaign 1', 'status': 'ACTIVE', 'daily_budget': 3000},
            {'id': '2', 'name': 'Campaign 2', 'status': 'ACTIVE', 'daily_budget': 2000}
        ]

        insights = [
            {
                'spend': '30.0',
                'actions': [
                    {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '20'}
                ]
            },
            {
                'spend': '20.0',
                'actions': [
                    {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '5'}
                ]
            }
        ]

        optimizer.client.get_campaigns = Mock(return_value=campaigns)
        optimizer.client.get_campaign_insights = Mock(side_effect=insights)
        optimizer._update_campaign_budget = Mock()

        allocations = optimizer.rebalance_portfolio(total_budget=100.0, dry_run=True)

        # Campaign 1 has better ROAS, should get more budget
        # ROAS 1 = (20 * 50) / 30 = 33.33
        # ROAS 2 = (5 * 50) / 20 = 12.5
        assert len(allocations) == 2
        assert allocations[0]['new_budget'] > allocations[1]['new_budget']

    def test_rebalance_portfolio_zero_roas_excluded(self, optimizer):
        """Test that campaigns with zero ROAS get no budget."""
        campaigns = [
            {'id': '1', 'name': 'Good Campaign', 'status': 'ACTIVE', 'daily_budget': 5000},
            {'id': '2', 'name': 'Bad Campaign', 'status': 'ACTIVE', 'daily_budget': 5000}
        ]

        insights = [
            {
                'spend': '50.0',
                'actions': [
                    {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '10'}
                ]
            },
            {
                'spend': '50.0',
                'actions': []  # No conversions
            }
        ]

        optimizer.client.get_campaigns = Mock(return_value=campaigns)
        optimizer.client.get_campaign_insights = Mock(side_effect=insights)

        allocations = optimizer.rebalance_portfolio(total_budget=100.0, dry_run=True)

        # Campaign 2 should get 0 budget
        bad_campaign = next(a for a in allocations if a['campaign_id'] == '2')
        assert bad_campaign['new_budget'] == 0


class TestExtractConversions:
    """Tests for conversion extraction."""

    @pytest.fixture
    def optimizer(self, mock_config):
        """Create an optimizer for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return BudgetOptimizer(mock_client)

    def test_extract_conversions_purchase(self, optimizer):
        """Test extracting purchase conversions."""
        insight = {
            'actions': [
                {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '10'}
            ]
        }

        conversions = optimizer._extract_conversions(insight)

        assert conversions == 10

    def test_extract_conversions_generic(self, optimizer):
        """Test extracting generic conversions."""
        insight = {
            'actions': [
                {'action_type': 'conversion', 'value': '5'}
            ]
        }

        conversions = optimizer._extract_conversions(insight)

        assert conversions == 5

    def test_extract_conversions_no_actions(self, optimizer):
        """Test extraction with no actions."""
        insight = {}

        conversions = optimizer._extract_conversions(insight)

        assert conversions == 0

    def test_extract_conversions_no_conversion_actions(self, optimizer):
        """Test extraction with no conversion-type actions."""
        insight = {
            'actions': [
                {'action_type': 'link_click', 'value': '100'},
                {'action_type': 'page_view', 'value': '50'}
            ]
        }

        conversions = optimizer._extract_conversions(insight)

        assert conversions == 0


class TestGetChangeReason:
    """Tests for change reason generation."""

    @pytest.fixture
    def optimizer(self, mock_config):
        """Create an optimizer for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return BudgetOptimizer(mock_client)

    def test_get_change_reason_high_roas_increase(self, optimizer):
        """Test reason for high ROAS increase."""
        reason = optimizer._get_change_reason(roas=5.0, min_roas=1.5, change_pct=20.0)

        assert "High ROAS" in reason
        assert "scaling up" in reason

    def test_get_change_reason_good_roas_increase(self, optimizer):
        """Test reason for good ROAS increase."""
        reason = optimizer._get_change_reason(roas=2.0, min_roas=1.5, change_pct=10.0)

        assert "Good ROAS" in reason

    def test_get_change_reason_low_roas_decrease(self, optimizer):
        """Test reason for low ROAS decrease."""
        reason = optimizer._get_change_reason(roas=0.5, min_roas=1.5, change_pct=-30.0)

        assert "Low ROAS" in reason
        assert "reducing budget" in reason


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.fixture
    def optimizer(self, mock_config):
        """Create an optimizer for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return BudgetOptimizer(mock_client)

    def test_optimize_budgets_no_active_campaigns(self, optimizer):
        """Test optimization with no active campaigns."""
        optimizer.client.get_campaigns = Mock(return_value=[])

        changes = optimizer.optimize_budgets(dry_run=True)

        assert changes == []

    def test_optimize_budgets_no_insights(self, optimizer):
        """Test optimization when insights are unavailable."""
        campaign_data = {
            'id': '123',
            'name': 'Campaign',
            'status': 'ACTIVE',
            'daily_budget': 5000
        }

        optimizer.client.get_campaigns = Mock(return_value=[campaign_data])
        optimizer.client.get_campaign_insights = Mock(return_value=[])

        changes = optimizer.optimize_budgets(dry_run=True)

        # Should skip campaigns without insights
        assert changes == []
