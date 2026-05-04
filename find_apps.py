"""Find Facebook app IDs for the Stock Alarm apps."""

from src.api_client import FacebookAdsClient
from facebook_business.api import FacebookAdsApi
import requests

client = FacebookAdsClient()

# Try to get apps from the business
business_id = "1495431848844691"  # From the URL you provided

print("Looking for apps in your business...")

# Use Graph API to get apps
api = FacebookAdsApi.get_default_api()
access_token = client.config['facebook']['access_token']

try:
    # Get apps from business
    url = f"https://graph.facebook.com/v19.0/{business_id}/client_apps"
    params = {
        "access_token": access_token,
        "fields": "id,name,namespace,app_installs_tracked_ios,app_installs_tracked_android"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'data' in data:
        print(f"\nFound {len(data['data'])} apps:")
        for app in data['data']:
            print(f"  - {app.get('name', 'N/A')}: {app.get('id')}")
    else:
        print(f"Response: {data}")

except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50)
print("App from your URL: 1190524789905900")
print("This might be the Stock Alarm app Facebook ID")
