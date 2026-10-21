"""Genre text thumbnail for the 261020 playlist: "UK / GARAGE" in the white space left of the beanie.

Run: uv run --with pillow --with numpy python scripts/playlist/thumbnail_261020.py <image> <out.png>
Only near-white background pixels take the text colour, so the figure always stays in front.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
src, out = sys.argv[1], sys.argv[2]
img = Image.open(src).convert("RGB")
a = np.asarray(img).astype(np.float32)
white = (a.min(axis=2) > 236).astype(np.uint8) * 255
bg = np.asarray(Image.fromarray(white, "L").filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1))).astype(np.float32) / 255
path = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
layer = Image.new("L", img.size, 0)
d = ImageDraw.Draw(layer)
x0, target = 56, 556  # GARAGE ends just before the beanie edge
size = 100
while ImageFont.truetype(path, size + 2).getlength("GARAGE") < target - x0:
    size += 2
fg = ImageFont.truetype(path, size)
fu = ImageFont.truetype(path, int(size * 2.1))
bu = d.textbbox((0, 0), "UK", font=fu); bgx = d.textbbox((0, 0), "GARAGE", font=fg)
y_uk = 110
d.text((x0 - bu[0], y_uk - bu[1]), "UK", font=fu, fill=255)
y_g = y_uk + (bu[3] - bu[1]) + 22
d.text((x0 - bgx[0], y_g - bgx[1]), "GARAGE", font=fg, fill=255)
m = Image.fromarray((np.asarray(layer).astype(np.float32) * bg).astype(np.uint8), "L")
res = img.copy()
res.paste(Image.new("RGB", img.size, (50, 46, 46)), (0, 0), m)
res.save(out)
print(size)
