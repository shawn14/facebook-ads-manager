"""Try to configure iOS and Android platforms via API."""

import requests
from src.api_client import FacebookAdsClient

client = FacebookAdsClient()
access_token = client.config['facebook']['access_token']
app_id = "1190524789905900"

print("Attempting to configure app platforms via API...")
print("=" * 50)

# Try to update the app with iOS settings
print("\n1. Configuring iOS platform...")
ios_url = f"https://graph.facebook.com/v19.0/{app_id}"
ios_data = {
    "access_token": access_token,
    "ios_bundle_id": "com.StockMarketAlarms.StockAlarm",  # iOS bundle ID
    "ios_sf_app_links": [{
        "url": "https://apps.apple.com/us/app/stock-alarm-alerts-tracker/id1465535138",
        "app_store_id": "1465535138"
    }]
}

try:
    response = requests.post(ios_url, data=ios_data)
    result = response.json()
    if 'success' in result and result['success']:
        print("✓ iOS platform configured successfully")
    else:
        print(f"iOS result: {result}")
except Exception as e:
    print(f"iOS error: {e}")

# Try to update with Android settings
print("\n2. Configuring Android platform...")
android_url = f"https://graph.facebook.com/v19.0/{app_id}"
android_data = {
    "access_token": access_token,
    "android_key_hash": "",  # Not required for ads
    "app_domains": ["stockalarm.io"],
    "gdpv4_nux_enabled": False
}

try:
    response = requests.post(android_url, data=android_data)
    result = response.json()
    if 'success' in result and result['success']:
        print("✓ Android platform configured")
    else:
        print(f"Android result: {result}")
except Exception as e:
    print(f"Android error: {e}")

print("\n" + "=" * 50)
print("\nNote: This may require app-level admin permissions")
print("If this fails, the platforms must be added manually in the UI")
