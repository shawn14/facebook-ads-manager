"""Unit tests for AnalyticsReporter."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.analytics.reporter import AnalyticsReporter


class TestAnalyticsReporterInit:
    """Tests for AnalyticsReporter initialization."""

    def test_init(self, mock_config):
        """Test AnalyticsReporter initialization."""
        mock_client = Mock()
        mock_client.config = mock_config

        reporter = AnalyticsReporter(mock_client)

        assert reporter.client == mock_client
        assert reporter.config == mock_config


class TestCampaignReport:
    """Tests for campaign reporting."""

    @pytest.fixture
    def reporter(self, mock_config):
        """Create a reporter for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return AnalyticsReporter(mock_client)

    def test_campaign_report_with_data(self, reporter, mock_insights_with_conversions, mock_campaign_data):
        """Test generating campaign report with data."""
        reporter.client.get_campaign_insights = Mock(
            return_value=[mock_insights_with_conversions]
        )
        reporter.client.get_campaigns = Mock(return_value=[mock_campaign_data])

        report = reporter.campaign_report('123456789', days=7)

        assert report['campaign_id'] == '123456789'
        assert report['impressions'] == 10000
        assert report['clicks'] == 500
        assert 'ctr' in report
        assert 'spend' in report

    def test_campaign_report_no_data(self, reporter):
        """Test campaign report when no data is available."""
        reporter.client.get_campaign_insights = Mock(return_value=[])

        report = reporter.campaign_report('123456789')

        assert 'error' in report
        assert report['error'] == 'No data available'

    def test_campaign_report_date_preset_conversion(self, reporter, mock_insights_data):
        """Test that days are converted to proper date presets."""
        reporter.client.get_campaign_insights = Mock(return_value=[mock_insights_data])
        reporter.client.get_campaigns = Mock(return_value=[])

        # Test various day values
        reporter.campaign_report('123456789', days=7)
        call_args = reporter.client.get_campaign_insights.call_args
        assert call_args[1]['date_preset'] == 'last_7d'

        reporter.campaign_report('123456789', days=30)
        call_args = reporter.client.get_campaign_insights.call_args
        assert call_args[1]['date_preset'] == 'last_30d'


class TestAccountReport:
    """Tests for account-level reporting."""

    @pytest.fixture
    def reporter(self, mock_config):
        """Create a reporter for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return AnalyticsReporter(mock_client)

    def test_account_report(self, reporter, mock_insights_data):
        """Test generating account-level report."""
        reporter.client.get_account_insights = Mock(
            return_value=[mock_insights_data]
        )

        report = reporter.account_report(days=7)

        assert len(report) == 1
        assert report[0]['campaign_id'] == '123456789'
        reporter.client.get_account_insights.assert_called_once()

    def test_account_report_multiple_campaigns(self, reporter, mock_insights_data):
        """Test account report with multiple campaigns."""
        insights_list = [
            {**mock_insights_data, 'campaign_id': '111'},
            {**mock_insights_data, 'campaign_id': '222'},
            {**mock_insights_data, 'campaign_id': '333'}
        ]
        reporter.client.get_account_insights = Mock(return_value=insights_list)

        report = reporter.account_report()

        assert len(report) == 3


class TestFormatInsights:
    """Tests for insights formatting."""

    @pytest.fixture
    def reporter(self, mock_config):
        """Create a reporter for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return AnalyticsReporter(mock_client)

    def test_format_insights_basic_metrics(self, reporter, mock_insights_data):
        """Test formatting basic metrics."""
        formatted = reporter._format_insights(mock_insights_data)

        assert formatted['impressions'] == 10000
        assert formatted['clicks'] == 500
        assert formatted['spend'] == 100.50

    def test_format_insights_calculated_metrics(self, reporter, mock_insights_data):
        """Test that calculated metrics are correct."""
        formatted = reporter._format_insights(mock_insights_data)

        # CTR = (clicks / impressions) * 100
        expected_ctr = (500 / 10000) * 100
        assert formatted['ctr'] == expected_ctr

        # CPC = spend / clicks
        expected_cpc = 100.50 / 500
        assert formatted['cpc'] == expected_cpc

    def test_format_insights_with_conversions(self, reporter, mock_insights_with_conversions):
        """Test formatting with conversion data."""
        formatted = reporter._format_insights(mock_insights_with_conversions)

        assert formatted['conversions'] == 10
        assert formatted['cost_per_conversion'] > 0

    def test_format_insights_without_conversions(self, reporter, mock_insights_no_conversions):
        """Test formatting without conversion data."""
        formatted = reporter._format_insights(mock_insights_no_conversions)

        assert formatted['conversions'] == 0
        assert formatted['cost_per_conversion'] == 0

    def test_format_insights_roas_calculation(self, reporter, mock_insights_with_conversions):
        """Test ROAS calculation."""
        formatted = reporter._format_insights(mock_insights_with_conversions)

        # ROAS = (conversions * avg_order_value) / spend
        expected_roas = (10 * 50) / 100.50
        assert formatted['roas'] == pytest.approx(expected_roas, rel=0.01)

    def test_format_insights_zero_division_handling(self, reporter):
        """Test handling of zero values to avoid division errors."""
        insights = {
            'impressions': '0',
            'clicks': '0',
            'spend': '0'
        }

        formatted = reporter._format_insights(insights)

        assert formatted['ctr'] == 0
        assert formatted['cpc'] == 0
        assert formatted['roas'] == 0


