"""Tests for advanced analytics module."""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json

from src.analytics.advanced_analytics import AdvancedAnalytics


class MockAPIClient:
    """Mock API client for testing."""

    def __init__(self):
        self.config = {
            'analytics': {
                'avg_order_value': 50
            }
        }

    def get_campaign_insights(self, campaign_id, **kwargs):
        """Generate mock time-series data."""
        # Generate 90 days of synthetic data with trends
        days = 90
        dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]

        data = []
        base_spend = 100
        base_conversions = 10

        for i, date in enumerate(dates):
            # Add trend (increasing spend, conversions)
            trend_factor = 1 + (i / days) * 0.5

            # Add weekly seasonality (weekends are better)
            weekday = date.weekday()
            seasonal_factor = 1.2 if weekday in [5, 6] else 1.0

            # Add some noise
            noise = np.random.normal(1, 0.1)

            spend = base_spend * trend_factor * seasonal_factor * noise
            conversions = base_conversions * trend_factor * seasonal_factor * noise
            impressions = int(spend * 100)
            clicks = int(impressions * 0.02)

            data.append({
                'date_start': date.strftime('%Y-%m-%d'),
                'date_stop': date.strftime('%Y-%m-%d'),
                'campaign_id': campaign_id,
                'campaign_name': 'Test Campaign',
                'impressions': str(impressions),
                'clicks': str(clicks),
                'spend': str(spend),
                'reach': str(int(impressions * 0.7)),
                'frequency': '1.3',
                'actions': [
                    {
                        'action_type': 'purchase',
                        'value': str(int(conversions))
                    }
                ]
            })

        return data

    def get_account_insights(self, **kwargs):
        """Get account-level insights."""
        return self.get_campaign_insights('12345', **kwargs)


@pytest.fixture
def analytics():
    """Create analytics instance with mock client."""
    client = MockAPIClient()
    return AdvancedAnalytics(client)


def test_trend_detection(analytics):
    """Test trend detection functionality."""
    results = analytics.detect_trends(campaign_id='12345', days=90)

    assert 'spend' in results
    assert 'conversions' in results
    assert 'roas' in results

    # Check spend trend (should be increasing)
    spend_trend = results['spend']
    assert spend_trend['trend'] == 'increasing'
    assert spend_trend['significance'] == 'significant'
    assert spend_trend['r_squared'] > 0.5
    assert spend_trend['percent_change'] > 0

    # Check for seasonality detection
    assert 'seasonality' in spend_trend
    assert isinstance(spend_trend['seasonality'], dict)


def test_forecast(analytics):
    """Test metric forecasting."""
    forecast = analytics.forecast_metric(
        campaign_id='12345',
        metric='conversions',
        days_ahead=7,
        days_history=30
    )

    assert 'error' not in forecast
    assert len(forecast['forecast']) == 7
    assert len(forecast['upper_bound']) == 7
    assert len(forecast['lower_bound']) == 7
    assert len(forecast['dates']) == 7
    assert forecast['confidence_level'] == 0.95
    assert forecast['model_r_squared'] >= 0


def test_correlation_analysis(analytics):
    """Test correlation analysis."""
    results = analytics.correlation_analysis(campaign_id='12345', days=90)

    assert 'error' not in results
    assert 'correlation_matrix' in results
    assert 'strong_correlations' in results

    # Check that correlation matrix has expected metrics
    corr_matrix = results['correlation_matrix']
    assert 'spend' in corr_matrix
    assert 'conversions' in corr_matrix


def test_confidence_intervals(analytics):
    """Test confidence interval calculation."""
    results = analytics.performance_confidence_intervals(
        campaign_id='12345',
        days=30,
        confidence=0.95
    )

    assert 'error' not in results
    assert 'spend' in results
    assert 'conversions' in results

    # Check confidence interval structure
    spend_ci = results['spend']
    assert 'mean' in spend_ci
    assert 'std' in spend_ci
    assert 'lower_bound' in spend_ci
    assert 'upper_bound' in spend_ci
    assert spend_ci['lower_bound'] < spend_ci['mean'] < spend_ci['upper_bound']


