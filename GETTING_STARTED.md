# Getting Started - Run Your First Facebook Ad Campaign

## Step 1: Get Facebook API Credentials

### 1.1 Access Your Facebook App
Go to: https://developers.facebook.com/apps/2648986878795029/marketing-api/tools/

### 1.2 Get Required Credentials

You need 4 things:

**App ID:**
- Found on the app dashboard (top of page)
- Example: `2648986878795029`

**App Secret:**
- Settings → Basic → App Secret
- Click "Show" to reveal it
- Keep this SECRET - never commit to git

**Access Token:**
- Marketing API → Tools
- Click "Get Token"
- Select your ad account
- Copy the long token (starts with `EAAG...`)
- **Important:** Tokens expire! Get a long-lived token:
  - Use the Token Debugger tool
  - Extend the token to 60 days

**Ad Account ID:**
- Go to Facebook Ads Manager: https://business.facebook.com/adsmanager
- Look at the URL, you'll see `act=XXXXXXXXXX`
- Your ad account ID is: `act_XXXXXXXXXX` (include the "act_" prefix)

**Page ID (for creating ads):**
- Go to your Facebook Page
- Settings → Page Info
- Copy the Page ID
- Or visit: https://www.facebook.com/[your-page-name]/about

---

## Step 2: Configure the Tool

```bash
cd ~/projects/facebook-ads-manager

# Create virtual environment (if not already done)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy config template
cp config/config.example.yaml config/config.yaml

# Edit config (use your favorite editor)
nano config/config.yaml
# or
code config/config.yaml
```

**Edit `config/config.yaml` with your credentials:**

```yaml
facebook:
  app_id: "2648986878795029"
  app_secret: "YOUR_APP_SECRET_HERE"
  access_token: "EAAG...YOUR_LONG_TOKEN_HERE"
  ad_account_id: "act_XXXXXXXXXX"
  page_id: "YOUR_PAGE_ID_HERE"
  api_version: "v19.0"

campaigns:
  default_objective: "LINK_CLICKS"
  default_daily_budget: 50

targeting:
  default_countries: ["US"]
  default_age_min: 25
  default_age_max: 65

optimization:
  min_roas: 1.5
  min_ctr: 0.5
  max_cpa: 50
```

**Validate your credentials:**

```bash
python -m src.cli validate
```

You should see: ✓ Credentials validated successfully

---

## Step 3: Create Your First Campaign

### Option A: Using the Web Dashboard (Easiest)

```bash
# Start the web dashboard
python run_web.py
```

Visit http://localhost:8000

1. Click **"Campaigns"** in the nav
2. Click **"Create Campaign"** button
3. Fill in:
   - Name: "Test Campaign - [Your Product]"
   - Objective: LINK_CLICKS (or CONVERSIONS)
   - Daily Budget: $50 (start small)
   - Status: PAUSED (launch after setup)
4. Click **"Create"**

### Option B: Using the CLI

```bash
python -m src.cli campaign create \
  --name "Test Campaign - Q1 2026" \
  --objective LINK_CLICKS \
  --budget 50 \
  --status PAUSED
```

**Campaign Objectives Explained:**
- `LINK_CLICKS` - Drive traffic to your website
- `CONVERSIONS` - Track purchases/signups (requires Facebook Pixel)
- `REACH` - Maximize people who see your ad
- `BRAND_AWARENESS` - Increase brand recall
- `LEAD_GENERATION` - Collect leads within Facebook

---

## Step 4: Set Up Targeting

### Using Python API:

```python
from src.api_client import FacebookAdsClient
from src.targeting.builder import TargetingBuilder
from src.targeting.presets import TargetingPresets

# Initialize
client = FacebookAdsClient()

# Option 1: Use a preset
targeting = TargetingPresets.ecommerce_shoppers()

# Option 2: Build custom targeting
targeting = (TargetingBuilder()
    .add_location(countries=["US"])
    .add_age_range(25, 55)
    .add_gender("all")  # "male", "female", or "all"
    .add_interests([
        "Online shopping",
        "E-commerce",
        "Shopping"
    ])
    .build()
)

print(targeting)
```

