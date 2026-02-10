"""Unit tests for FacebookAdsClient."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.api_client import FacebookAdsClient


class TestFacebookAdsClientInit:
    """Tests for FacebookAdsClient initialization."""

    def test_init_with_config_file(self, mock_config_file, mock_facebook_ads_api, mock_account_object):
        """Test successful initialization with config file."""
        with patch('src.api_client.AdAccount', return_value=mock_account_object):
            client = FacebookAdsClient(config_path=mock_config_file)

            assert client.config is not None
            assert client.config['facebook']['app_id'] == 'test_app_id'
            mock_facebook_ads_api.init.assert_called_once()

    def test_init_missing_config_file(self):
        """Test initialization fails with missing config file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            FacebookAdsClient(config_path="nonexistent/config.yaml")

        assert "Config file not found" in str(exc_info.value)

    def test_api_initialization(self, mock_config_file, mock_facebook_ads_api, mock_account_object):
        """Test Facebook API is initialized with correct parameters."""
        with patch('src.api_client.AdAccount', return_value=mock_account_object):
            client = FacebookAdsClient(config_path=mock_config_file)

            mock_facebook_ads_api.init.assert_called_once_with(
                app_id='test_app_id',
                app_secret='test_app_secret',
                access_token='test_access_token',
                api_version='v19.0'
            )


class TestCampaignManagement:
    """Tests for campaign management methods."""

    @pytest.fixture
    def client(self, mock_config_file, mock_facebook_ads_api, mock_account_object):
        """Create a client for testing."""
        with patch('src.api_client.AdAccount', return_value=mock_account_object):
            return FacebookAdsClient(config_path=mock_config_file)

    def test_create_campaign_basic(self, client, mock_campaign_data):
        """Test creating a basic campaign."""
        client.ad_account.create_campaign = Mock(return_value=mock_campaign_data)

        result = client.create_campaign(
            name="Test Campaign",
            objective="LINK_CLICKS",
            status="PAUSED"
        )

        assert result['id'] == '123456789'
        assert result['name'] == 'Test Campaign'
        client.ad_account.create_campaign.assert_called_once()

    def test_create_campaign_with_special_categories(self, client, mock_campaign_data):
        """Test creating campaign with special ad categories."""
        client.ad_account.create_campaign = Mock(return_value=mock_campaign_data)

        result = client.create_campaign(
            name="Test Campaign",
            objective="CONVERSIONS",
            special_ad_categories=["EMPLOYMENT", "HOUSING"]
        )

        call_args = client.ad_account.create_campaign.call_args
        assert 'special_ad_categories' in call_args[1]['params']
        assert call_args[1]['params']['special_ad_categories'] == ["EMPLOYMENT", "HOUSING"]

    def test_get_campaigns(self, client, mock_campaign_data):
        """Test fetching campaigns."""
        client.ad_account.get_campaigns = Mock(return_value=[mock_campaign_data])

        campaigns = client.get_campaigns()

        assert len(campaigns) == 1
        assert campaigns[0]['id'] == '123456789'

    def test_get_campaigns_with_filtering(self, client, mock_campaign_data):
        """Test fetching campaigns with filters."""
        client.ad_account.get_campaigns = Mock(return_value=[mock_campaign_data])

        filtering = [{'field': 'status', 'operator': 'EQUAL', 'value': 'ACTIVE'}]
        campaigns = client.get_campaigns(filtering=filtering)

        call_args = client.ad_account.get_campaigns.call_args
        assert 'filtering' in call_args[1]['params']

    def test_update_campaign(self, client):
        """Test updating a campaign."""
        mock_campaign = Mock()
        mock_campaign.api_update = Mock()

        with patch('src.api_client.Campaign', return_value=mock_campaign):
            result = client.update_campaign('123456789', {'status': 'PAUSED'})

            mock_campaign.api_update.assert_called_once_with(
                params={'status': 'PAUSED'}
            )

    def test_pause_campaign(self, client):
        """Test pausing a campaign."""
        mock_campaign = Mock()
        mock_campaign.api_update = Mock()

        with patch('src.api_client.Campaign', return_value=mock_campaign):
            client.pause_campaign('123456789')

            mock_campaign.api_update.assert_called_once_with(
                params={'status': 'PAUSED'}
            )

    def test_activate_campaign(self, client):
        """Test activating a campaign."""
        mock_campaign = Mock()
        mock_campaign.api_update = Mock()

        with patch('src.api_client.Campaign', return_value=mock_campaign):
            client.activate_campaign('123456789')

            mock_campaign.api_update.assert_called_once_with(
                params={'status': 'ACTIVE'}
            )

    def test_delete_campaign(self, client):
        """Test deleting a campaign."""
        mock_campaign = Mock()
        mock_campaign.api_delete = Mock()

        with patch('src.api_client.Campaign', return_value=mock_campaign):
            client.delete_campaign('123456789')

            mock_campaign.api_delete.assert_called_once()


