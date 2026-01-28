#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

# Create base icon 1024x1024
size = 1024
img = Image.new('RGB', (size, size), '#1a1a2e')
draw = ImageDraw.Draw(img)

# Draw gradient-like background
for i in range(size):
    color = (26 + i//20, 26 + i//30, 46 + i//15)
    color = tuple(min(255, c) for c in color)
    draw.line([(0, i), (size, i)], fill=color)

# Draw 'E' letter
try:
    font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 600)
except:
    font = ImageFont.load_default()

# Center the E
text = 'E'
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (size - text_width) // 2
y = (size - text_height) // 2 - 50

# Draw E with orange color
draw.text((x, y), text, fill='#ff9500', font=font)

# Save
output_dir = 'ios/EnlikoTrading/EnlikoTrading/Assets.xcassets/AppIcon.appiconset'
os.makedirs(output_dir, exist_ok=True)

img.save(f'{output_dir}/icon-1024.png')
print('Created icon-1024.png')

# All required sizes for iOS
required_sizes = [20, 29, 40, 58, 60, 76, 80, 87, 120, 152, 167, 180, 1024]

for px in required_sizes:
    resized = img.resize((px, px), Image.LANCZOS)
    resized.save(f'{output_dir}/icon-{px}.png')
    print(f'Created icon-{px}.png')

print('All icons created!')
