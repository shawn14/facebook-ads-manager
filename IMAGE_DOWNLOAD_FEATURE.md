# Image Download Feature ✅

## Overview

You can now download images from your ads in multiple ways:
1. **Download from Creatives page** - Download any creative's image
2. **Auto-save AI images** - AI-generated images are automatically saved locally
3. **Browse saved images** - View all generated images via API

## Features Added

### 1. Download Creative Images

**From Creatives Page:**
1. Go to: http://localhost:8000/creatives
2. Find any creative
3. Click "Download Image" button
4. ✅ Image downloads to your computer!

**How it works:**
- Fetches image from Facebook
- Downloads as `creative_{ID}.jpg`
- Works for all image creatives

### 2. Auto-Save AI-Generated Images

**When you create ads with AI:**
- All AI-generated images are **automatically saved** to `generated_images/` folder
- Saved in original quality (before Facebook upload)
- Filenames include timestamp and product name

**Example:**
```
generated_images/
├── 20260210_143022_Stock Alarm Pro_ad.png
├── 20260210_143156_Stock Alarm_ad.png
└── 20260210_143301_Free Trial_ad.png
```

### 3. New API Endpoints

**Download from Creative:**
```bash
# Download image from Facebook creative
GET /api/creatives/{creative_id}/download

# Example
curl -o my_ad.jpg http://localhost:8000/api/creatives/23857123456789012/download
```

**Download Locally Saved Image:**
```bash
# Download from local generated_images folder
GET /api/images/download/{filename}

# Example
curl -o saved_image.png http://localhost:8000/api/images/download/20260210_143022_Stock_Alarm_Pro_ad.png
```

**List All Generated Images:**
```bash
# List all AI-generated images
GET /api/images/list

# Returns
{
  "images": [
    {
      "filename": "20260210_143022_Stock_Alarm_Pro_ad.png",
      "size": 1318104,
      "created": "2026-02-10T14:30:22",
      "download_url": "/api/images/download/20260210_143022_Stock_Alarm_Pro_ad.png"
    }
  ],
  "count": 1
}
```

**Get Creative Image URL:**
```bash
# Get Facebook image URL for a creative
GET /api/creatives/{creative_id}/image

# Returns
{
  "creative_id": "23857123456789012",
  "image_url": "https://scontent.xx.fbcdn.net/...",
  "can_download": true
}
```

## Usage Examples

### Example 1: Download All Your Ad Images

```bash
# 1. List all creatives
curl http://localhost:8000/api/creatives

# 2. Download each creative's image
for creative_id in $(curl -s http://localhost:8000/api/creatives | jq -r '.creatives[].id'); do
    curl -o "creative_${creative_id}.jpg" \
         "http://localhost:8000/api/creatives/${creative_id}/download"
done
```

### Example 2: List All AI-Generated Images

```bash
curl http://localhost:8000/api/images/list | jq
```

Response:
```json
{
  "images": [
    {
      "filename": "20260210_143022_Stock_Alarm_Pro_ad.png",
      "size": 1318104,
      "created": "2026-02-10T14:30:22.123456",
      "download_url": "/api/images/download/20260210_143022_Stock_Alarm_Pro_ad.png"
    },
    {
      "filename": "20260210_142015_Day_Traders_ad.png",
      "size": 1265432,
      "created": "2026-02-10T14:20:15.654321",
      "download_url": "/api/images/download/20260210_142015_Day_Traders_ad.png"
    }
  ],
  "count": 2
}
```

### Example 3: Download Specific Saved Image

```bash
curl -o my_saved_image.png \
     http://localhost:8000/api/images/download/20260210_143022_Stock_Alarm_Pro_ad.png
```

## Web UI Features

### Creatives Page

**Download Button:**
- Every creative card now has a "Download Image" button
- Click to download the image directly from Facebook
- Saves as `creative_{ID}.jpg`

**Visual Indicator:**
- Green button with download icon
- Shows "Download Image"
- Works for all image-type creatives

## File Organization

### Generated Images Folder

**Location:** `generated_images/`

