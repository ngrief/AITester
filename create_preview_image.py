"""
Create LinkedIn/Social Media Preview Image
Creates a 1200x627 PNG image for Open Graph preview
"""

from PIL import Image, ImageDraw, ImageFont
import os

# LinkedIn recommended size: 1200 x 627
width = 1200
height = 627

# Create image with gradient background
img = Image.new('RGB', (width, height), color='#0A2F35')
draw = ImageDraw.Draw(img)

# Draw gradient effect (simple approximation)
for i in range(height):
    alpha = i / height
    r = int(10 + (26-10) * alpha)
    g = int(47 + (26-47) * alpha)
    b = int(53 + (46-53) * alpha)
    draw.rectangle([(0, i), (width, i+1)], fill=(r, g, b))

# Add text
try:
    # Try to use a nice font
    title_font = ImageFont.truetype("arial.ttf", 72)
    subtitle_font = ImageFont.truetype("arial.ttf", 36)
    detail_font = ImageFont.truetype("arial.ttf", 28)
except:
    # Fallback to default
    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()
    detail_font = ImageFont.load_default()

# Title
title = "Fortress 2.0"
title_bbox = draw.textbbox((0, 0), title, font=title_font)
title_width = title_bbox[2] - title_bbox[0]
title_x = (width - title_width) // 2
draw.text((title_x, 120), title, fill='#00CED1', font=title_font)

# Subtitle
subtitle = "Multi-Strategy Trading Framework"
subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
subtitle_x = (width - subtitle_width) // 2
draw.text((subtitle_x, 220), subtitle, fill='#E0E0E0', font=subtitle_font)

# Details
details = [
    "3 Systematic Strategies • 41 AI/Tech Stocks",
    "Backtested: 2022-2024",
    "Interactive Dashboard with Plotly"
]

y_position = 320
for detail in details:
    detail_bbox = draw.textbbox((0, 0), detail, font=detail_font)
    detail_width = detail_bbox[2] - detail_bbox[0]
    detail_x = (width - detail_width) // 2
    draw.text((detail_x, y_position), detail, fill='#B0B0B0', font=detail_font)
    y_position += 50

# Add accent line
draw.rectangle([(400, 500), (800, 505)], fill='#00CED1')

# Tech stack footer
footer = "VectorBT • pandas-ta • Plotly"
footer_bbox = draw.textbbox((0, 0), footer, font=detail_font)
footer_width = footer_bbox[2] - footer_bbox[0]
footer_x = (width - footer_width) // 2
draw.text((footer_x, 540), footer, fill='#808080', font=detail_font)

# Save
output_path = "preview.png"
img.save(output_path, 'PNG', quality=95)
print(f"[OK] Preview image created: {output_path}")
print(f"  Size: {width}x{height} (LinkedIn recommended)")
print(f"  Format: PNG")
print(f"\nNext steps:")
print(f"1. Commit and push preview.png to GitHub")
print(f"2. Update index.html with og:image tag")
print(f"3. LinkedIn will cache the image when you share the link")
