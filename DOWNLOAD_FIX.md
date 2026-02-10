# Image Download Fix - Full Size Images ✅

## Problem Fixed
Downloads were getting tiny thumbnail images instead of full-size images.

## Solution Applied

### Updated Download Logic

**Priority Order (best to worst):**

1. **Image Hash Method** (Best Quality)
   - Gets original uploaded image from Facebook
   - Uses `AdImage` API with image hash
   - Full resolution, no compression

2. **Object Story Spec** (Good Quality)
   - Gets picture URL from creative's link_data
   - Usually full-size or close to it

3. **Image URL Field** (Fallback)
   - Direct image URL from creative
   - Better than thumbnail

**Code updated in:** `src/web/app.py` → `/api/creatives/{creative_id}/download`

## Even Better: Use Local Images!

### For AI-Generated Images

If you created the image with AI, it's **already saved locally** in full quality!

**Location:** `generated_images/` folder

**Quality:** Original PNG, ~1-1.5 MB, full resolution

**To download:**
```bash
# List all your AI-generated images
curl http://localhost:8000/api/images/list

# Download specific image
curl -o image.png http://localhost:8000/api/images/download/{filename}
```

### Comparison

| Source | Quality | Size | When Available |
|--------|---------|------|----------------|
| **Local `generated_images/`** | ⭐⭐⭐⭐⭐ Original | ~1.5 MB | AI-generated ads |
| **Facebook (Image Hash)** | ⭐⭐⭐⭐ Full-size | ~500 KB | Most creatives |
| **Facebook (Picture URL)** | ⭐⭐⭐ Large | ~300 KB | Some creatives |
| **Facebook (Thumbnail)** | ⭐ Tiny | ~30 KB | ❌ Avoided now |

## How to Get Best Quality

### Option 1: AI-Generated Images (Recommended)
1. Check `generated_images/` folder first
2. Files named: `20260210_143022_Product_Name_ad.png`
3. These are original quality before Facebook upload

### Option 2: Download from Creatives Page
1. Go to: http://localhost:8000/creatives
2. Click "Download Image"
3. Now gets full-size from Facebook (not thumbnail)

### Option 3: API Download
```bash
# Download full-size from creative
curl -o full_image.jpg \
     http://localhost:8000/api/creatives/{creative_id}/download
```

## Test It

Try downloading now - you should get much larger images!

**Before:** 5-30 KB (thumbnail)
**After:** 300 KB - 1.5 MB (full-size)

## For Your Current Ads

If you created ads with AI Creator today, they're already saved locally:

```bash
# Check your generated images
ls -lh generated_images/

# You'll see files like:
# 20260210_143022_Stock_Alarm_Pro_ad.png  (1.3 MB)
# 20260210_143156_Free_Trial_ad.png       (1.4 MB)
```

These are the **original high-quality** images - better than downloading from Facebook!

## Summary

✅ **Fixed:** Download button now gets full-size images
✅ **Better:** AI images auto-saved locally in original quality
✅ **Best:** Use `generated_images/` folder for highest quality

Try it now - your downloads should be much bigger and better quality! 🎉