**Naming Convention:**
```
{timestamp}_{product_name}_ad.png

Examples:
20260210_143022_Stock_Alarm_Pro_ad.png
20260210_142015_Day_Traders_ad.png
```

**When Images Are Saved:**
- ✅ AI Creator generates image
- ✅ Direct API call to `/api/images/generate`
- ✅ Creating complete ads with `/api/ai/create-ad-from-prompt`

**Image Format:**
- PNG format (original quality)
- Full resolution before Facebook resizing
- Typically 1-1.5 MB per image

## Complete Workflow

### Workflow 1: Create & Download AI Ad Image

1. **Create AI Ad:**
   - Go to AI Creator
   - Generate ad with Google Gemini
   - Image automatically saved to `generated_images/`

2. **Download Options:**
   - Option A: Find file in `generated_images/` folder
   - Option B: Go to Creatives page → Click "Download Image"
   - Option C: Use API: `GET /api/images/list` → Download via URL

### Workflow 2: Download Existing Creative Images

1. **Go to Creatives Page:**
   - http://localhost:8000/creatives

2. **Browse Your Creatives:**
   - View all creatives in grid

3. **Download:**
   - Click "Download Image" on any creative
   - Image downloads automatically

## Python Usage

### Download Image Programmatically

```python
import requests

# Download creative image
creative_id = "23857123456789012"
response = requests.get(f"http://localhost:8000/api/creatives/{creative_id}/download")

if response.ok:
    with open(f"creative_{creative_id}.jpg", "wb") as f:
        f.write(response.content)
    print("✅ Image downloaded!")
```

### List Generated Images

```python
import requests

response = requests.get("http://localhost:8000/api/images/list")
data = response.json()

print(f"Total images: {data['count']}")
for img in data['images']:
    print(f"  - {img['filename']} ({img['size']} bytes)")
    print(f"    Download: {img['download_url']}")
```

### Download Saved Image

```python
import requests

filename = "20260210_143022_Stock_Alarm_Pro_ad.png"
response = requests.get(f"http://localhost:8000/api/images/download/{filename}")

if response.ok:
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"✅ Downloaded: {filename}")
```

## Benefits

### Before
- ❌ Images only in Facebook
- ❌ No way to save original high-quality versions
- ❌ Manual screenshot needed
- ❌ Lose images if creative deleted

### After
- ✅ Auto-save all AI-generated images
- ✅ Download any creative's image anytime
- ✅ Keep original high-quality versions
- ✅ Build image library for reuse
- ✅ Backup images locally

## Tips

1. **Organize Your Images:**
   - `generated_images/` folder has all AI images
   - Organized by timestamp
   - Easy to find recent images

2. **Reuse Images:**
   - Download once, use multiple times
   - Upload to other platforms
   - Keep for portfolio/archive

3. **Quality:**
   - AI images saved in original quality
   - Better than downloading from Facebook
   - Perfect for print or high-res use

4. **Backup:**
   - All AI-generated images are backed up locally
   - Won't lose images if Facebook creative deleted
   - Can restore/recreate ads anytime

## Troubleshooting

### Image Not Downloading
**Issue:** Download button doesn't work

**Solutions:**
1. Check creative has an image (not video)
2. Check Facebook creative still exists
3. Try API endpoint directly: `/api/creatives/{id}/download`
4. Check browser console for errors

### Can't Find Saved Images
**Issue:** Generated images not in folder

**Solutions:**
1. Check `generated_images/` folder exists
2. Verify `save_locally=True` in API calls
3. Check server has write permissions
4. Look for images in API: `GET /api/images/list`

### Download Returns 404
**Issue:** API returns "Image not found"

**Solutions:**
1. Verify creative ID is correct
2. Check creative type is "image" not "video"
3. Ensure creative exists in Facebook
4. Try getting image URL first: `/api/creatives/{id}/image`

## Summary

You now have **3 ways** to download images:

1. **Auto-Save:** AI images saved automatically → `generated_images/` folder
2. **Web UI:** Creatives page → "Download Image" button
3. **API:** Direct download via REST endpoints

All images are preserved in high quality for backup, reuse, and archival! ✅
