"""Integration tests for complete workflows."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.api_client import FacebookAdsClient
from src.campaign.manager import CampaignManager
from src.analytics.reporter import AnalyticsReporter
from src.optimization.optimizer import BudgetOptimizer
from src.optimization.ab_testing import ABTestManager


class TestCampaignCreationWorkflow:
    """Integration tests for campaign creation workflow."""

    @pytest.fixture
    def client(self, mock_config_file, mock_facebook_ads_api, mock_account_object):
        """Create a client for integration testing."""
        with patch('src.api_client.AdAccount', return_value=mock_account_object):
            return FacebookAdsClient(config_path=mock_config_file)

    def test_create_campaign_and_fetch_insights(self, client, mock_campaign_data, mock_insights_data):
        """Test creating a campaign and fetching insights."""
        # Mock campaign creation
        client.ad_account.create_campaign = Mock(return_value=mock_campaign_data)

        # Create campaign
        campaign = client.create_campaign(
            name="Integration Test Campaign",
            objective="LINK_CLICKS"
        )

        assert campaign['id'] == '123456789'

        # Mock insights
        mock_campaign_obj = Mock()
        mock_campaign_obj.get_insights = Mock(return_value=[mock_insights_data])

        with patch('src.api_client.Campaign', return_value=mock_campaign_obj):
            insights = client.get_campaign_insights(campaign['id'])

            assert len(insights) > 0
            assert insights[0]['campaign_id'] == '123456789'

    def test_create_campaign_with_manager(self, client, sample_targeting):
        """Test creating campaign through campaign manager."""
        manager = CampaignManager(client)

        client.create_campaign = Mock(return_value={
            'id': '123456789',
            'name': 'Test Campaign',
            'objective': 'CONVERSIONS'
        })

        client.create_adset = Mock(return_value={
            'id': '987654321',
            'name': 'Ad Set 1'
        })

        with patch.object(manager, '_get_default_targeting', return_value=sample_targeting):
            campaign = manager.create_campaign(
                name="Managed Campaign",
                objective="CONVERSIONS",
                daily_budget=100.0,
                status="ACTIVE"
            )

            assert campaign is not None
            # Should have created both campaign and ad set
            client.create_campaign.assert_called_once()
            client.create_adset.assert_called_once()


class TestAnalyticsWorkflow:
    """Integration tests for analytics workflow."""

    @pytest.fixture
    def setup(self, mock_config_file, mock_facebook_ads_api, mock_account_object):
        """Setup client and reporter."""
        with patch('src.api_client.AdAccount', return_value=mock_account_object):
            client = FacebookAdsClient(config_path=mock_config_file)
            reporter = AnalyticsReporter(client)
            return client, reporter

    def test_generate_and_export_report(self, setup, mock_insights_data, tmp_path):
        """Test generating report and exporting to CSV."""
        client, reporter = setup

        # Mock insights
        client.get_account_insights = Mock(return_value=[mock_insights_data])

        # Generate report
        report = reporter.account_report(days=7)

        assert len(report) > 0

        # Export to CSV
        with patch('src.analytics.reporter.Path', return_value=tmp_path):
            with patch('pandas.DataFrame.to_csv') as mock_to_csv:
                filepath = reporter.export_csv(report)

                assert filepath.endswith('.csv')
                mock_to_csv.assert_called_once()

    def test_anomaly_detection_workflow(self, setup):
        """Test complete anomaly detection workflow."""
        client, reporter = setup

        # Mock insights with anomalies
        insights_data = {
            'impressions': '100000',
            'clicks': '100',  # Low CTR
            'spend': '1000.0',  # High spend
            'actions': [
                {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '5'}
            ]
        }

        client.get_campaign_insights = Mock(return_value=[insights_data])
        client.get_campaigns = Mock(return_value=[])

        # Detect anomalies
        anomalies = reporter.detect_anomalies('123456789')

        # Should detect multiple anomalies
        assert len(anomalies) > 0
        anomaly_types = [a['type'] for a in anomalies]
        assert 'low_ctr' in anomaly_types or 'high_cpa' in anomaly_types


class TestOptimizationWorkflow:
    """Integration tests for optimization workflow."""

    @pytest.fixture
    def setup(self, mock_config_file, mock_facebook_ads_api, mock_account_object):
        """Setup client and optimizer."""
        with patch('src.api_client.AdAccount', return_value=mock_account_object):
            client = FacebookAdsClient(config_path=mock_config_file)
            optimizer = BudgetOptimizer(client)
            return client, optimizer

    def test_optimize_and_apply_changes(self, setup):
        """Test optimizing budgets and applying changes."""
        client, optimizer = setup

        # Mock campaigns
        campaigns = [
            {
                'id': '1',
                'name': 'High Performer',
                'status': 'ACTIVE',
                'daily_budget': 5000
            },
            {
                'id': '2',
                'name': 'Low Performer',
                'status': 'ACTIVE',
                'daily_budget': 5000
            }
        ]

        # Mock insights
        insights = [
            {
                'spend': '50.0',
                'actions': [
                    {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '50'}
                ]
            },
            {
                'spend': '50.0',
                'actions': [
                    {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '1'}
                ]
            }
        ]

        client.get_campaigns = Mock(return_value=campaigns)
        client.get_campaign_insights = Mock(side_effect=insights)
        optimizer._update_campaign_budget = Mock()

        # Dry run first
        changes_dry = optimizer.optimize_budgets(dry_run=True)

        assert len(changes_dry) > 0
        optimizer._update_campaign_budget.assert_not_called()

        # Apply changes
        changes_applied = optimizer.optimize_budgets(dry_run=False)

        assert len(changes_applied) > 0
        # Should have applied changes
        if changes_applied:
            optimizer._update_campaign_budget.assert_called()

    def test_pause_underperformers_workflow(self, setup):
        """Test complete underperformer pausing workflow."""
        client, optimizer = setup

        campaigns = [
            {
                'id': '1',
                'name': 'Bad Campaign',
                'status': 'ACTIVE'
            }
        ]

        insights = [
            {
                'spend': '200.0',
                'impressions': '100000',
                'clicks': '100'  # 0.1% CTR - very low
            }
        ]

        client.get_campaigns = Mock(return_value=campaigns)
        client.get_campaign_insights = Mock(side_effect=insights)
        client.pause_campaign = Mock()

        # Identify underperformers
        paused = optimizer.pause_underperformers(
            min_ctr=0.5,
            min_spend=100,
            dry_run=False
        )

        assert len(paused) > 0
        client.pause_campaign.assert_called_once_with('1')


class TestABTestingWorkflow:
    """Integration tests for A/B testing workflow."""

    @pytest.fixture
    def setup(self, mock_config_file, mock_facebook_ads_api, mock_account_object):
        """Setup client and AB test manager."""
        with patch('src.api_client.AdAccount', return_value=mock_account_object):
            client = FacebookAdsClient(config_path=mock_config_file)
            ab_test = ABTestManager(client)
            return client, ab_test

    def test_complete_ab_test_workflow(self, setup, mock_campaign_data):
        """Test complete A/B testing workflow."""
        client, ab_test = setup

        # Step 1: Create test
        client.get_campaigns = Mock(return_value=[mock_campaign_data])
        client.create_campaign = Mock(return_value={
            'id': '999',
            'name': 'Test Variant'
        })

        test = ab_test.create_test(
            base_campaign_id='123456789',
            num_variants=2,
            test_name='Landing Page Test'
        )

        assert test is not None
        assert len(test['variants']) == 2

        # Step 2: Run campaigns (mocked)
        # Step 3: Analyze results
        campaigns = [
            {'id': '1', 'name': 'Landing Page Test - Variant 1'},
            {'id': '2', 'name': 'Landing Page Test - Variant 2'}
        ]

        insights = [
            {
                'impressions': '10000',
                'clicks': '600',
                'actions': [
                    {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '60'}
                ]
            },
            {
                'impressions': '10000',
                'clicks': '400',
                'actions': [
                    {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '30'}
                ]
            }
        ]

        client.get_campaigns = Mock(return_value=campaigns)
        client.get_campaign_insights = Mock(side_effect=insights)

        results = ab_test.analyze_test('Landing Page Test')

        assert results is not None
        assert len(results['variants']) == 2
        # Variant 1 should be better
        assert results['variants'][0]['conversions'] > results['variants'][1]['conversions']


class TestEndToEndScenarios:
    """End-to-end integration tests."""

    @pytest.fixture
    def full_setup(self, mock_config_file, mock_facebook_ads_api, mock_account_object):
        """Setup all components."""
        with patch('src.api_client.AdAccount', return_value=mock_account_object):
            client = FacebookAdsClient(config_path=mock_config_file)
            campaign_manager = CampaignManager(client)
            reporter = AnalyticsReporter(client)
            optimizer = BudgetOptimizer(client)
            return client, campaign_manager, reporter, optimizer

    def test_create_campaign_monitor_optimize(self, full_setup, sample_targeting):
        """Test creating campaign, monitoring performance, and optimizing."""
        client, campaign_manager, reporter, optimizer = full_setup

        # Step 1: Create campaign
        client.create_campaign = Mock(return_value={
            'id': '123456789',
            'name': 'New Campaign',
            'objective': 'CONVERSIONS'
        })

        with patch.object(campaign_manager, '_get_default_targeting', return_value=sample_targeting):
            campaign = campaign_manager.create_campaign(
                name="New Campaign",
                objective="CONVERSIONS",
                daily_budget=50.0,
                status="PAUSED"
            )

        assert campaign['id'] == '123456789'

        # Step 2: Monitor performance
        insights_data = {
            'campaign_id': '123456789',
            'impressions': '10000',
            'clicks': '500',
            'spend': '50.0',
            'actions': [
                {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '10'}
            ]
        }

        client.get_campaign_insights = Mock(return_value=[insights_data])
        client.get_campaigns = Mock(return_value=[campaign])

        report = reporter.campaign_report('123456789')

        assert report['campaign_id'] == '123456789'
        assert report['roas'] > 0

        # Step 3: Detect anomalies if any
        anomalies = reporter.detect_anomalies('123456789')

        # Step 4: Optimize budget based on performance
        campaign['status'] = 'ACTIVE'
        campaign['daily_budget'] = 5000

        client.get_campaigns = Mock(return_value=[campaign])
        client.get_campaign_insights = Mock(return_value=[insights_data])
        optimizer._update_campaign_budget = Mock()

        changes = optimizer.optimize_budgets(dry_run=True)

        # Should have recommendations based on ROAS
        # ROAS = (10 * 50) / 50 = 10.0, which is excellent
        if changes:
            # Should recommend increase for such high ROAS
            assert any(c['change_pct'] > 0 for c in changes)

    def test_multi_campaign_management(self, full_setup):
        """Test managing multiple campaigns simultaneously."""
        client, campaign_manager, reporter, optimizer = full_setup

        # Create multiple campaigns
        campaigns = [
            {
                'id': f'{i}',
                'name': f'Campaign {i}',
                'status': 'ACTIVE',
                'daily_budget': 5000
            }
            for i in range(1, 4)
        ]

        # Mock insights for each
        insights_list = [
            {
                'spend': '50.0',
                'impressions': '10000',
                'clicks': '500',
                'actions': [
                    {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': str(10 * i)}
                ]
            }
            for i in range(1, 4)
        ]

        client.get_campaigns = Mock(return_value=campaigns)

        # Test listing campaigns
        campaign_list = campaign_manager.list_campaigns(include_insights=True)

        assert len(campaign_list) == 3

        # Test account-level report
        client.get_account_insights = Mock(return_value=insights_list)

        report = reporter.account_report()

        assert len(report) == 3

        # Test portfolio rebalancing
        client.get_campaigns = Mock(return_value=campaigns)
        client.get_campaign_insights = Mock(side_effect=insights_list)
        optimizer._update_campaign_budget = Mock()

        allocations = optimizer.rebalance_portfolio(
            total_budget=150.0,
            dry_run=True
        )

        assert len(allocations) == 3
        # Campaign 3 should get most budget (best ROAS)
        assert allocations[0]['campaign_id'] == '3'


class TestErrorHandlingIntegration:
    """Integration tests for error handling."""

    @pytest.fixture
    def client(self, mock_config_file, mock_facebook_ads_api, mock_account_object):
        """Create a client for testing."""
        with patch('src.api_client.AdAccount', return_value=mock_account_object):
            return FacebookAdsClient(config_path=mock_config_file)

    def test_api_error_during_optimization(self, client):
        """Test handling API errors during optimization."""
        optimizer = BudgetOptimizer(client)

        # Mock API error
        client.get_campaigns = Mock(side_effect=Exception("API Error"))

        with pytest.raises(Exception) as exc_info:
            optimizer.optimize_budgets()

        assert "API Error" in str(exc_info.value)

    def test_missing_data_handling(self, client):
        """Test handling missing data gracefully."""
        reporter = AnalyticsReporter(client)

        # Mock empty insights
        client.get_campaign_insights = Mock(return_value=[])

        report = reporter.campaign_report('123456789')

        assert 'error' in report

    def test_invalid_campaign_id(self, client):
        """Test handling invalid campaign IDs."""
        manager = CampaignManager(client)

        client.get_campaigns = Mock(return_value=[])

        with pytest.raises(ValueError):
            manager.duplicate_campaign('nonexistent')


class TestPerformanceMetrics:
    """Integration tests for performance metrics calculations."""

    @pytest.fixture
    def setup(self, mock_config_file, mock_facebook_ads_api, mock_account_object):
        """Setup client and reporter."""
        with patch('src.api_client.AdAccount', return_value=mock_account_object):
            client = FacebookAdsClient(config_path=mock_config_file)
            reporter = AnalyticsReporter(client)
            return client, reporter

    def test_metrics_calculation_accuracy(self, setup):
        """Test that all metrics are calculated accurately."""
        client, reporter = setup

        insights_data = {
            'impressions': '10000',
            'clicks': '500',
            'spend': '100.0',
            'reach': '8000',
            'frequency': '1.25',
            'actions': [
                {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '10'}
            ]
        }

        formatted = reporter._format_insights(insights_data)

        # Verify calculations
        assert formatted['ctr'] == pytest.approx(5.0, rel=0.01)  # (500/10000)*100
        assert formatted['cpc'] == pytest.approx(0.2, rel=0.01)  # 100/500
        assert formatted['conversions'] == 10
        assert formatted['cost_per_conversion'] == pytest.approx(10.0, rel=0.01)  # 100/10
        assert formatted['roas'] == pytest.approx(5.0, rel=0.01)  # (10*50)/100

    def test_metrics_with_zero_values(self, setup):
        """Test metrics calculation with zero values."""
        client, reporter = setup

        insights_data = {
            'impressions': '0',
            'clicks': '0',
            'spend': '0'
        }

        formatted = reporter._format_insights(insights_data)

        # Should handle zeros without errors
        assert formatted['ctr'] == 0
        assert formatted['cpc'] == 0
        assert formatted['roas'] == 0