def test_ab_test_significance(analytics):
    """Test A/B test significance testing."""
    variant_a = {'conversions': [10, 12, 11, 13, 10, 12, 11]}
    variant_b = {'conversions': [15, 17, 16, 18, 15, 17, 16]}

    results = analytics.ab_test_significance(variant_a, variant_b, metric='conversions')

    assert 'error' not in results
    assert results['metric'] == 'conversions'
    assert results['variant_b_mean'] > results['variant_a_mean']
    assert results['significant'] == True
    assert results['winner'] == 'B'
    assert results['p_value'] < 0.05


def test_change_point_detection(analytics):
    """Test change point detection."""
    results = analytics.detect_trends(campaign_id='12345', days=90)

    # Check if change points were detected
    spend_trend = results['spend']
    assert 'change_points' in spend_trend
    assert isinstance(spend_trend['change_points'], list)

    # If change points exist, verify structure
    if spend_trend['change_points']:
        cp = spend_trend['change_points'][0]
        assert 'date' in cp
        assert 'value' in cp
        assert 'z_score' in cp
        assert 'type' in cp


def test_visualizations(analytics, tmp_path):
    """Test visualization generation."""
    # Override exports directory for testing
    analytics.exports_dir = tmp_path

    # Test trend visualization
    trend_path = analytics.visualize_trends(
        campaign_id='12345',
        days=90,
        metrics=['spend', 'conversions'],
        filename='test_trends.png'
    )

    assert trend_path
    assert Path(trend_path).exists()
    assert Path(trend_path).suffix == '.png'

    # Test correlation visualization
    corr_path = analytics.visualize_correlations(
        campaign_id='12345',
        days=90,
        filename='test_corr.png'
    )

    assert corr_path
    assert Path(corr_path).exists()
    assert Path(corr_path).suffix == '.png'


def test_comprehensive_report(analytics, tmp_path):
    """Test comprehensive insights report generation."""
    analytics.exports_dir = tmp_path

    report = analytics.generate_insights_report(
        campaign_id='12345',
        days=90
    )

    assert 'generated_at' in report
    assert 'period_days' in report
    assert report['period_days'] == 90

    # Check report sections
    assert 'trends' in report
    assert 'correlations' in report
    assert 'confidence_intervals' in report
    assert 'forecasts' in report
    assert 'visualizations' in report

    # Verify forecasts for key metrics
    assert 'conversions' in report['forecasts']
    assert 'spend' in report['forecasts']

    # Check visualization files were created
    assert report['visualizations']['trends']
    assert report['visualizations']['correlations']

    # Verify report JSON was saved
    assert 'report_file' in report
    assert Path(report['report_file']).exists()

    # Verify JSON can be loaded
    with open(report['report_file'], 'r') as f:
        loaded_report = json.load(f)
    assert loaded_report['period_days'] == 90


def test_seasonality_detection(analytics):
    """Test weekly seasonality detection."""
    # Create data with strong weekly pattern
    series = np.array([10, 11, 12, 13, 14, 20, 22] * 10)  # Weekend spikes

    seasonality = analytics._detect_seasonality(series, period=7)

    assert 'detected' in seasonality
    assert 'period' in seasonality or not seasonality['detected']


def test_empty_data_handling(analytics):
    """Test handling of empty or insufficient data."""
    # Create a mock client that returns empty data
    empty_client = MockAPIClient()
    empty_client.get_campaign_insights = lambda *args, **kwargs: []

    empty_analytics = AdvancedAnalytics(empty_client)

    # Test trend detection with no data
    results = empty_analytics.detect_trends(campaign_id='empty', days=90)
    assert 'error' in results

    # Test forecast with no data
    forecast = empty_analytics.forecast_metric(campaign_id='empty')
    assert 'error' in forecast


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])
