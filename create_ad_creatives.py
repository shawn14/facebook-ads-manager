"""Create ad creatives for the 3 test campaigns following Saucy Writing Rules.

This script shows you how to create ad creatives. You'll need:
1. Image assets (1080x1080px or 1200x628px)
2. A Facebook Page ID (required by Facebook)

For now, this demonstrates the structure. Replace with your actual images.
"""

from src.api_client import FacebookAdsClient
from src.creative.manager import CreativeManager

# Initialize
client = FacebookAdsClient()
manager = CreativeManager(client)

print("🎨 Creating Ad Creatives for Stock Alarm Campaigns...\n")

# Check if Page ID is configured
page_id = client.config['facebook'].get('page_id')
if not page_id or page_id == 'YOUR_PAGE_ID':
    print("⚠️  WARNING: You need to set your Facebook Page ID in config/config.yaml")
    print("   Get it from: https://www.facebook.com/[your-page]/about")
    print("   Or create a new page at: https://www.facebook.com/pages/create")
    print("\nSkipping creative creation for now.\n")
    print("=" * 70)
    print("SAMPLE AD COPY (following Saucy Writing Rules)")
    print("=" * 70)
else:
    print(f"✓ Using Facebook Page ID: {page_id}\n")

# Campaign 1: Never Miss a Stock Move
print("\n📱 Campaign 1: 'Never Miss a Stock Move'")
print("   Objective: Drive traffic to app")
print("   Strategy: Direct value, simple message")
print()
print("   AD COPY:")
print("   Headline: Never Miss a Stock Move")
print("   Primary Text: Get instant alerts when your stocks hit your target price.")
print("   Description: Set it. Forget it. We'll notify you.")
print("   CTA: Download Now")
print()

# Campaign 2: Your Stocks, Your Alerts
print("📱 Campaign 2: 'Your Stocks, Your Alerts'")
print("   Objective: App promotion")
print("   Strategy: Direct address, emphasize control")
print()
print("   AD COPY:")
print("   Headline: Your Stocks, Your Alerts")
print("   Primary Text: You choose the stocks. You set the price. We do the rest.")
print("   Description: Stock alerts that work for you.")
print("   CTA: Get Started")
print()

# Campaign 3: Stop Guessing, Start Knowing
print("📱 Campaign 3: 'Stop Guessing, Start Knowing'")
print("   Objective: Drive traffic")
print("   Strategy: Problem → Solution, action-oriented")
print()
print("   AD COPY:")
print("   Headline: Stop Guessing, Start Knowing")
print("   Primary Text: Know exactly when to buy or sell with real-time price alerts.")
print("   Description: Smart alerts for smarter trading.")
print("   CTA: Learn More")
print()

print("=" * 70)
print("NEXT STEPS:")
print("=" * 70)
print()
print("1. Get your Facebook Page ID:")
print("   • Go to your Facebook Page")
print("   • Click 'About' → Page Info")
print("   • Copy the Page ID")
print("   • Add it to config/config.yaml under facebook.page_id")
print()
print("2. Prepare your ad images:")
print("   • Size: 1080x1080px (square) or 1200x628px (landscape)")
print("   • Format: JPG or PNG")
print("   • Show your app in action")
print("   • Keep text minimal (Facebook limits text in images)")
print()
print("3. Create the creatives:")
print("   • Uncomment the code below and update image paths")
print("   • Run this script again")
print()
print("=" * 70)

# UNCOMMENT THIS SECTION AFTER YOU:
# 1. Add your Page ID to config.yaml
# 2. Prepare 3 ad images and save them in an 'assets/' folder

"""
# Example: Creating actual creatives (uncomment when ready)

if page_id and page_id != 'YOUR_PAGE_ID':
    print("\n🎨 Creating actual creatives...\n")

    # Creative 1: Never Miss a Stock Move
    creative1 = manager.create_simple_ad(
        name="Never Miss a Stock Move - Creative",
        image_path="assets/ad1_never_miss.jpg",  # YOUR IMAGE HERE
        headline="Never Miss a Stock Move",
        description="Set it. Forget it. We'll notify you.",
        message="Get instant alerts when your stocks hit your target price.",
        link="https://yourapplink.com/download",  # YOUR APP LINK
        call_to_action="DOWNLOAD"
    )
    print(f"✓ Creative 1 created: {creative1['id']}")

    # Creative 2: Your Stocks, Your Alerts
    creative2 = manager.create_simple_ad(
        name="Your Stocks, Your Alerts - Creative",
        image_path="assets/ad2_your_stocks.jpg",  # YOUR IMAGE HERE
        headline="Your Stocks, Your Alerts",
        description="Stock alerts that work for you.",
        message="You choose the stocks. You set the price. We do the rest.",
        link="https://yourapplink.com/download",  # YOUR APP LINK
        call_to_action="DOWNLOAD"
    )
    print(f"✓ Creative 2 created: {creative2['id']}")

    # Creative 3: Stop Guessing, Start Knowing
    creative3 = manager.create_simple_ad(
        name="Stop Guessing, Start Knowing - Creative",
        image_path="assets/ad3_stop_guessing.jpg",  # YOUR IMAGE HERE
        headline="Stop Guessing, Start Knowing",
        description="Smart alerts for smarter trading.",
        message="Know exactly when to buy or sell with real-time price alerts.",
        link="https://yourapplink.com/download",  # YOUR APP LINK
        call_to_action="LEARN_MORE"
    )
    print(f"✓ Creative 3 created: {creative3['id']}")

    print("\n✅ All 3 creatives created!")
    print("\nNext: Create ad sets and link them to campaigns")
"""

print("\n💡 TIP: Use the web dashboard to manage your campaigns:")
print("   http://localhost:8000")
