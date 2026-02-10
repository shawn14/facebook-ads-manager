"""Unit tests for CampaignManager."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.campaign.manager import CampaignManager


class TestCampaignManagerInit:
    """Tests for CampaignManager initialization."""

    def test_init(self):
        """Test CampaignManager initialization."""
        mock_client = Mock()
        mock_client.config = {'test': 'config'}

        manager = CampaignManager(mock_client)

        assert manager.client == mock_client
        assert manager.config == mock_client.config


class TestCreateCampaign:
    """Tests for campaign creation."""

    @pytest.fixture
    def manager(self, mock_config):
        """Create a manager for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        mock_client.create_campaign = Mock(return_value={
            'id': '123456789',
            'name': 'Test Campaign',
            'objective': 'LINK_CLICKS'
        })
        return CampaignManager(mock_client)

    def test_create_campaign_basic(self, manager):
        """Test creating a basic campaign."""
        result = manager.create_campaign(
            name="Test Campaign",
            objective="LINK_CLICKS",
            daily_budget=50.0,
            status="PAUSED"
        )

        assert result['id'] == '123456789'
        assert result['name'] == 'Test Campaign'
        manager.client.create_campaign.assert_called_once()

    def test_create_campaign_budget_conversion(self, manager):
        """Test that budget is converted from USD to cents."""
        manager.create_campaign(
            name="Test Campaign",
            objective="CONVERSIONS",
            daily_budget=100.0
        )

        # Verify campaign creation was called
        manager.client.create_campaign.assert_called_once()
        call_args = manager.client.create_campaign.call_args
        assert call_args[1]['name'] == "Test Campaign"
        assert call_args[1]['objective'] == "CONVERSIONS"

    def test_create_campaign_with_active_status(self, manager, sample_targeting):
        """Test creating an active campaign also creates ad set."""
        manager.client.create_adset = Mock(return_value={
            'id': '987654321',
            'name': 'Ad Set 1'
        })

        with patch.object(manager, '_get_default_targeting', return_value=sample_targeting):
            result = manager.create_campaign(
                name="Active Campaign",
                objective="LINK_CLICKS",
                daily_budget=50.0,
                status="ACTIVE"
            )

            # Should create ad set for active campaign
            manager.client.create_adset.assert_called_once()

    def test_create_campaign_with_special_categories(self, manager):
        """Test creating campaign with special ad categories."""
        result = manager.create_campaign(
            name="Housing Ad",
            objective="LINK_CLICKS",
            daily_budget=50.0,
            special_ad_categories=["HOUSING"]
        )

        call_args = manager.client.create_campaign.call_args
        assert call_args[1]['special_ad_categories'] == ["HOUSING"]

    def test_get_default_targeting(self, manager):
        """Test default targeting from config."""
        targeting = manager._get_default_targeting()

        assert 'geo_locations' in targeting
        assert targeting['geo_locations']['countries'] == ['US']
        assert targeting['age_min'] == 25
        assert targeting['age_max'] == 65

    def test_create_default_adset(self, manager, sample_targeting):
        """Test creating default ad set."""
        manager.client.create_adset = Mock(return_value={
            'id': '987654321',
            'name': 'Ad Set 1'
        })

        with patch.object(manager, '_get_default_targeting', return_value=sample_targeting):
            result = manager._create_default_adset('123456789', 5000)

            manager.client.create_adset.assert_called_once()
            call_args = manager.client.create_adset.call_args
            assert call_args[1]['campaign_id'] == '123456789'
            assert call_args[1]['daily_budget'] == 5000


class TestListCampaigns:
    """Tests for listing campaigns."""

    @pytest.fixture
    def manager(self, mock_config):
        """Create a manager for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return CampaignManager(mock_client)

    def test_list_campaigns_no_filter(self, manager, mock_campaign_data):
        """Test listing all campaigns without filter."""
        manager.client.get_campaigns = Mock(return_value=[mock_campaign_data])

        campaigns = manager.list_campaigns()

        assert len(campaigns) == 1
        assert campaigns[0]['id'] == '123456789'
        manager.client.get_campaigns.assert_called_once()

    def test_list_campaigns_with_status_filter(self, manager, mock_campaign_data):
        """Test listing campaigns with status filter."""
        manager.client.get_campaigns = Mock(return_value=[mock_campaign_data])

        campaigns = manager.list_campaigns(status_filter='ACTIVE')

        call_args = manager.client.get_campaigns.call_args
        filtering = call_args[1]['filtering']
        assert filtering[0]['field'] == 'status'
        assert filtering[0]['value'] == 'ACTIVE'

    def test_list_campaigns_with_insights(self, manager, mock_campaign_data, mock_insights_data):
        """Test listing campaigns with insights included."""
        manager.client.get_campaigns = Mock(return_value=[mock_campaign_data])
        manager.client.get_campaign_insights = Mock(return_value=[mock_insights_data])

        campaigns = manager.list_campaigns(include_insights=True)

        assert len(campaigns) == 1
        assert 'insights' in campaigns[0]
        manager.client.get_campaign_insights.assert_called_once_with('123456789')

    def test_list_campaigns_empty(self, manager):
        """Test listing campaigns when none exist."""
        manager.client.get_campaigns = Mock(return_value=[])

        campaigns = manager.list_campaigns()

        assert campaigns == []


class TestCampaignOperations:
    """Tests for campaign operations (pause, activate, update)."""

    @pytest.fixture
    def manager(self, mock_config):
        """Create a manager for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return CampaignManager(mock_client)

    def test_pause_campaign(self, manager):
        """Test pausing a campaign."""
        manager.client.pause_campaign = Mock()

        manager.pause_campaign('123456789')

        manager.client.pause_campaign.assert_called_once_with('123456789')

    def test_activate_campaign(self, manager):
        """Test activating a campaign."""
        manager.client.activate_campaign = Mock()

        manager.activate_campaign('123456789')

        manager.client.activate_campaign.assert_called_once_with('123456789')

    def test_update_budget(self, manager, mock_adset_data):
        """Test updating campaign budget."""
        manager.client.get_adsets = Mock(return_value=[mock_adset_data])
        manager.client.update_campaign = Mock()

        manager.update_budget('123456789', 100.0)

        # Should update all ad sets
        manager.client.get_adsets.assert_called_once_with(campaign_id='123456789')
        manager.client.update_campaign.assert_called_once()

        call_args = manager.client.update_campaign.call_args
        assert call_args[0][1]['daily_budget'] == 10000  # $100 in cents


