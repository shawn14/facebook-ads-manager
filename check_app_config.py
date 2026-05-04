"""Check what's configured in the Facebook app."""

import requests
from src.api_client import FacebookAdsClient

client = FacebookAdsClient()
access_token = client.config['facebook']['access_token']
app_id = "1190524789905900"

# Query the app details
url = f"https://graph.facebook.com/v19.0/{app_id}"
params = {
    "access_token": access_token,
    "fields": "id,name,namespace,ios_bundle_id,ios_sdk_error_categories,android_key_hash,app_domains,app_install_tracked,canvas_fluid_height,canvas_fluid_width,canvas_url"
}

response = requests.get(url, params=params)
data = response.json()

print("App Configuration:")
print("=" * 50)
for key, value in data.items():
    print(f"{key}: {value}")

print("\n" + "=" * 50)
print("\nLooking for iOS Bundle ID or Android Package...")

if 'ios_bundle_id' in data:
    print(f"✓ iOS Bundle ID: {data['ios_bundle_id']}")
else:
    print("✗ No iOS Bundle ID configured")

print("\nTo configure platforms for app install ads:")
print("You need to add platforms in Facebook App Dashboard")
print(f"https://developers.facebook.com/apps/{app_id}/settings/basic/")
