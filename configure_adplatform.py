"""Configure AdPlatform app for app installs."""

import requests
from src.api_client import FacebookAdsClient

client = FacebookAdsClient()
config = client.config['facebook']

# Use the AdPlatform app (the one in your config)
app_id = config['app_id']  # 2648986878795029
app_secret = config['app_secret']

print(f"Using AdPlatform app: {app_id}")
print("=" * 50)

print("\nStep 1: Getting app access token...")
token_url = "https://graph.facebook.com/oauth/access_token"
token_params = {
    "client_id": app_id,
    "client_secret": app_secret,
    "grant_type": "client_credentials"
}

token_response = requests.get(token_url, params=token_params)
token_data = token_response.json()

if 'access_token' not in token_data:
    print(f"Error: {token_data}")
    exit(1)

app_access_token = token_data['access_token']
print(f"✓ Got app access token")

print("\nStep 2: Configuring iOS Bundle ID...")
ios_url = f"https://graph.facebook.com/v19.0/{app_id}"
ios_data = {
    "access_token": app_access_token,
    "ios_bundle_id": "com.StockMarketAlarms.StockAlarm",
}

ios_response = requests.post(ios_url, data=ios_data)
ios_result = ios_response.json()
print(f"iOS: {ios_result}")

print("\nStep 3: Verifying...")
verify_url = f"https://graph.facebook.com/v19.0/{app_id}"
verify_params = {
    "access_token": app_access_token,
    "fields": "id,name,ios_bundle_id"
}

verify_response = requests.get(verify_url, params=verify_params)
verify_data = verify_response.json()

print("\nCurrent configuration:")
for key, value in verify_data.items():
    print(f"  {key}: {value}")

print("\n✓ AdPlatform app configured for app installs!")