class TestAdSetManagement:
    """Tests for ad set management methods."""

    @pytest.fixture
    def client(self, mock_config_file, mock_facebook_ads_api, mock_account_object):
        """Create a client for testing."""
        with patch('src.api_client.AdAccount', return_value=mock_account_object):
            return FacebookAdsClient(config_path=mock_config_file)

    def test_create_adset(self, client, mock_adset_data, sample_targeting):
        """Test creating an ad set."""
        client.ad_account.create_ad_set = Mock(return_value=mock_adset_data)

        result = client.create_adset(
            campaign_id='123456789',
            name='Test Ad Set',
            daily_budget=5000,
            targeting=sample_targeting
        )

        assert result['id'] == '987654321'
        client.ad_account.create_ad_set.assert_called_once()

    def test_create_adset_with_custom_params(self, client, mock_adset_data, sample_targeting):
        """Test creating ad set with custom parameters."""
        client.ad_account.create_ad_set = Mock(return_value=mock_adset_data)

        result = client.create_adset(
            campaign_id='123456789',
            name='Test Ad Set',
            daily_budget=10000,
            targeting=sample_targeting,
            optimization_goal='CONVERSIONS',
            billing_event='IMPRESSIONS',
            bid_strategy='LOWEST_COST_WITH_BID_CAP'
        )

        call_args = client.ad_account.create_ad_set.call_args
        params = call_args[1]['params']
        assert params['optimization_goal'] == 'CONVERSIONS'
        assert params['bid_strategy'] == 'LOWEST_COST_WITH_BID_CAP'

    def test_get_adsets_all(self, client, mock_adset_data):
        """Test fetching all ad sets."""
        client.ad_account.get_ad_sets = Mock(return_value=[mock_adset_data])

        adsets = client.get_adsets()

        assert len(adsets) == 1
        assert adsets[0]['id'] == '987654321'

    def test_get_adsets_by_campaign(self, client, mock_adset_data):
        """Test fetching ad sets for a specific campaign."""
        mock_campaign = Mock()
        mock_campaign.get_ad_sets = Mock(return_value=[mock_adset_data])

        with patch('src.api_client.Campaign', return_value=mock_campaign):
            adsets = client.get_adsets(campaign_id='123456789')

            assert len(adsets) == 1
            mock_campaign.get_ad_sets.assert_called_once()