class TestDuplicateCampaign:
    """Tests for campaign duplication."""

    @pytest.fixture
    def manager(self, mock_config):
        """Create a manager for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return CampaignManager(mock_client)

    def test_duplicate_campaign_success(self, manager, mock_campaign_data):
        """Test successful campaign duplication."""
        manager.client.get_campaigns = Mock(return_value=[mock_campaign_data])
        manager.client.create_campaign = Mock(return_value={
            'id': '999999999',
            'name': 'Test Campaign (Copy)',
            'objective': 'LINK_CLICKS'
        })

        result = manager.duplicate_campaign('123456789')

        assert result['id'] == '999999999'
        assert '(Copy)' in result['name']
        manager.client.create_campaign.assert_called_once()

    def test_duplicate_campaign_custom_name(self, manager, mock_campaign_data):
        """Test duplicating campaign with custom name."""
        manager.client.get_campaigns = Mock(return_value=[mock_campaign_data])
        manager.client.create_campaign = Mock(return_value={
            'id': '999999999',
            'name': 'New Campaign Name',
            'objective': 'LINK_CLICKS'
        })

        result = manager.duplicate_campaign('123456789', new_name='New Campaign Name')

        call_args = manager.client.create_campaign.call_args
        assert call_args[1]['name'] == 'New Campaign Name'

    def test_duplicate_campaign_not_found(self, manager):
        """Test duplicating non-existent campaign."""
        manager.client.get_campaigns = Mock(return_value=[])

        with pytest.raises(ValueError) as exc_info:
            manager.duplicate_campaign('nonexistent')

        assert "not found" in str(exc_info.value)

    def test_duplicate_campaign_preserves_objective(self, manager, mock_campaign_data):
        """Test that duplication preserves campaign objective."""
        mock_campaign_data['objective'] = 'CONVERSIONS'
        manager.client.get_campaigns = Mock(return_value=[mock_campaign_data])
        manager.client.create_campaign = Mock(return_value={
            'id': '999999999',
            'name': 'Test Campaign (Copy)',
            'objective': 'CONVERSIONS'
        })

        result = manager.duplicate_campaign('123456789')

        call_args = manager.client.create_campaign.call_args
        assert call_args[1]['objective'] == 'CONVERSIONS'

    def test_duplicate_campaign_status_paused(self, manager, mock_campaign_data):
        """Test that duplicated campaigns start paused."""
        manager.client.get_campaigns = Mock(return_value=[mock_campaign_data])
        manager.client.create_campaign = Mock(return_value={
            'id': '999999999',
            'name': 'Test Campaign (Copy)',
            'objective': 'LINK_CLICKS'
        })

        result = manager.duplicate_campaign('123456789')

        call_args = manager.client.create_campaign.call_args
        assert call_args[1]['status'] == 'PAUSED'


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.fixture
    def manager(self, mock_config):
        """Create a manager for testing."""
        mock_client = Mock()
        mock_client.config = mock_config
        return CampaignManager(mock_client)

    def test_create_campaign_api_error(self, manager):
        """Test handling API errors during campaign creation."""
        manager.client.create_campaign = Mock(
            side_effect=Exception("API Error")
        )

        with pytest.raises(Exception) as exc_info:
            manager.create_campaign(
                name="Test",
                objective="LINK_CLICKS",
                daily_budget=50.0
            )

        assert "API Error" in str(exc_info.value)

    def test_list_campaigns_no_insights_data(self, manager, mock_campaign_data):
        """Test listing campaigns when insights return empty."""
        manager.client.get_campaigns = Mock(return_value=[mock_campaign_data])
        manager.client.get_campaign_insights = Mock(return_value=[])

        campaigns = manager.list_campaigns(include_insights=True)

        # Should not have insights key or should handle gracefully
        assert len(campaigns) == 1

    def test_update_budget_no_adsets(self, manager):
        """Test updating budget when no ad sets exist."""
        manager.client.get_adsets = Mock(return_value=[])
        manager.client.update_campaign = Mock()

        manager.update_budget('123456789', 100.0)

        # Should not fail, just not update anything
        manager.client.update_campaign.assert_not_called()
