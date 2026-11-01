"""Lay a desaturated, twisted glitch over a dark Frankenstein figure image.

The base image stays clean; the glitch is code so the same function can later
drive moving glitch in the video (vary `seed` / `strength` per frame).

Run: uv run --with pillow --with numpy python scripts/playlist/glitch_frankenstein.py IN.png OUT.png [--seed N] [--strength S]
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def luminance(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def figure_rows(a, thresh=18.0):
    """Vertical range of the lit figure (rows with any pixel brighter than thresh)."""
    rows = np.where((luminance(a) > thresh).any(axis=1))[0]
    if len(rows) == 0:
        return 0, a.shape[0]
    return int(rows[0]), int(rows[-1])


def twist(a, rng, top, bottom, strength, coverage=1.0):
    """Shift rows sideways: a slow sine sway plus random torn bands (the 'twisted' look)."""
    h, w, _ = a.shape
    out = a.copy()
    y = np.arange(h)
    sway = (np.sin(y / 23.0 + rng.uniform(0, 6)) * 6 + np.sin(y / 7.0) * 2) * strength
    shift = np.zeros(h)
    shift[top:bottom] = sway[top:bottom]
    y0 = top
    while y0 < bottom:
        band = int(rng.integers(3, 28))
        if rng.random() < 0.6 * coverage:
            shift[y0:y0 + band] += rng.normal(0, 90) * strength
        y0 += band + int(rng.integers(2, 18))
    for r in range(top, min(bottom, h)):
        s = int(round(shift[r]))
        if s:
            out[r] = np.roll(a[r], s, axis=0)
    return out


def smear(a, rng, top, bottom, strength, coverage=1.0):
    """Horizontal light trails: bright pixels in some bands bleed sideways and fade."""
    out = a.copy()
    y0 = top
    while y0 < bottom:
        band = int(rng.integers(2, 14))
        if rng.random() < 0.5 * coverage:
            seg = out[y0:y0 + band].astype(np.float32)
            trail = seg.copy()
            decay = rng.uniform(0.985, 0.997)
            step = 1 if rng.random() < 0.6 else -1
            xs = range(1, seg.shape[1]) if step == 1 else range(seg.shape[1] - 2, -1, -1)
            for x in xs:
                trail[:, x] = np.maximum(seg[:, x], trail[:, x - step] * decay)
            mix = min(1.0, 0.85 * strength)
            out[y0:y0 + band] = (seg * (1 - mix) + trail * mix).astype(np.uint8)
        y0 += band + int(rng.integers(4, 24))
    return out


def ghosts(a, rng, top, bottom, strength, coverage=1.0):
    """Echo copies of torn bands, offset sideways and screen-blended (stacked double images)."""
    out = a.astype(np.float32)
    y0 = top
    while y0 < bottom:
        band = int(rng.integers(6, 40))
        if rng.random() < 0.4 * coverage:
            for _ in range(int(rng.integers(1, 3))):
                dx = int(rng.normal(0, 40) * strength)
                echo = np.roll(a[y0:y0 + band], dx, axis=1).astype(np.float32) * rng.uniform(0.4, 0.8)
                seg = out[y0:y0 + band]
                out[y0:y0 + band] = 255 - (255 - seg) * (255 - echo) / 255
        y0 += band + int(rng.integers(4, 30))
    return out.clip(0, 255).astype(np.uint8)


def pixel_blocks(a, rng, top, bottom, strength, count=5):
    """A few mosaic blocks over the figure."""
    out = a.copy()
    h, w, _ = a.shape
    lum = luminance(a)
    cols = np.where((lum[top:bottom] > 18).any(axis=0))[0]
    if len(cols) == 0:
        return out
    left, right = int(cols[0]), int(cols[-1])
    for _ in range(int(count * strength)):
        bw, bh = int(rng.integers(30, 110)), int(rng.integers(14, 50))
        x = int(rng.integers(left, max(left + 1, right - bw)))
        y = int(rng.integers(top, max(top + 1, bottom - bh)))
        cell = int(rng.choice([8, 12, 16]))
        block = Image.fromarray(out[y:y + bh, x:x + bw])
        small = block.resize((max(1, bw // cell), max(1, bh // cell)), Image.BILINEAR)
        out[y:y + bh, x:x + bw] = np.asarray(small.resize((bw, bh), Image.NEAREST))
    return out


def vertical_streaks(a, strength):
    """Soft downward light streaks from bright areas, screen-blended (the ghostly dove look)."""
    img = Image.fromarray(a)
    bright = img.point(lambda v: max(0, v - 60) * 2)
    streak = np.asarray(bright, dtype=np.float32)
    acc = streak.copy()
    for d in range(1, 90, 3):
        acc = np.maximum(acc, np.roll(streak, d, axis=0) * (1 - d / 90))
    acc = np.asarray(Image.fromarray(acc.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)), dtype=np.float32)
    base = a.astype(np.float32)
    k = 0.35 * strength
    return (255 - (255 - base) * (255 - acc * k) / 255).clip(0, 255).astype(np.uint8)


def rgb_split(a, shift, saturation):
    """Offset red/blue channels, then pull colour back toward grey so the fringe stays muted."""
    out = a.copy()
    out[..., 0] = np.roll(a[..., 0], -shift, axis=1)
    out[..., 2] = np.roll(a[..., 2], shift, axis=1)
    f = out.astype(np.float32)
    grey = luminance(f)[..., None]
    return (grey + (f - grey) * saturation).clip(0, 255).astype(np.uint8)


def film_noise(a, rng, amount, lift=6):
    """Monochrome grain over the whole frame, blacks lifted a little so the grain shows on black."""
    h, w, _ = a.shape
    grain = rng.normal(0, amount, (h, w)).astype(np.float32)
    grain = np.asarray(Image.fromarray((grain + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)), dtype=np.float32) - 128
    return (a.astype(np.float32) + lift + grain[..., None]).clip(0, 255).astype(np.uint8)


def glitch(img, seed=0, strength=1.0, saturation=0.45, gamma=1.0, coverage=1.0, blocks=5, noise=0.0):
    rng = np.random.default_rng(seed)
    a = np.asarray(img.convert("RGB"))
    top, bottom = figure_rows(a)
    pad = int((bottom - top) * 0.05)
    top, bottom = max(0, top - pad), min(a.shape[0], bottom + pad)
    a = vertical_streaks(a, strength)
    a = ghosts(a, rng, top, bottom, strength, coverage)
    a = twist(a, rng, top, bottom, strength, coverage)
    a = smear(a, rng, top, bottom, strength, coverage)
    a = pixel_blocks(a, rng, top, bottom, strength, blocks)
    a = rgb_split(a, int(round(9 * strength)), saturation)
    if gamma != 1.0:
        # Darken after the glitch so the light trails keep their shape; gamma keeps highlights.
        a = (255 * (a / 255.0) ** gamma).astype(np.uint8)
    if noise > 0:
        a = film_noise(a, rng, noise)
    return Image.fromarray(a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("dst", type=Path)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--strength", type=float, default=1.0)
    ap.add_argument("--saturation", type=float, default=0.45)
    ap.add_argument("--gamma", type=float, default=1.0, help=">1 darkens")
    ap.add_argument("--coverage", type=float, default=1.0, help="share of rows torn (1.0 = default)")
    ap.add_argument("--blocks", type=int, default=5, help="number of mosaic blocks")
    ap.add_argument("--noise", type=float, default=0.0, help="film grain amount (0 = off)")
    args = ap.parse_args()
    if args.dst.exists():
        raise SystemExit(f"refusing to overwrite {args.dst}")
    glitch(Image.open(args.src), args.seed, args.strength, args.saturation, args.gamma, args.coverage, args.blocks, args.noise).save(args.dst)
    print(args.dst)


if __name__ == "__main__":
    main()
