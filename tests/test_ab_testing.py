"""Unit tests for ABTestManager."""

import pytest
from unittest.mock import Mock, patch
import numpy as np

from src.optimization.ab_testing import ABTestManager


class TestABTestManagerInit:
    """Tests for ABTestManager initialization."""

    def test_init(self, mock_config):
        """Test ABTestManager initialization."""
        mock_client = Mock()
        mock_client.config = mock_config

        ab_test = ABTestManager(mock_client)

        assert ab_test.client == mock_client
        assert ab_test.config == mock_config


class TestCreateTest:
    """Tests for A/B test creation."""

    @pytest.fixture
    def ab_test(self, mock_config):
        """Create an AB test manager for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return ABTestManager(mock_client)

    def test_create_test_basic(self, ab_test, mock_campaign_data):
        """Test creating a basic A/B test."""
        ab_test.client.get_campaigns = Mock(return_value=[mock_campaign_data])
        ab_test.client.create_campaign = Mock(return_value={
            'id': '999',
            'name': 'Test - Variant 1'
        })

        test = ab_test.create_test(
            base_campaign_id='123456789',
            num_variants=2,
            test_name='Landing Page Test'
        )

        assert test['name'] == 'Landing Page Test'
        assert test['base_campaign_id'] == '123456789'
        assert len(test['variants']) == 2
        assert test['status'] == 'created'

    def test_create_test_multiple_variants(self, ab_test, mock_campaign_data):
        """Test creating test with multiple variants."""
        ab_test.client.get_campaigns = Mock(return_value=[mock_campaign_data])
        ab_test.client.create_campaign = Mock(return_value={
            'id': '999',
            'name': 'Test Variant'
        })

        test = ab_test.create_test(
            base_campaign_id='123456789',
            num_variants=4,
            test_name='Multivariate Test'
        )

        assert len(test['variants']) == 4
        # Should be called 4 times
        assert ab_test.client.create_campaign.call_count == 4

    def test_create_test_budget_split(self, ab_test, mock_campaign_data):
        """Test that budget is split evenly among variants."""
        mock_campaign_data['daily_budget'] = 10000  # $100
        ab_test.client.get_campaigns = Mock(return_value=[mock_campaign_data])
        ab_test.client.create_campaign = Mock(return_value={
            'id': '999',
            'name': 'Test Variant'
        })

        test = ab_test.create_test(
            base_campaign_id='123456789',
            num_variants=2,
            test_name='Split Test'
        )

        # Each variant should get $50
        for variant in test['variants']:
            assert variant['budget'] == 50.0

    def test_create_test_campaign_not_found(self, ab_test):
        """Test creating test with non-existent campaign."""
        ab_test.client.get_campaigns = Mock(return_value=[])

        with pytest.raises(ValueError) as exc_info:
            ab_test.create_test(
                base_campaign_id='nonexistent',
                num_variants=2,
                test_name='Test'
            )

        assert "not found" in str(exc_info.value)

    def test_create_test_variants_start_paused(self, ab_test, mock_campaign_data):
        """Test that variant campaigns start paused."""
        ab_test.client.get_campaigns = Mock(return_value=[mock_campaign_data])
        ab_test.client.create_campaign = Mock(return_value={
            'id': '999',
            'name': 'Test Variant'
        })

        ab_test.create_test(
            base_campaign_id='123456789',
            num_variants=2,
            test_name='Test'
        )

        # Check that campaigns were created with PAUSED status
        calls = ab_test.client.create_campaign.call_args_list
        for call in calls:
            assert call[1]['status'] == 'PAUSED'


class TestAnalyzeTest:
    """Tests for A/B test analysis."""

    @pytest.fixture
    def ab_test(self, mock_config):
        """Create an AB test manager for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return ABTestManager(mock_client)

    def test_analyze_test_basic(self, ab_test):
        """Test basic test analysis."""
        campaigns = [
            {'id': '1', 'name': 'test_123 - Variant 1', 'status': 'ACTIVE'},
            {'id': '2', 'name': 'test_123 - Variant 2', 'status': 'ACTIVE'}
        ]

        insights = [
            {
                'impressions': '10000',
                'clicks': '500',
                'actions': [
                    {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '50'}
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

        ab_test.client.get_campaigns = Mock(return_value=campaigns)
        ab_test.client.get_campaign_insights = Mock(side_effect=insights)

        results = ab_test.analyze_test('test_123')

        assert results['test_id'] == 'test_123'
        assert len(results['variants']) == 2
        assert results['variants'][0]['conversions'] == 50
        assert results['variants'][1]['conversions'] == 30

    def test_analyze_test_no_campaigns(self, ab_test):
        """Test analysis with no matching campaigns."""
        ab_test.client.get_campaigns = Mock(return_value=[])

        with pytest.raises(ValueError) as exc_info:
            ab_test.analyze_test('nonexistent')

        assert "No campaigns found" in str(exc_info.value)

    def test_analyze_test_calculates_metrics(self, ab_test):
        """Test that CTR and CVR are calculated correctly."""
        campaigns = [
            {'id': '1', 'name': 'test_123 - Variant 1'}
        ]

        insights = [
            {
                'impressions': '10000',
                'clicks': '500',
                'actions': [
                    {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '50'}
                ]
            }
        ]

        ab_test.client.get_campaigns = Mock(return_value=campaigns)
        ab_test.client.get_campaign_insights = Mock(side_effect=insights)

        results = ab_test.analyze_test('test_123')

        variant = results['variants'][0]
        assert variant['ctr'] == 5.0  # (500 / 10000) * 100
        assert variant['cvr'] == 10.0  # (50 / 500) * 100


class TestDetermineWinner:
    """Tests for determining test winner."""

    @pytest.fixture
    def ab_test(self, mock_config):
        """Create an AB test manager for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return ABTestManager(mock_client)

    def test_determine_winner_clear_winner(self, ab_test):
        """Test determining winner with clear statistical significance."""
        variants = [
            {
                'id': '1',
                'name': 'Variant 1',
                'clicks': 1000,
                'conversions': 100,
                'cvr': 10.0
            },
            {
                'id': '2',
                'name': 'Variant 2',
                'clicks': 1000,
                'conversions': 50,
                'cvr': 5.0
            }
        ]

        winner, confidence = ab_test._determine_winner(variants, 'conversions')

        # Variant 1 should win with high confidence
        assert winner == '1'
        assert confidence > 0.90

    def test_determine_winner_insufficient_data(self, ab_test):
        """Test winner determination with insufficient data."""
        variants = [
            {
                'id': '1',
                'name': 'Variant 1',
                'clicks': 10,  # Too few
                'conversions': 2,
                'cvr': 20.0
            },
            {
                'id': '2',
                'name': 'Variant 2',
                'clicks': 10,  # Too few
                'conversions': 1,
                'cvr': 10.0
            }
        ]

        winner, confidence = ab_test._determine_winner(variants, 'conversions')

        # Should return None due to insufficient data
        assert winner is None
        assert confidence == 0

    def test_determine_winner_no_significant_difference(self, ab_test):
        """Test when there's no significant difference."""
        variants = [
            {
                'id': '1',
                'name': 'Variant 1',
                'clicks': 1000,
                'conversions': 100,
                'cvr': 10.0
            },
            {
                'id': '2',
                'name': 'Variant 2',
                'clicks': 1000,
                'conversions': 98,
                'cvr': 9.8
            }
        ]

        winner, confidence = ab_test._determine_winner(variants, 'conversions')

        # Difference is too small, may not reach confidence threshold
        if winner is not None:
            assert confidence < 0.95

    def test_determine_winner_single_variant(self, ab_test):
        """Test winner determination with single variant."""
        variants = [
            {
                'id': '1',
                'name': 'Variant 1',
                'clicks': 1000,
                'conversions': 100,
                'cvr': 10.0
            }
        ]

        winner, confidence = ab_test._determine_winner(variants, 'conversions')

        assert winner is None
        assert confidence == 0

    def test_determine_winner_zero_clicks(self, ab_test):
        """Test winner determination with zero clicks."""
        variants = [
            {
                'id': '1',
                'name': 'Variant 1',
                'clicks': 0,
                'conversions': 0,
                'cvr': 0
            },
            {
                'id': '2',
                'name': 'Variant 2',
                'clicks': 0,
                'conversions': 0,
                'cvr': 0
            }
        ]

        winner, confidence = ab_test._determine_winner(variants, 'conversions')

        assert winner is None


class TestExtractConversions:
    """Tests for conversion extraction."""

    @pytest.fixture
    def ab_test(self, mock_config):
        """Create an AB test manager for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return ABTestManager(mock_client)

    def test_extract_conversions_purchase(self, ab_test):
        """Test extracting purchase conversions."""
        insight = {
            'actions': [
                {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '25'}
            ]
        }

        conversions = ab_test._extract_conversions(insight)

        assert conversions == 25

    def test_extract_conversions_generic(self, ab_test):
        """Test extracting generic conversions."""
        insight = {
            'actions': [
                {'action_type': 'conversion', 'value': '15'}
            ]
        }

        conversions = ab_test._extract_conversions(insight)

        assert conversions == 15

    def test_extract_conversions_no_actions(self, ab_test):
        """Test extraction with no actions."""
        insight = {}

        conversions = ab_test._extract_conversions(insight)

        assert conversions == 0

    def test_extract_conversions_no_conversion_actions(self, ab_test):
        """Test extraction with no conversion-type actions."""
        insight = {
            'actions': [
                {'action_type': 'link_click', 'value': '200'},
                {'action_type': 'page_engagement', 'value': '150'}
            ]
        }

        conversions = ab_test._extract_conversions(insight)

        assert conversions == 0


class TestDisplayResults:
    """Tests for results display."""

    @pytest.fixture
    def ab_test(self, mock_config):
        """Create an AB test manager for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return ABTestManager(mock_client)

    def test_display_results_with_winner(self, ab_test):
        """Test displaying results with a winner."""
        results = {
            'test_id': 'test_123',
            'variants': [
                {
                    'id': '1',
                    'name': 'Variant 1',
                    'impressions': 10000,
                    'clicks': 500,
                    'ctr': 5.0,
                    'conversions': 50,
                    'cvr': 10.0
                },
                {
                    'id': '2',
                    'name': 'Variant 2',
                    'impressions': 10000,
                    'clicks': 400,
                    'ctr': 4.0,
                    'conversions': 30,
                    'cvr': 7.5
                }
            ],
            'winner': '1',
            'confidence': 0.95
        }

        # Should not raise an error
        with patch.object(ab_test.console, 'print'):
            ab_test.display_results(results)

    def test_display_results_no_winner(self, ab_test):
        """Test displaying results without a winner."""
        results = {
            'test_id': 'test_123',
            'variants': [
                {
                    'id': '1',
                    'name': 'Variant 1',
                    'impressions': 100,
                    'clicks': 10,
                    'ctr': 10.0,
                    'conversions': 2,
                    'cvr': 20.0
                },
                {
                    'id': '2',
                    'name': 'Variant 2',
                    'impressions': 100,
                    'clicks': 8,
                    'ctr': 8.0,
                    'conversions': 1,
                    'cvr': 12.5
                }
            ],
            'winner': None,
            'confidence': 0.5
        }

        # Should not raise an error
        with patch.object(ab_test.console, 'print'):
            ab_test.display_results(results)


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""

    @pytest.fixture
    def ab_test(self, mock_config):
        """Create an AB test manager for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return ABTestManager(mock_client)

    def test_complete_ab_test_workflow(self, ab_test, mock_campaign_data):
        """Test complete A/B test workflow."""
        # Create test
        ab_test.client.get_campaigns = Mock(return_value=[mock_campaign_data])
        ab_test.client.create_campaign = Mock(return_value={
            'id': '999',
            'name': 'Test Variant'
        })

        test = ab_test.create_test(
            base_campaign_id='123456789',
            num_variants=2,
            test_name='Complete Test'
        )

        assert test is not None
        assert len(test['variants']) == 2

        # Analyze test (mock the campaigns)
        campaigns = [
            {'id': '1', 'name': f"{test['name']} - Variant 1"},
            {'id': '2', 'name': f"{test['name']} - Variant 2"}
        ]

        insights = [
            {
                'impressions': '10000',
                'clicks': '500',
                'actions': [
                    {'action_type': 'offsite_conversion.fb_pixel_purchase', 'value': '50'}
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

        ab_test.client.get_campaigns = Mock(return_value=campaigns)
        ab_test.client.get_campaign_insights = Mock(side_effect=insights)

        results = ab_test.analyze_test(test['name'])

        assert results is not None
        assert len(results['variants']) == 2


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.fixture
    def ab_test(self, mock_config):
        """Create an AB test manager for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return ABTestManager(mock_client)

    def test_create_test_zero_variants(self, ab_test, mock_campaign_data):
        """Test creating test with zero variants."""
        ab_test.client.get_campaigns = Mock(return_value=[mock_campaign_data])

        test = ab_test.create_test(
            base_campaign_id='123456789',
            num_variants=0,
            test_name='Zero Variant Test'
        )

        assert len(test['variants']) == 0

    def test_analyze_test_no_insights(self, ab_test):
        """Test analysis when campaigns have no insights."""
        campaigns = [
            {'id': '1', 'name': 'test_123 - Variant 1'}
        ]

        ab_test.client.get_campaigns = Mock(return_value=campaigns)
        ab_test.client.get_campaign_insights = Mock(return_value=[])

        results = ab_test.analyze_test('test_123')

        # Should handle gracefully
        assert results['test_id'] == 'test_123'
        # Variants list might be empty or have entries with no data
        assert 'variants' in results

    def test_determine_winner_equal_performance(self, ab_test):
        """Test winner determination with exactly equal performance."""
        variants = [
            {
                'id': '1',
                'name': 'Variant 1',
                'clicks': 1000,
                'conversions': 100,
                'cvr': 10.0
            },
            {
                'id': '2',
                'name': 'Variant 2',
                'clicks': 1000,
                'conversions': 100,
                'cvr': 10.0
            }
        ]

        winner, confidence = ab_test._determine_winner(variants, 'conversions')

        # With equal performance, confidence should be very low
        # Winner might be declared based on first position but with low confidence
        if confidence > 0:
            assert confidence < 0.5
