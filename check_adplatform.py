"""Check AdPlatform app configuration."""

import requests
from src.api_client import FacebookAdsClient

client = FacebookAdsClient()
access_token = client.config['facebook']['access_token']
app_id = "2648986878795029"  # AdPlatform

url = f"https://graph.facebook.com/v19.0/{app_id}"
params = {
    "access_token": access_token,
    "fields": "id,name,ios_bundle_id,android_key_hash,app_domains,namespace"
}

response = requests.get(url, params=params)
data = response.json()

print("AdPlatform App Configuration:")
print("=" * 50)
for key, value in data.items():
    print(f"{key}: {value}")

print("\n" + "=" * 50)
if 'ios_bundle_id' in data and data['ios_bundle_id']:
    print(f"✓ iOS Bundle ID: {data['ios_bundle_id']}")
else:
    print("✗ No iOS Bundle ID configured")

print("\nThe platforms are NOT configured yet.")
print("You need to add them at:")
print(f"https://developers.facebook.com/apps/{app_id}/settings/basic/")