**Available Presets:**
- `ecommerce_shoppers()` - Online shoppers
- `tech_enthusiasts()` - Tech/gadget lovers
- `fitness_enthusiasts()` - Health/fitness audience
- `business_professionals()` - B2B audience
- `parents_with_kids()` - Parents
- `travelers()` - Travel enthusiasts
- `luxury_shoppers()` - High-income shoppers
- `mobile_first()` - Mobile-only users
- `local_business()` - Local area targeting

See `src/targeting/presets.py` for all 14 presets.

---

## Step 5: Create Ad Creative

### 5.1 Prepare Your Creative Assets

You need:
- **Image:** 1080x1080px (square) or 1200x628px (landscape)
- **Ad Copy:** Headline (max 40 chars) + Description (max 125 chars)
- **Destination URL:** Where users go when they click

### 5.2 Upload and Create Ad

```python
from src.creative.manager import CreativeManager

manager = CreativeManager(client)

# Upload image
image = manager.upload_asset("path/to/your/ad-image.jpg")
print(f"Uploaded! Hash: {image['hash']}")

# Create ad creative
creative = manager.create_simple_ad(
    name="Spring Sale Ad",
    image_path="path/to/your/ad-image.jpg",
    headline="50% Off Spring Collection",
    description="Limited time offer. Free shipping on orders over $50.",
    link="https://yourwebsite.com/spring-sale",
    call_to_action="SHOP_NOW"
)

print(f"Creative created: {creative['id']}")
```

**Call-to-Action Options:**
- `SHOP_NOW` - E-commerce
- `LEARN_MORE` - General info
- `SIGN_UP` - Lead gen
- `DOWNLOAD` - Apps
- `BOOK_NOW` - Services/events
- `GET_QUOTE` - Professional services

### 5.3 Using Templates

```python
from src.creative.templates import AdCopyTemplates

# Generate copy variations for A/B testing
variations = AdCopyTemplates.generate_variations(
    template_type="ecommerce",
    product="Premium Wireless Headphones",
    benefit="Crystal Clear Sound",
    urgency="Limited Stock"
)

for i, variation in enumerate(variations, 1):
    print(f"\nVariation {i}:")
    print(f"Headline: {variation['headline']}")
    print(f"Description: {variation['description']}")
```

---

## Step 6: Create Ad Set & Launch

### Using the Complete Workflow:

```python
from src.campaign.manager import CampaignManager

# Get your campaign ID (from Step 3)
campaigns = manager.list_campaigns()
campaign_id = campaigns[0]['id']

# Create ad set with targeting
adset = client.create_adset(
    campaign_id=campaign_id,
    name="US - Ages 25-55 - Online Shoppers",
    daily_budget=5000,  # $50 in cents
    targeting=targeting,
    optimization_goal="LINK_CLICKS",
    status="ACTIVE"
)

# Create ad with creative
ad = client.create_ad(
    adset_id=adset['id'],
    creative_id=creative['id'],
    name="Spring Sale Ad - Variation 1",
    status="ACTIVE"
)

print(f"✅ Ad is now LIVE! Ad ID: {ad['id']}")
```

---

## Step 7: Monitor Performance

### Web Dashboard:

```bash
python run_web.py
```

Visit http://localhost:8000/analytics

- View real-time metrics
- See spend, impressions, clicks, ROAS
- Detect anomalies
- Export reports

### CLI:

```bash
# Account overview
python -m src.cli analytics report --days 7

# Specific campaign
python -m src.cli analytics report --campaign-id <id> --days 7

# Live dashboard
python -m src.cli analytics dashboard

# Export to CSV
python -m src.cli analytics report --format csv
```

### Python API:

```python
from src.analytics.reporter import AnalyticsReporter

reporter = AnalyticsReporter(client)

# Get campaign report
report = reporter.campaign_report(campaign_id, days=7)

print(f"Spend: ${report['spend']:.2f}")
print(f"Impressions: {report['impressions']:,}")
print(f"Clicks: {report['clicks']:,}")
print(f"CTR: {report['ctr']:.2f}%")
print(f"CPC: ${report['cpc']:.2f}")
print(f"ROAS: {report['roas']:.2f}x")
```

---

## Step 8: Set Up Automation

### 8.1 Create Automation Rules

Edit `config/rules.yaml`:

