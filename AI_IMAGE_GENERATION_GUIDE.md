# AI Image Generation for Facebook Ads - Setup Guide

## 🎨 What I Just Built For You

Your Facebook Ads Manager now has **AI-powered image generation** using OpenAI's DALL-E! You can:

1. ✅ **Generate ad images with AI** - Describe what you want, AI creates it
2. ✅ **Upload your own images** - Manual upload support
3. ✅ **Auto-resize for Facebook** - Images automatically sized to Facebook specs
4. ✅ **Create complete ads** - Headline + copy + image in one step
5. ✅ **Character validation** - Real-time limits (40 headline / 125 description)
6. ✅ **Multiple styles** - Professional, modern, minimalist, bold, tech, finance

---

## 🚀 Setup (Required for AI Generation)

### Step 1: Get Your OpenAI API Key

1. Go to: https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click **"Create new secret key"**
4. Copy the key (starts with `sk-...`)

### Step 2: Add API Key to Config

Edit `config/config.yaml` and add your key:

```yaml
# OpenAI API for AI image generation
openai:
  api_key: "sk-your-actual-key-here"
```

**Or** set as environment variable:
```bash
export OPENAI_API_KEY="sk-your-actual-key-here"
```

### Step 3: Restart the Web Server

```bash
# Stop current server (Ctrl+C in terminal)
# Then restart:
python run_web.py
```

---

## 🎯 How to Use

### Method 1: AI-Generated Images (Recommended)

**Create an Ad with AI-Generated Image:**

```bash
curl -X POST http://localhost:8000/api/creatives/create-with-image \
  -F "name=Stock Alert Ad Campaign" \
  -F "headline=Never Miss a Price Move" \
  -F "description=Get instant alerts when stocks hit your price targets. Try free for 14 days." \
  -F "link_url=https://pro.stockalarm.io/" \
  -F "call_to_action=LEARN_MORE" \
  -F "generate_image=true" \
  -F "image_prompt=Professional stock market trading dashboard with price alerts and notifications" \
  -F "product_name=Stock Alarm Pro" \
  -F "style=finance"
```

**Available Styles:**
- `professional` - Clean, corporate style
- `modern` - Sleek, contemporary design
- `minimalist` - Simple, elegant
- `bold` - Vibrant, eye-catching
- `tech` - High-tech, futuristic
- `finance` - Financial, trustworthy (RECOMMENDED for Stock Alarm)

### Method 2: Upload Your Own Image

**Step 1: Upload Image**
```bash
curl -X POST http://localhost:8000/api/images/upload \
  -F "file=@/path/to/your/image.jpg"
```

Response:
```json
{
  "image_hash": "abc123...",
  "filename": "image.jpg",
  "size": 245678,
  "status": "uploaded"
}
```

**Step 2: Create Ad with Uploaded Image**
```bash
curl -X POST http://localhost:8000/api/creatives/create-with-image \
  -F "name=My Ad" \
  -F "headline=Buy Now" \
  -F "description=Limited time offer!" \
  -F "link_url=https://yoursite.com" \
  -F "call_to_action=SHOP_NOW" \
  -F "image_hash=abc123..."
```

### Method 3: Generate Image Only

**Generate and upload AI image without creating ad:**
```bash
curl -X POST http://localhost:8000/api/images/generate \
  -F "prompt=Stock market trading interface with charts" \
  -F "product_name=Stock Alarm Pro" \
  -F "style=finance" \
  -F "format_type=feed"
```

Returns image_hash you can use later.

---

## 📐 Image Specifications

### Facebook Ad Formats

| Format | Size | Aspect Ratio | Use Case |
|--------|------|--------------|----------|
| Feed | 1200x628px | 1.91:1 | News feed ads (default) |
| Square | 1080x1080px | 1:1 | Instagram, carousel |
| Story | 1080x1920px | 9:16 | Instagram/FB stories |
| Carousel | 1080x1080px | 1:1 | Multi-image ads |

### Character Limits

- **Headline**: 40 characters max
- **Primary Text (Description)**: 125 characters max
- **Link Description**: 30 characters max

### Image Requirements

- **Max file size**: 30MB (images), 4GB (videos)
- **Formats**: JPG, PNG (images), MP4, MOV (videos)
- **Text in image**: Keep minimal (Facebook limits)

---

## 🤖 AI Prompt Tips

### Good Prompts

✅ **Specific and descriptive:**
- "Professional financial dashboard showing stock price alerts and notifications on a mobile phone"
- "Modern trading platform interface with real-time market data and price charts"
- "Minimalist stock screener app on smartphone with clean UI"