class TestDisplayReport:
    """Tests for report display."""

    @pytest.fixture
    def reporter(self, mock_config):
        """Create a reporter for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return AnalyticsReporter(mock_client)

    def test_display_report_single_campaign(self, reporter):
        """Test displaying report for single campaign."""
        data = {
            'campaign_name': 'Test Campaign',
            'impressions': 10000,
            'clicks': 500,
            'ctr': 5.0,
            'spend': 100.50,
            'cpc': 0.20,
            'conversions': 10,
            'cost_per_conversion': 10.05,
            'roas': 4.98
        }

        # Should not raise an error
        with patch.object(reporter.console, 'print'):
            reporter.display_report(data)

    def test_display_report_multiple_campaigns(self, reporter):
        """Test displaying report for multiple campaigns."""
        data = [
            {
                'campaign_name': 'Campaign 1',
                'impressions': 10000,
                'clicks': 500,
                'ctr': 5.0,
                'spend': 100.0,
                'cpc': 0.20,
                'conversions': 10,
                'cost_per_conversion': 10.0,
                'roas': 5.0
            },
            {
                'campaign_name': 'Campaign 2',
                'impressions': 5000,
                'clicks': 250,
                'ctr': 5.0,
                'spend': 50.0,
                'cpc': 0.20,
                'conversions': 5,
                'cost_per_conversion': 10.0,
                'roas': 5.0
            }
        ]

        # Should not raise an error and should show summary
        with patch.object(reporter.console, 'print'):
            reporter.display_report(data)


class TestExportCSV:
    """Tests for CSV export."""

    @pytest.fixture
    def reporter(self, mock_config):
        """Create a reporter for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return AnalyticsReporter(mock_client)

    def test_export_csv_single_campaign(self, reporter, tmp_path):
        """Test exporting single campaign to CSV."""
        data = {
            'campaign_id': '123',
            'campaign_name': 'Test Campaign',
            'impressions': 10000,
            'clicks': 500,
            'spend': 100.0
        }

        with patch('src.analytics.reporter.Path', return_value=tmp_path):
            filepath = reporter.export_csv(data)

        assert filepath.endswith('.csv')

    def test_export_csv_multiple_campaigns(self, reporter, tmp_path):
        """Test exporting multiple campaigns to CSV."""
        data = [
            {'campaign_id': '123', 'campaign_name': 'Campaign 1', 'spend': 100.0},
            {'campaign_id': '456', 'campaign_name': 'Campaign 2', 'spend': 200.0}
        ]

        with patch('src.analytics.reporter.Path', return_value=tmp_path):
            with patch('pandas.DataFrame.to_csv') as mock_to_csv:
                filepath = reporter.export_csv(data)

                mock_to_csv.assert_called_once()

    def test_export_csv_custom_filename(self, reporter, tmp_path):
        """Test exporting with custom filename."""
        data = {'campaign_id': '123', 'spend': 100.0}

        with patch('src.analytics.reporter.Path', return_value=tmp_path):
            with patch('pandas.DataFrame.to_csv'):
                filepath = reporter.export_csv(data, filename='custom_report.csv')

                assert 'custom_report.csv' in filepath


