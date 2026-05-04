"""Setup Stock Alarm app install campaigns with proper app linking."""

from src.api_client import FacebookAdsClient
from loguru import logger

# Initialize client
client = FacebookAdsClient()

# Campaign IDs (these were already created)
ios_campaign_id = "52511032656434"
android_campaign_id = "52511032830434"

# Use AdPlatform app (from config)
app_id = client.config['facebook']['app_id']  # 2648986878795029

# App details
ios_app_store_url = "https://apps.apple.com/us/app/stock-alarm-alerts-tracker/id1465535138"
android_app_store_url = "https://play.google.com/store/apps/details?id=com.StockMarketAlarms.StockAlarm"

# Basic targeting for stock traders (mobile only)
mobile_targeting = {
    "geo_locations": {"countries": ["US"]},
    "age_min": 25,
    "age_max": 65,
    "interests": [
        {"id": "6003139266461", "name": "Stock market"},  # Stock market interest
        {"id": "6003020834693", "name": "Investing"},      # Investing interest
    ],
    "user_os": []  # Will be set per platform
}

print("Creating iOS Ad Set...")
try:
    ios_targeting = mobile_targeting.copy()
    ios_targeting["user_os"] = ["iOS"]

    ios_promoted_object = {
        "application_id": app_id,
        "object_store_url": ios_app_store_url
    }

    ios_adset = client.create_adset(
        campaign_id=ios_campaign_id,
        name="Stock Alarm iOS - US - Stock Traders",
        daily_budget=3000,  # $30 in cents
        targeting=ios_targeting,
        optimization_goal="APP_INSTALLS",
        billing_event="IMPRESSIONS",
        status="PAUSED",
        promoted_object=ios_promoted_object
    )

    print(f"✓ iOS Ad Set Created: {ios_adset['id']}")

except Exception as e:
    print(f"✗ iOS Ad Set Error: {e}")
    logger.error(f"iOS ad set creation failed: {e}")

print("\nCreating Android Ad Set...")
try:
    android_targeting = mobile_targeting.copy()
    android_targeting["user_os"] = ["Android"]

    android_promoted_object = {
        "application_id": app_id,
        "object_store_url": android_app_store_url
    }

    android_adset = client.create_adset(
        campaign_id=android_campaign_id,
        name="Stock Alarm Android - US - Stock Traders",
        daily_budget=3000,  # $30 in cents
        targeting=android_targeting,
        optimization_goal="APP_INSTALLS",
        billing_event="IMPRESSIONS",
        status="PAUSED",
        promoted_object=android_promoted_object
    )

    print(f"✓ Android Ad Set Created: {android_adset['id']}")

except Exception as e:
    print(f"✗ Android Ad Set Error: {e}")
    logger.error(f"Android ad set creation failed: {e}")

print("\nDone! Check the output above for any errors.")
print("\nNext step: Create ads with app preview creatives for each ad set.")
