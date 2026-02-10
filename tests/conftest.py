"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import yaml


@pytest.fixture
def mock_config():
    """Mock configuration data."""
    return {
        'facebook': {
            'app_id': 'test_app_id',
            'app_secret': 'test_app_secret',
            'access_token': 'test_access_token',
            'ad_account_id': 'act_123456789',
            'api_version': 'v19.0'
        },
        'targeting': {
            'default_countries': ['US'],
            'default_age_min': 25,
            'default_age_max': 65
        },
        'campaigns': {
            'min_daily_budget': 10,
            'max_daily_budget': 5000
        },
        'optimization': {
            'min_roas': 1.5,
            'min_ctr': 0.5,
            'max_cpa': 50,
            'confidence_level': 0.95
        },
        'analytics': {
            'avg_order_value': 50
        }
    }


@pytest.fixture
def mock_config_file(tmp_path, mock_config):
    """Create a temporary config file."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"

    with open(config_file, 'w') as f:
        yaml.dump(mock_config, f)

    return str(config_file)


@pytest.fixture
def mock_campaign_data():
    """Mock campaign data."""
    return {
        'id': '123456789',
        'name': 'Test Campaign',
        'objective': 'LINK_CLICKS',
        'status': 'ACTIVE',
        'daily_budget': 5000,  # in cents
        'lifetime_budget': None,
        'created_time': '2024-01-01T00:00:00+0000',
        'updated_time': '2024-01-02T00:00:00+0000'
    }


@pytest.fixture
def mock_adset_data():
    """Mock ad set data."""
    return {
        'id': '987654321',
        'name': 'Test Ad Set',
        'campaign_id': '123456789',
        'status': 'ACTIVE',
        'daily_budget': 5000,
        'optimization_goal': 'LINK_CLICKS',
        'billing_event': 'IMPRESSIONS',
        'created_time': '2024-01-01T00:00:00+0000',
        'updated_time': '2024-01-02T00:00:00+0000'
    }


@pytest.fixture
def mock_insights_data():
    """Mock insights/analytics data."""
    return {
        'campaign_id': '123456789',
        'campaign_name': 'Test Campaign',
        'impressions': '10000',
        'clicks': '500',
        'spend': '100.50',
        'ctr': '5.0',
        'cpc': '0.20',
        'frequency': '1.5',
        'reach': '8000',
        'actions': [
            {
                'action_type': 'offsite_conversion.fb_pixel_purchase',
                'value': '10'
            }
        ]
    }


@pytest.fixture
def mock_insights_with_conversions():
    """Mock insights data with conversions."""
    return {
        'campaign_id': '123456789',
        'campaign_name': 'Test Campaign',
        'impressions': '10000',
        'clicks': '500',
        'spend': '100.50',
        'ctr': '5.0',
        'cpc': '0.20',
        'frequency': '1.5',
        'reach': '8000',
        'actions': [
            {
                'action_type': 'offsite_conversion.fb_pixel_purchase',
                'value': '10'
            },
            {
                'action_type': 'link_click',
                'value': '500'
            }
        ]
    }


@pytest.fixture
def mock_insights_no_conversions():
    """Mock insights data without conversions."""
    return {
        'campaign_id': '123456789',
        'campaign_name': 'Test Campaign',
        'impressions': '10000',
        'clicks': '100',
        'spend': '50.00',
        'ctr': '1.0',
        'cpc': '0.50',
        'frequency': '1.2',
        'reach': '8500'
    }


@pytest.fixture
def mock_ad_account():
    """Mock Facebook AdAccount object."""
    account = Mock()
    account.__getitem__ = Mock(side_effect=lambda key: f'mock_{key}')
    return account


@pytest.fixture
def mock_campaign_object():
    """Mock Facebook Campaign object."""
    campaign = Mock()
    campaign.__getitem__ = Mock(side_effect=lambda key: {
        'id': '123456789',
        'name': 'Test Campaign'
    }.get(key, f'mock_{key}'))
    campaign.api_update = Mock()
    campaign.api_delete = Mock()
    campaign.get_insights = Mock(return_value=[])
    campaign.get_ad_sets = Mock(return_value=[])
    return campaign


@pytest.fixture
def mock_adset_object():
    """Mock Facebook AdSet object."""
    adset = Mock()
    adset.__getitem__ = Mock(side_effect=lambda key: {
        'id': '987654321',
        'name': 'Test Ad Set'
    }.get(key, f'mock_{key}'))
    adset.api_update = Mock()
    return adset


@pytest.fixture
def mock_facebook_ads_api():
    """Mock FacebookAdsApi initialization."""
    with patch('src.api_client.FacebookAdsApi') as mock_api:
        mock_api.init = Mock()
        yield mock_api


@pytest.fixture
def mock_account_object():
    """Mock account object with methods."""
    account = Mock()
    account.api_get = Mock(return_value={
        'id': 'act_123456789',
        'name': 'Test Account',
        'currency': 'USD',
        'timezone_name': 'America/New_York',
        'account_status': 1,
        'amount_spent': '1000.00',
        'balance': '5000.00'
    })
    account.create_campaign = Mock(return_value={'id': '123456789', 'name': 'Test Campaign'})
    account.create_ad_set = Mock(return_value={'id': '987654321', 'name': 'Test Ad Set'})
    account.get_campaigns = Mock(return_value=[])
    account.get_ad_sets = Mock(return_value=[])
    account.get_insights = Mock(return_value=[])
    return account


@pytest.fixture
def sample_targeting():
    """Sample targeting specification."""
    return {
        'geo_locations': {
            'countries': ['US']
        },
        'age_min': 25,
        'age_max': 65
    }


@pytest.fixture
def mock_pandas_dataframe():
    """Mock pandas DataFrame for CSV export tests."""
    import pandas as pd
    return pd.DataFrame({
        'campaign_id': ['123', '456'],
        'campaign_name': ['Campaign 1', 'Campaign 2'],
        'impressions': [1000, 2000],
        'clicks': [50, 100],
        'spend': [10.0, 20.0]
    })
