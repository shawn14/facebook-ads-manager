"""Create 3 test campaigns in sandbox following Saucy Writing Rules."""

from src.api_client import FacebookAdsClient
from src.campaign.manager import CampaignManager

# Initialize
client = FacebookAdsClient()
manager = CampaignManager(client)

print("🚀 Creating 3 Test Campaigns for Stock Alarm...\n")

# Campaign 1: Never Miss a Stock Move
# Strategy: Direct value proposition, simple message
print("Creating Campaign 1: 'Never Miss a Stock Move'")
campaign1_name = "Never Miss a Stock Move"
campaign1 = client.create_campaign(
    name=campaign1_name,
    objective="OUTCOME_TRAFFIC",  # Drive traffic to app download
    status="PAUSED",  # Start paused so we can review
    special_ad_categories=[]  # Not a special ad category
)
print(f"✓ Campaign 1 created: {campaign1_name} (ID: {campaign1['id']})\n")

# Campaign 2: Your Stocks, Your Alerts
# Strategy: Speak directly to the user, emphasize control
print("Creating Campaign 2: 'Your Stocks, Your Alerts'")
campaign2_name = "Your Stocks, Your Alerts"
campaign2 = client.create_campaign(
    name=campaign2_name,
    objective="OUTCOME_APP_PROMOTION",  # Track app installs
    status="PAUSED",
    special_ad_categories=[]
)
print(f"✓ Campaign 2 created: {campaign2_name} (ID: {campaign2['id']})\n")

# Campaign 3: Stop Guessing, Start Knowing
# Strategy: Problem → Solution, action-oriented
print("Creating Campaign 3: 'Stop Guessing, Start Knowing'")
campaign3_name = "Stop Guessing, Start Knowing"
campaign3 = client.create_campaign(
    name=campaign3_name,
    objective="OUTCOME_TRAFFIC",
    status="PAUSED",
    special_ad_categories=[]
)
print(f"✓ Campaign 3 created: {campaign3_name} (ID: {campaign3['id']})\n")

print("=" * 60)
print("✅ All 3 campaigns created successfully!")
print("=" * 60)
print("\nNext steps:")
print("1. View campaigns: python -m src.cli campaign list")
print("2. Start web dashboard: python run_web.py")
print("3. Create ad creatives for each campaign")
print("\nCampaign IDs:")
print(f"  1. {campaign1_name}: {campaign1['id']}")
print(f"  2. {campaign2_name}: {campaign2['id']}")
print(f"  3. {campaign3_name}: {campaign3['id']}")