class TestInsightsAndAnalytics:
    """Tests for insights and analytics methods."""

    @pytest.fixture
    def client(self, mock_config_file, mock_facebook_ads_api, mock_account_object):
        """Create a client for testing."""
        with patch('src.api_client.AdAccount', return_value=mock_account_object):
            return FacebookAdsClient(config_path=mock_config_file)

    def test_get_campaign_insights(self, client, mock_insights_data):
        """Test fetching campaign insights."""
        mock_campaign = Mock()
        mock_campaign.get_insights = Mock(return_value=[mock_insights_data])

        with patch('src.api_client.Campaign', return_value=mock_campaign):
            insights = client.get_campaign_insights('123456789')

            assert len(insights) == 1
            assert insights[0]['campaign_id'] == '123456789'
            mock_campaign.get_insights.assert_called_once()

    def test_get_campaign_insights_custom_date_range(self, client, mock_insights_data):
        """Test fetching insights with custom date range."""
        mock_campaign = Mock()
        mock_campaign.get_insights = Mock(return_value=[mock_insights_data])

        with patch('src.api_client.Campaign', return_value=mock_campaign):
            insights = client.get_campaign_insights('123456789', date_preset='last_30d')

            call_args = mock_campaign.get_insights.call_args
            assert call_args[1]['params']['date_preset'] == 'last_30d'

    def test_get_campaign_insights_custom_fields(self, client, mock_insights_data):
        """Test fetching insights with custom fields."""
        mock_campaign = Mock()
        mock_campaign.get_insights = Mock(return_value=[mock_insights_data])

        custom_fields = ['impressions', 'clicks', 'spend']

        with patch('src.api_client.Campaign', return_value=mock_campaign):
            insights = client.get_campaign_insights(
                '123456789',
                fields=custom_fields
            )

            call_args = mock_campaign.get_insights.call_args
            assert call_args[1]['fields'] == custom_fields

    def test_get_account_insights(self, client, mock_insights_data):
        """Test fetching account-level insights."""
        client.ad_account.get_insights = Mock(return_value=[mock_insights_data])

        insights = client.get_account_insights()

        assert len(insights) == 1
        client.ad_account.get_insights.assert_called_once()

    def test_get_account_insights_by_level(self, client, mock_insights_data):
        """Test fetching account insights with different aggregation levels."""
        client.ad_account.get_insights = Mock(return_value=[mock_insights_data])

        insights = client.get_account_insights(level='adset')

        call_args = client.ad_account.get_insights.call_args
        assert call_args[1]['params']['level'] == 'adset'


class TestUtilityMethods:
    """Tests for utility methods."""

    @pytest.fixture
    def client(self, mock_config_file, mock_facebook_ads_api, mock_account_object):
        """Create a client for testing."""
        with patch('src.api_client.AdAccount', return_value=mock_account_object):
            return FacebookAdsClient(config_path=mock_config_file)

    def test_get_account_info(self, client):
        """Test fetching account information."""
        account_data = {
            'id': 'act_123456789',
            'name': 'Test Account',
            'currency': 'USD',
            'timezone_name': 'America/New_York',
            'account_status': 1,
            'amount_spent': '1000.00',
            'balance': '5000.00'
        }

        client.ad_account.api_get = Mock(return_value=account_data)

        info = client.get_account_info()

        assert info['name'] == 'Test Account'
        assert info['currency'] == 'USD'
        client.ad_account.api_get.assert_called_once()

    def test_validate_credentials_success(self, client):
        """Test successful credential validation."""
        client.ad_account.api_get = Mock(return_value={
            'id': 'act_123456789',
            'name': 'Test Account'
        })

        result = client.validate_credentials()

        assert result is True

    def test_validate_credentials_failure(self, client):
        """Test failed credential validation."""
        client.ad_account.api_get = Mock(side_effect=Exception("Invalid credentials"))

        result = client.validate_credentials()

        assert result is False


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.fixture
    def client(self, mock_config_file, mock_facebook_ads_api, mock_account_object):
        """Create a client for testing."""
        with patch('src.api_client.AdAccount', return_value=mock_account_object):
            return FacebookAdsClient(config_path=mock_config_file)

    def test_get_campaigns_empty_result(self, client):
        """Test handling empty campaign results."""
        client.ad_account.get_campaigns = Mock(return_value=[])

        campaigns = client.get_campaigns()

        assert campaigns == []

    def test_get_insights_no_data(self, client):
        """Test handling no insights data."""
        mock_campaign = Mock()
        mock_campaign.get_insights = Mock(return_value=[])

        with patch('src.api_client.Campaign', return_value=mock_campaign):
            insights = client.get_campaign_insights('123456789')

            assert insights == []

    def test_create_campaign_api_error(self, client):
        """Test handling API errors during campaign creation."""
        client.ad_account.create_campaign = Mock(
            side_effect=Exception("API Error: Invalid parameters")
        )

        with pytest.raises(Exception) as exc_info:
            client.create_campaign(
                name="Test",
                objective="INVALID_OBJECTIVE"
            )

        assert "API Error" in str(exc_info.value)