✅ **Include context:**
- Mention the device (mobile, desktop, tablet)
- Specify the setting (office, home, on-the-go)
- Describe the mood (professional, exciting, trustworthy)

### Bad Prompts

❌ **Too vague:**
- "Stock app"
- "Finance stuff"
- "Trading"

❌ **Including text:**
- Don't ask for specific text in images (Facebook adds headlines/copy separately)

### Prompt Suggestions

**For Stock Alarm Pro ads:**

1. **Alert-focused:**
   - "Smartphone displaying stock price alert notification with rising chart in background, professional finance style"

2. **Dashboard-focused:**
   - "Clean stock trading dashboard interface with real-time price monitoring and alert settings, modern tech aesthetic"

3. **Lifestyle-focused:**
   - "Professional trader checking stock alerts on mobile phone in modern office, confident and successful"

4. **Data-focused:**
   - "Financial charts and graphs showing stock price movements with alert indicators, professional visualization"

---

## 📋 API Endpoints Reference

### Image Generation

**POST** `/api/images/generate`
- Generate AI image and upload to Facebook
- Returns: `image_hash`

**POST** `/api/images/upload`
- Upload your own image to Facebook
- Returns: `image_hash`

**POST** `/api/images/suggest-prompt`
- Get AI-suggested prompt based on your ad copy
- Helps write better image prompts

### Creative Creation

**POST** `/api/creatives/create-with-image`
- Create complete ad with image (uploaded or AI-generated)
- All-in-one ad creation

**POST** `/api/creatives/image`
- Create image ad creative (requires existing image_hash)

**POST** `/api/creatives/video`
- Create video ad creative

**GET** `/api/creatives`
- List all your ad creatives

**GET** `/api/creatives/specifications`
- Get Facebook's ad specs and limits

---

## 💡 Best Practices

### 1. Test Multiple Variations

Generate 3-5 image variations for A/B testing:

```bash
# Variation 1: Close-up
curl -X POST http://localhost:8000/api/images/generate \
  -F "prompt=Close-up of stock alert notification on phone screen" \
  -F "style=finance"

# Variation 2: Wide view
curl -X POST http://localhost:8000/api/images/generate \
  -F "prompt=Trading desk with multiple monitors showing stock data" \
  -F "style=professional"

# Variation 3: Lifestyle
curl -X POST http://localhost:8000/api/images/generate \
  -F "prompt=Successful trader reviewing stock alerts on mobile" \
  -F "style=modern"
```

### 2. Match Image to Copy

Make sure your image visually supports your headline and description:

**Headline**: "Never Miss a Big Move"
**Image**: Stock charts with alert indicators

**Headline**: "Stop Missing Price Alerts"
**Image**: Phone with notification alerts

### 3. Use Finance Style for Stock Alarm

The `finance` style works best for financial products:
- Professional and trustworthy
- Charts and data visualization
- Corporate color schemes

---

## 🔧 Troubleshooting

### "Failed to generate image. Check OpenAI API key"

**Solution:**
1. Verify API key is set in `config/config.yaml`
2. Or set environment variable: `export OPENAI_API_KEY="sk-..."`
3. Restart web server
4. Check API key is valid at https://platform.openai.com/api-keys

### "Image upload failed"

**Solution:**
- Check image file size (max 30MB)
- Verify format is JPG or PNG
- Ensure Facebook access token is valid

### "Character limit exceeded"

**Solution:**
- Headline: Max 40 characters
- Description: Max 125 characters
- Edit your copy to fit limits

### AI images look generic

**Solution:**
- Be more specific in prompts
- Include details about device, setting, mood
- Try different styles (finance, professional, modern)
- Generate multiple variations

---

## 📊 Cost Estimates

### OpenAI DALL-E Pricing

- **Standard quality**: ~$0.040 per image (1024x1024)
- **HD quality**: ~$0.080 per image (1024x1024)

**Example:** 100 ad variations = $4-$8

Much cheaper than hiring a designer for each variation!

---

## 🎯 Next Steps

1. ✅ Get OpenAI API key
2. ✅ Add to config.yaml
3. ✅ Restart web server
4. ✅ Test generating an image
5. ✅ Create your first AI-powered ad
6. ✅ A/B test multiple variations
7. ✅ Scale your ad creation

**You now have a complete AI-powered ad creation system!** 🚀

---

## Need Help?

- **OpenAI docs**: https://platform.openai.com/docs
- **Facebook ad specs**: https://www.facebook.com/business/ads-guide
- **Check logs**: Look at web server output for detailed error messages
