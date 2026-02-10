"""Create ad creatives with images for the 3 test campaigns.

BEFORE RUNNING THIS SCRIPT:
1. Prepare 3 ad images (1080x1080px or 1200x628px)
2. Name them:
   - assets/ad1_never_miss.jpg (or .png)
   - assets/ad2_your_stocks.jpg (or .png)
   - assets/ad3_stop_guessing.jpg (or .png)
3. Set your app download link below (line 29)
"""

from src.api_client import FacebookAdsClient
from src.creative.manager import CreativeManager
from pathlib import Path
import sys

# Initialize
client = FacebookAdsClient()
manager = CreativeManager(client)

print("🎨 Creating Ad Creatives with Images for Stock Alarm...\n")

# ============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================================================

# Your app download link (App Store, Google Play, or landing page)
APP_DOWNLOAD_LINK = "https://stockalarm.app/download"  # ⬅️ CHANGE THIS!

# Image file paths (supports .jpg or .png)
IMAGE_FILES = {
    'campaign1': 'assets/ad1_never_miss.jpg',
    'campaign2': 'assets/ad2_your_stocks.jpg',
    'campaign3': 'assets/ad3_stop_guessing.jpg'
}

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================

# Check Page ID is configured
page_id = client.config['facebook'].get('page_id')
if not page_id or page_id == 'YOUR_PAGE_ID':
    print("❌ ERROR: Facebook Page ID not configured!")
    print("   Add your Page ID to config/config.yaml")
    sys.exit(1)

print(f"✓ Using Facebook Page ID: {page_id}")

# Check if images exist
missing_images = []
for campaign, image_path in IMAGE_FILES.items():
    # Check both .jpg and .png
    jpg_path = Path(image_path)
    png_path = Path(image_path.replace('.jpg', '.png'))

    if not jpg_path.exists() and not png_path.exists():
        missing_images.append(image_path)
    elif png_path.exists() and not jpg_path.exists():
        # Update to use .png if that's what exists
        IMAGE_FILES[campaign] = str(png_path)

if missing_images:
    print("\n❌ ERROR: Missing image files!")
    print("   Please create these images and save them as:")
    for img in missing_images:
        print(f"   - {img} (or .png)")
    print("\n   Image specs:")
    print("   - Size: 1080x1080px (square) or 1200x628px (landscape)")
    print("   - Format: JPG or PNG")
    print("   - Content: Show your app, keep text minimal")
    sys.exit(1)

print(f"✓ All 3 images found")

# Check app link
if APP_DOWNLOAD_LINK == "https://stockalarm.app/download":
    print("\n⚠️  WARNING: Using placeholder app link!")
    print("   Update APP_DOWNLOAD_LINK in this script (line 29)")
    response = input("   Continue anyway? (y/n): ")
    if response.lower() != 'y':
        sys.exit(0)

print(f"✓ App download link: {APP_DOWNLOAD_LINK}\n")

print("=" * 70)
print("Creating ad creatives...")
print("=" * 70)

# ============================================================================
# CREATE AD CREATIVES
# ============================================================================

try:
    # Creative 1: Never Miss a Stock Move
    print("\n📱 Campaign 1: 'Never Miss a Stock Move'")
    print(f"   Image: {IMAGE_FILES['campaign1']}")

    creative1 = manager.create_simple_ad(
        name="Never Miss a Stock Move - Creative",
        image_path=IMAGE_FILES['campaign1'],
        headline="Never Miss a Stock Move",
        description="Set it. Forget it. We'll notify you.",
        message="Get instant alerts when your stocks hit your target price.",
        link=APP_DOWNLOAD_LINK,
        call_to_action="DOWNLOAD"
    )
    print(f"   ✓ Creative created: {creative1['id']}")

    # Creative 2: Your Stocks, Your Alerts
    print("\n📱 Campaign 2: 'Your Stocks, Your Alerts'")
    print(f"   Image: {IMAGE_FILES['campaign2']}")

    creative2 = manager.create_simple_ad(
        name="Your Stocks, Your Alerts - Creative",
        image_path=IMAGE_FILES['campaign2'],
        headline="Your Stocks, Your Alerts",
        description="Stock alerts that work for you.",
        message="You choose the stocks. You set the price. We do the rest.",
        link=APP_DOWNLOAD_LINK,
        call_to_action="DOWNLOAD"
    )
    print(f"   ✓ Creative created: {creative2['id']}")

    # Creative 3: Stop Guessing, Start Knowing
    print("\n📱 Campaign 3: 'Stop Guessing, Start Knowing'")
    print(f"   Image: {IMAGE_FILES['campaign3']}")

    creative3 = manager.create_simple_ad(
        name="Stop Guessing, Start Knowing - Creative",
        image_path=IMAGE_FILES['campaign3'],
        headline="Stop Guessing, Start Knowing",
        description="Smart alerts for smarter trading.",
        message="Know exactly when to buy or sell with real-time price alerts.",
        link=APP_DOWNLOAD_LINK,
        call_to_action="LEARN_MORE"
    )
    print(f"   ✓ Creative created: {creative3['id']}")

    print("\n" + "=" * 70)
    print("✅ All 3 ad creatives created successfully!")
    print("=" * 70)

    print("\n📋 Creative IDs:")
    print(f"   1. Never Miss a Stock Move: {creative1['id']}")
    print(f"   2. Your Stocks, Your Alerts: {creative2['id']}")
    print(f"   3. Stop Guessing, Start Knowing: {creative3['id']}")

    print("\n🎯 NEXT STEPS:")
    print("   1. Create ad sets with targeting")
    print("   2. Link creatives to ad sets")
    print("   3. Set budgets and launch campaigns")
    print("\n   💡 Use the web dashboard to manage everything:")
    print("      http://localhost:8000")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("- Check that images are valid JPG or PNG files")
    print("- Verify Page ID is correct in config.yaml")
    print("- Make sure access token has ads_management permission")
    sys.exit(1)