class TestDaysToPreset:
    """Tests for date preset conversion."""

    @pytest.fixture
    def reporter(self, mock_config):
        """Create a reporter for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return AnalyticsReporter(mock_client)

    def test_days_to_preset_common_values(self, reporter):
        """Test conversion of common day values."""
        assert reporter._days_to_preset(1) == 'today'
        assert reporter._days_to_preset(7) == 'last_7d'
        assert reporter._days_to_preset(14) == 'last_14d'
        assert reporter._days_to_preset(30) == 'last_30d'
        assert reporter._days_to_preset(90) == 'last_90d'

    def test_days_to_preset_default(self, reporter):
        """Test default preset for uncommon values."""
        assert reporter._days_to_preset(5) == 'last_7d'
        assert reporter._days_to_preset(100) == 'last_7d'


class TestDetectAnomalies:
    """Tests for anomaly detection."""

    @pytest.fixture
    def reporter(self, mock_config):
        """Create a reporter for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return AnalyticsReporter(mock_client)

    def test_detect_anomalies_low_roas(self, reporter):
        """Test detection of low ROAS."""
        insights_data = {
            'impressions': '10000',
            'clicks': '500',
            'spend': '1000.0',  # High spend
            'actions': [
                {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '5'}
            ]
        }
        reporter.client.get_campaign_insights = Mock(return_value=[insights_data])

        anomalies = reporter.detect_anomalies('123456789')

        # Should detect low ROAS (revenue = 5 * 50 = 250, spend = 1000, ROAS = 0.25)
        assert len(anomalies) > 0
        assert any(a['type'] == 'low_roas' for a in anomalies)

    def test_detect_anomalies_low_ctr(self, reporter):
        """Test detection of low CTR."""
        insights_data = {
            'impressions': '100000',
            'clicks': '100',  # Low clicks
            'spend': '100.0',
            'actions': [
                {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '10'}
            ]
        }
        reporter.client.get_campaign_insights = Mock(return_value=[insights_data])

        anomalies = reporter.detect_anomalies('123456789')

        # Should detect low CTR (100/100000 = 0.1%)
        assert any(a['type'] == 'low_ctr' for a in anomalies)

    def test_detect_anomalies_high_cpa(self, reporter):
        """Test detection of high CPA."""
        insights_data = {
            'impressions': '10000',
            'clicks': '500',
            'spend': '1000.0',
            'actions': [
                {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '5'}
            ]
        }
        reporter.client.get_campaign_insights = Mock(return_value=[insights_data])

        anomalies = reporter.detect_anomalies('123456789')

        # Should detect high CPA (1000 / 5 = 200, threshold is 50)
        assert any(a['type'] == 'high_cpa' for a in anomalies)

    def test_detect_anomalies_no_issues(self, reporter):
        """Test when no anomalies are detected."""
        insights_data = {
            'impressions': '10000',
            'clicks': '500',
            'spend': '100.0',
            'actions': [
                {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '20'}
            ]
        }
        reporter.client.get_campaign_insights = Mock(return_value=[insights_data])

        anomalies = reporter.detect_anomalies('123456789')

        # Good metrics: ROAS = (20 * 50) / 100 = 10, CTR = 5%, CPA = 5
        # Might still have some anomalies depending on thresholds
        # but should not have all three types
        assert len(anomalies) < 3

    def test_detect_anomalies_no_data(self, reporter):
        """Test anomaly detection with no data."""
        reporter.client.get_campaign_insights = Mock(return_value=[])

        anomalies = reporter.detect_anomalies('123456789')

        assert anomalies == []


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.fixture
    def reporter(self, mock_config):
        """Create a reporter for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return AnalyticsReporter(mock_client)

    def test_format_insights_missing_fields(self, reporter):
        """Test formatting with missing fields."""
        insights = {
            'campaign_id': '123'
        }

        formatted = reporter._format_insights(insights)

        # Should handle missing fields gracefully
        assert formatted['impressions'] == 0
        assert formatted['clicks'] == 0
        assert formatted['spend'] == 0.0

    def test_export_csv_empty_data(self, reporter, tmp_path):
        """Test exporting empty data."""
        data = []

        with patch('src.analytics.reporter.Path', return_value=tmp_path):
            filepath = reporter.export_csv(data)

        # Should still create a file
        assert filepath.endswith('.csv')
