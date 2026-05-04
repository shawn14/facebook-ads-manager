"""Create AI-generated ads for Stock Alarm app install campaigns."""

from src.api_client import FacebookAdsClient
from src.creative.ai_ad_generator import AIAdGenerator
from src.creative.image_generator import create_image_generator_from_config
import time

client = FacebookAdsClient()
ai_generator = AIAdGenerator(client)

# Ad sets we created
ios_adset_id = "52511692646434"
android_adset_id = "52511692656234"

# Ad concepts for Stock Alarm
ad_concepts = [
    {
        "name": "Never Miss a Breakout",
        "image_prompt": "Professional mobile app interface showing real-time stock price alerts and notifications, modern fintech design, clean UI with green upward arrows and price charts, iPhone mockup, premium look",
        "headline": "Never Miss a Breakout",
        "primary_text": "Get instant alerts when your stocks hit your target prices. Stock Alarm sends real-time notifications so you never miss a move. Join 100,000+ traders staying ahead of the market.",
        "description": "Real-time stock alerts",
        "cta": "INSTALL_MOBILE_APP"
    },
    {
        "name": "Track Any Stock",
        "image_prompt": "Sleek stock trading app showing a watchlist of popular stocks like AAPL, TSLA, NVDA with price alerts, dark mode UI, professional fintech app design, mobile phone mockup",
        "headline": "Track Any Stock, Anytime",
        "primary_text": "Set custom price alerts for stocks, crypto, and forex. Get notified the moment your targets hit. Free app with unlimited alerts.",
        "description": "Custom price alerts",
        "cta": "INSTALL_MOBILE_APP"
    },
    {
        "name": "Beat the Market",
        "image_prompt": "Modern stock market app with push notifications showing price alerts, charts going up, professional trader using phone, success theme, fintech app UI",
        "headline": "Beat the Market With Alerts",
        "primary_text": "Top traders use alerts to time their entries perfectly. Stock Alarm gives you the edge with instant notifications when stocks reach your targets. Install free now.",
        "description": "Professional stock alerts",
        "cta": "INSTALL_MOBILE_APP"
    }
]

print("🎨 Generating AI-powered Stock Alarm ads...")
print("=" * 60)

created_ads = []

for i, concept in enumerate(ad_concepts, 1):
    print(f"\n[{i}/3] Creating: {concept['name']}")
    print("-" * 60)

    try:
        # Generate image using AI
        print(f"  🎨 Generating image: {concept['image_prompt'][:50]}...")
        image_gen = create_image_generator_from_config(client.config)

        image_bytes = image_gen.generate_ad_image(
            prompt=concept['image_prompt'],
            product_name="Stock Alarm",
            style="professional",
            size="1024x1024"
        )

        if not image_bytes:
            raise Exception("Failed to generate image")

        # Save image to file
        import os
        os.makedirs("generated_images", exist_ok=True)
        image_path = f"generated_images/stock_alarm_{concept['name'].lower().replace(' ', '_')}.png"

        with open(image_path, 'wb') as f:
            f.write(image_bytes)

        print(f"  ✓ Image generated: {image_path}")

        # Upload image to Facebook
        print(f"  📤 Uploading to Facebook...")
        image = client.upload_image(image_path=image_path)
        image_hash = image['hash']
        print(f"  ✓ Uploaded: {image_hash}")

        # Create ad creative for iOS
        print(f"  📱 Creating iOS ad creative...")
        ios_creative = client.create_image_creative(
            name=f"{concept['name']} - iOS",
            image_hash=image_hash,
            message=concept['primary_text'],
            link="https://apps.apple.com/us/app/stock-alarm-alerts-tracker/id1465535138",
            call_to_action_type=concept['cta']
        )

        # Create iOS ad
        ios_ad = client.create_ad(
            name=f"{concept['name']} - iOS",
            adset_id=ios_adset_id,
            creative_id=ios_creative['id'],
            status="PAUSED"
        )
        print(f"  ✓ iOS ad created: {ios_ad['id']}")

        # Create ad creative for Android
        print(f"  🤖 Creating Android ad creative...")
        android_creative = client.create_image_creative(
            name=f"{concept['name']} - Android",
            image_hash=image_hash,
            message=concept['primary_text'],
            link="https://play.google.com/store/apps/details?id=com.StockMarketAlarms.StockAlarm",
            call_to_action_type=concept['cta']
        )

        # Create Android ad
        android_ad = client.create_ad(
            name=f"{concept['name']} - Android",
            adset_id=android_adset_id,
            creative_id=android_creative['id'],
            status="PAUSED"
        )
        print(f"  ✓ Android ad created: {android_ad['id']}")

        created_ads.append({
            "concept": concept['name'],
            "ios_ad_id": ios_ad['id'],
            "android_ad_id": android_ad['id']
        })

        print(f"  ✅ {concept['name']} complete!")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print(f"✅ Created {len(created_ads)} ad pairs (iOS + Android)")
print("\nSummary:")
for ad in created_ads:
    print(f"  • {ad['concept']}")
    print(f"    iOS: {ad['ios_ad_id']}")
    print(f"    Android: {ad['android_ad_id']}")

print("\n🎉 All ads created! Check them at:")
print("http://localhost:8000/ads")
