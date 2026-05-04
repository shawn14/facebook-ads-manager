"""Configure app platforms using app access token."""

import requests
from src.api_client import FacebookAdsClient

client = FacebookAdsClient()
config = client.config['facebook']

app_id = "1190524789905900"
app_secret = config['app_secret']

print("Step 1: Getting app access token...")
print("=" * 50)

# Generate app access token
token_url = "https://graph.facebook.com/oauth/access_token"
token_params = {
    "client_id": app_id,
    "client_secret": app_secret,
    "grant_type": "client_credentials"
}

token_response = requests.get(token_url, params=token_params)
token_data = token_response.json()

if 'access_token' not in token_data:
    print(f"Error getting app token: {token_data}")
    exit(1)

app_access_token = token_data['access_token']
print(f"✓ Got app access token: {app_access_token[:20]}...")

print("\nStep 2: Configuring iOS platform...")
print("=" * 50)

# Configure iOS
ios_url = f"https://graph.facebook.com/v19.0/{app_id}"
ios_data = {
    "access_token": app_access_token,
    "ios_bundle_id": "com.StockMarketAlarms.StockAlarm",
}

ios_response = requests.post(ios_url, data=ios_data)
ios_result = ios_response.json()
print(f"iOS Response: {ios_result}")

if 'success' in ios_result:
    print("✓ iOS platform configured!")

print("\nStep 3: Verifying configuration...")
print("=" * 50)

# Check what's configured now
verify_url = f"https://graph.facebook.com/v19.0/{app_id}"
verify_params = {
    "access_token": app_access_token,
    "fields": "id,name,ios_bundle_id,android_key_hash,app_domains"
}

verify_response = requests.get(verify_url, params=verify_params)
verify_data = verify_response.json()

print("Current app configuration:")
for key, value in verify_data.items():
    print(f"  {key}: {value}")

print("\n" + "=" * 50)
print("✓ App configuration complete!")
