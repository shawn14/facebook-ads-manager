"""Generate simple placeholder ad images for testing."""

from PIL import Image, ImageDraw, ImageFont
import os

# Create assets directory if it doesn't exist
os.makedirs('assets', exist_ok=True)

# Image settings
WIDTH = 1080
HEIGHT = 1080
BACKGROUND_COLORS = [
    (41, 128, 185),   # Blue - Campaign 1
    (52, 152, 219),   # Light Blue - Campaign 2
    (41, 98, 155),    # Dark Blue - Campaign 3
]

# Campaign messages
CAMPAIGNS = [
    {
        'filename': 'assets/ad1_never_miss.jpg',
        'title': 'Never Miss a\nStock Move',
        'subtitle': 'Real-time alerts for your portfolio',
        'color': BACKGROUND_COLORS[0]
    },
    {
        'filename': 'assets/ad2_your_stocks.jpg',
        'title': 'Your Stocks\nYour Alerts',
        'subtitle': 'Custom price notifications',
        'color': BACKGROUND_COLORS[1]
    },
    {
        'filename': 'assets/ad3_stop_guessing.jpg',
        'title': 'Stop Guessing\nStart Knowing',
        'subtitle': 'Smart stock alerts',
        'color': BACKGROUND_COLORS[2]
    }
]

print("🎨 Generating placeholder ad images...\n")

for i, campaign in enumerate(CAMPAIGNS, 1):
    # Create image with colored background
    img = Image.new('RGB', (WIDTH, HEIGHT), campaign['color'])
    draw = ImageDraw.Draw(img)

    # Try to use a system font, fallback to default
    try:
        title_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 100)
        subtitle_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 50)
        url_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 40)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        url_font = ImageFont.load_default()

    # Draw title (centered, upper area)
    title_bbox = draw.multiline_textbbox((0, 0), campaign['title'], font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    title_x = (WIDTH - title_width) // 2
    title_y = HEIGHT // 3

    draw.multiline_text(
        (title_x, title_y),
        campaign['title'],
        fill='white',
        font=title_font,
        align='center'
    )

    # Draw subtitle (centered, middle area)
    subtitle_bbox = draw.textbbox((0, 0), campaign['subtitle'], font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (WIDTH - subtitle_width) // 2
    subtitle_y = title_y + title_height + 80

    draw.text(
        (subtitle_x, subtitle_y),
        campaign['subtitle'],
        fill='white',
        font=subtitle_font
    )

    # Draw URL at bottom
    url_text = "pro.stockalarm.io"
    url_bbox = draw.textbbox((0, 0), url_text, font=url_font)
    url_width = url_bbox[2] - url_bbox[0]
    url_x = (WIDTH - url_width) // 2
    url_y = HEIGHT - 150

    draw.text(
        (url_x, url_y),
        url_text,
        fill='white',
        font=url_font
    )

    # Add a simple icon/shape at the top
    # Draw a bell icon representation (simple circle)
    icon_center_x = WIDTH // 2
    icon_center_y = 200
    icon_radius = 60
    draw.ellipse(
        [icon_center_x - icon_radius, icon_center_y - icon_radius,
         icon_center_x + icon_radius, icon_center_y + icon_radius],
        outline='white',
        width=8
    )

    # Save image
    img.save(campaign['filename'], 'JPEG', quality=95)
    print(f"✓ Created: {campaign['filename']}")

print("\n✅ All 3 placeholder images created!")
print("\nThese are simple placeholder images for testing.")
print("You can replace them with professional designs later.")
print("\nNext: Run the creative creation script:")
print("  python create_ad_creatives_with_images.py")
