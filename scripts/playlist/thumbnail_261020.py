"""Genre text thumbnail for the 261020 playlist: one line "UK GARAGE" in Bodoni Moda Bold,
laid over the figure across the centre in the beanie star colour (user pick, variant "line / star").

Run: uv run --with pillow --with numpy python scripts/playlist/thumbnail_261020.py <image> <out_dir> references/local/fonts/BodoniModa_72pt-Bold.ttf
Writes four variants (stack|line x invert|star); the thumbnail uses over_line_star.png.
The font file lives in references/local/fonts/ (OFL, not tracked by Git).
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
src, out_dir, font_path = sys.argv[1:4]
img = Image.open(src).convert("RGB")
W, H = img.size
base = np.asarray(img).astype(np.float32)
lum = (base @ np.array([0.299, 0.587, 0.114], np.float32))
CHAR, CREAM, STAR = np.array((50, 46, 46), np.float32), np.array((247, 243, 239), np.float32), np.array((186, 166, 167), np.float32)

def fit(word, width):
    size = 60
    while ImageFont.truetype(font_path, size + 4).getlength(word) < width:
        size += 4
    return ImageFont.truetype(font_path, size)

def mask(lines):
    layer = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(layer)
    for word, f, cy in lines:
        b = d.textbbox((0, 0), word, font=f)
        d.text(((W - (b[2] - b[0])) / 2 - b[0], cy - (b[3] + b[1]) / 2), word, font=f, fill=255)
    return np.asarray(layer).astype(np.float32)[..., None] / 255

layouts = {
    # Two lines: UK on the beanie, GARAGE across the lower face and collar; the eyes stay clear.
    "stack": lambda: [("UK", fit("UK", 640), 215), ("GARAGE", fit("GARAGE", 1760), 790)],
    # One line straight through the centre.
    "line": lambda: [("UK GARAGE", fit("UK GARAGE", 1800), 560)],
}
for lname, lay in layouts.items():
    m = mask(lay())
    # Invert: charcoal over light areas, cream over the dark beanie / hair / sweater.
    t = np.clip((lum - 90) / 60, 0, 1)[..., None]
    col = CREAM * (1 - t) + CHAR * t
    for cname, c in (("invert", col), ("star", STAR)):
        res = base * (1 - m) + c * m
        Image.fromarray(res.round().astype(np.uint8)).save(f"{out_dir}/over_{lname}_{cname}.png")
        print(lname, cname)