```yaml
rules:
  - name: "Pause Low Performers"
    enabled: true
    conditions:
      - metric: "roas"
        operator: "<"
        value: 1.5
      - metric: "spend"
        operator: ">"
        value: 100
    actions:
      - type: "pause_campaign"

  - name: "Scale Winners"
    enabled: true
    conditions:
      - metric: "roas"
        operator: ">="
        value: 3.0
      - metric: "spend"
        operator: ">"
        value: 50
    actions:
      - type: "increase_budget"
        amount: 20  # Increase by 20%
```

### 8.2 Run Daily Automation

```bash
# Test it first (dry run)
python scripts/daily_automation.py --dry-run

# Run it for real
python scripts/daily_automation.py
```

### 8.3 Set Up Cron Job (Automated Daily Optimization)

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /Users/shawncarpenter/projects/facebook-ads-manager && source venv/bin/activate && python scripts/daily_automation.py
```

---

## Complete Example: End-to-End Campaign

```python
from src.api_client import FacebookAdsClient
from src.campaign.manager import CampaignManager
from src.creative.manager import CreativeManager
from src.targeting.presets import TargetingPresets

# Initialize
client = FacebookAdsClient()
campaign_mgr = CampaignManager(client)
creative_mgr = CreativeManager(client)

# 1. Create campaign
campaign = campaign_mgr.create_campaign(
    name="Spring Sale 2026",
    objective="CONVERSIONS",
    daily_budget=100,
    status="PAUSED"
)

# 2. Upload creative
creative = creative_mgr.create_simple_ad(
    name="Spring Sale Hero",
    image_path="/path/to/ad-image.jpg",
    headline="50% Off Everything",
    description="Limited time Spring sale. Free shipping.",
    link="https://yourstore.com/spring-sale",
    call_to_action="SHOP_NOW"
)

# 3. Create ad set with targeting
targeting = TargetingPresets.ecommerce_shoppers()

adset = client.create_adset(
    campaign_id=campaign['id'],
    name="US Shoppers 25-55",
    daily_budget=10000,  # $100/day in cents
    targeting=targeting,
    optimization_goal="CONVERSIONS",
    status="PAUSED"
)

# 4. Create ad
ad = client.create_ad(
    adset_id=adset['id'],
    creative_id=creative['id'],
    name="Spring Sale - Main Ad",
    status="PAUSED"
)

# 5. Review before launching
print(f"Campaign: {campaign['name']} ({campaign['id']})")
print(f"Ad Set: {adset['name']} ({adset['id']})")
print(f"Ad: {ad['name']} ({ad['id']})")
print("\nReview everything, then activate:")
print(f"python -m src.cli campaign activate --id {campaign['id']}")

# 6. Activate when ready
client.activate_campaign(campaign['id'])
client.update_adset(adset['id'], {'status': 'ACTIVE'})
client.activate_ad(ad['id'])

print("✅ Campaign is LIVE!")
```

---

## Pro Tips

### Start Small
- Begin with $20-50/day budget
- Test 2-3 ad variations
- Monitor closely for first 3 days
- Scale winners, pause losers

### Best Practices
1. **Always preview ads** before launching
2. **Use dry-run mode** for optimizations
3. **Set up automated rules** to prevent waste
4. **Monitor daily** for first week
5. **A/B test everything** (creative, copy, targeting)

### Common Mistakes to Avoid
- ❌ Don't launch with huge budgets ($500+/day)
- ❌ Don't forget to set up conversion tracking (Facebook Pixel)
- ❌ Don't use broad targeting (be specific)
- ❌ Don't ignore underperforming ads (pause them)
- ❌ Don't change too many things at once

---

## Need Help?

- **Documentation:** See `docs/tutorials.md` for 6 detailed walkthroughs
- **Examples:** Check `docs/campaign-management.md` for more examples
- **API Reference:** See `docs/api-reference.md` for all available methods
- **Web Dashboard:** Use http://localhost:8000 for visual interface

---

## Quick Reference Commands

```bash
# Validate setup
python -m src.cli validate

# List campaigns
python -m src.cli campaign list

# View performance
python -m src.cli analytics report

# Run automation
python scripts/daily_automation.py --dry-run

# Start web dashboard
python run_web.py
```

**You're ready to run Facebook ads like a pro!** 🚀
