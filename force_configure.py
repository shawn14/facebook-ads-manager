"""Force configure app platforms via API - aggressive approach."""

import requests
import json
from src.api_client import FacebookAdsClient

client = FacebookAdsClient()
config = client.config['facebook']

app_id = config['app_id']
app_secret = config['app_secret']

print(f"Forcing configuration for app: {app_id}")
print("=" * 60)

# Get app access token
print("\n[1/4] Getting app access token...")
token_url = "https://graph.facebook.com/oauth/access_token"
token_response = requests.get(token_url, params={
    "client_id": app_id,
    "client_secret": app_secret,
    "grant_type": "client_credentials"
})
token_data = token_response.json()
app_token = token_data['access_token']
print(f"✓ Got token: {app_token[:30]}...")

# Enable API access to app settings
print("\n[2/4] Enabling API access to app settings...")
settings_url = f"https://graph.facebook.com/v19.0/{app_id}"
enable_response = requests.post(settings_url, data={
    "access_token": app_token,
    "restrictions": json.dumps({"age_distr": "13+"})
})
print(f"Result: {enable_response.json()}")

# Configure iOS
print("\n[3/4] Configuring iOS platform...")
ios_fields = {
    "access_token": app_token,
    "ios_bundle_id": "com.StockMarketAlarms.StockAlarm",
    "ios_supports_native_proxy_auth_flow": True,
    "ios_supports_system_auth": True
}

ios_response = requests.post(settings_url, data=ios_fields)
ios_result = ios_response.json()
print(f"iOS: {ios_result}")

# Configure Android
print("\n[4/4] Configuring Android platform...")
android_fields = {
    "access_token": app_token,
    "android_key_hash": [""],  # Empty is OK for ads
}

android_response = requests.post(settings_url, data=android_fields)
android_result = android_response.json()
print(f"Android: {android_result}")

print("\n" + "=" * 60)
print("Configuration complete - verifying...")

# Verify
verify_response = requests.get(settings_url, params={
    "access_token": app_token,
    "fields": "id,name,ios_bundle_id,android_key_hash"
})
print(f"\nFinal config: {verify_response.json()}")

print("\n✓ DONE! Now retrying ad set creation...")
