"""Render the 261101 Frankenstein (the text / preface) playlist video, one pass.

The chosen still (v4, glitch seed 3, strength 0.5, gamma 1.4) is the steady frame.
Every frame gets fresh film grain; every few seconds a short burst of other glitch
renders flickers in. The BG TAPE panel keeps the cassette and the meter but no
track title. Loop the finished pass with loop_261101.py.

Run: uv run --with pillow --with numpy python scripts/playlist/render_261101.py [--preview SECONDS] [--frame SECONDS]
"""

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from glitch_frankenstein import glitch, grain_field

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "runs/playlist_261101"  # render outputs (not tracked by Git)
HERE.mkdir(parents=True, exist_ok=True)
MUSIC = ROOT / "music/261101 frankenstein - the text"
IMAGE = ROOT / "runs/euno/drafts/2026-11-01_frankenstein_preface/frankenstein_preface_v4.png"

NAME_RE = re.compile(r"^\s*(\d+)\s*\.\s*(.+)$")
TRACK_FILES = sorted(MUSIC.glob("*.wav"), key=lambda p: int(NAME_RE.match(p.stem).group(1)))
TRACKS = [NAME_RE.match(p.stem).group(2).strip() for p in TRACK_FILES]

CHANNEL = "Background Tape"
TITLE = "Frankenstein - Mary Shelley"
W, H, FPS = 1920, 1080, 24
SR = 48000

# Chosen look (process_log.md, 2026-11-01).
EYES = (895, 428, 1040, 470)  # eye hollows in the v4 frame; torn light covers them so they don't read as holes
BASE = dict(seed=3, strength=0.5, gamma=0.9, eyes=EYES)  # chosen at 1.4; lifted so the hair and shoulders read
NOISE, LIFT = 14, 6
GRAIN_POOL = 48  # grain frames cycled at random; enough that no repeat is visible
GRAIN_HOLD = 2  # frames each grain stays (12 grain changes per second); halves the bitrate grain costs
CRF = 24
MAXRATE = "12M"  # YouTube suggests ~8 Mbps for 1080p24 and re-encodes anyway; keeps an hour near 5 GB

# Glitch bursts: alternate renders flicker in for a few frames, then the steady frame returns.
BURST_GAP = (3.0, 9.0)  # seconds between bursts
BURST_FRAMES = (2, 7)
ALT_COUNT = 14
ALT_STRENGTH = (0.6, 1.0)

# Overlay geometry is in design units; K scales it to output pixels (same as earlier BG TAPE renders).
K = 0.545  # earlier renders used 0.72; this panel is much smaller (0.45, then +10% twice)
SS = 4  # supersampling for static drawing
OH_U = 176
PAD_R = 26  # panel padding right of the meter
MARGIN_R, MARGIN_T = 16, 16
PANEL_ALPHA = 0  # no backing panel; the cassette and text sit straight on the frame

FONT_BOLD = "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"
FONT_REG = "/System/Library/Fonts/Supplemental/Courier New.ttf"

# Colours follow the glitch: cold grey-white light with muted red/blue fringes, on black.
INK = (12, 13, 16)  # reel hubs
BODY = (112, 118, 130)  # cassette body, the cold light on the face, dimmed
SHELL = (80, 86, 98)  # bottom trapezoid
WINDOW = (18, 20, 25)  # dark tape window
RIM = (150, 156, 168)
REEL = (160, 165, 175)
DARK = (8, 8, 10)
MID = (62, 66, 76)  # tape guide, holes
STITCH = (0, 0, 0)  # sutured seam across the body
TEXT = (150, 160, 178)
BAR_INK = (128, 140, 162)
LABEL = (90, 98, 114)
FRINGE = ((130, 72, 80), (70, 86, 150))  # muted red / blue copies, as in the RGB split
FRINGE_PX, FRINGE_ALPHA = 2, 0.5

# Cassette (design units inside the panel), drawn full size then scaled by CS beside the text.
CX, CY, CW, CH = 22, 22, 214, 136
CS = 0.7
REEL_R = 17
REEL_L = (CX + 66, CY + 60)
REEL_R_POS = (CX + CW - 66, CY + 60)

# Text / meter. With no title line the channel name sits higher and the meter follows it.
TX = CX + round(CW * CS) + 24
N_BARS, BAR_W, BAR_GAP, BAR_MAXH, BAR_MINH = 19, 9, 7, 30, 5
BAR_X, BAR_BASE = TX, CY + 92
BARS_W_U = N_BARS * (BAR_W + BAR_GAP) - BAR_GAP
PANEL_W_U = TX + BARS_W_U + PAD_R


def font(path, size):
    return ImageFont.truetype(path, round(size * K * SS))


def s(v):
    return int(round(v * K * SS))


def px(v):
    return int(round(v * K))


F_CHANNEL = (FONT_BOLD, 22)
F_SMALL = (FONT_REG, 12)


def draw_cassette(img):
    d = ImageDraw.Draw(img)
    body = (s(CX), s(CY), s(CX + CW), s(CY + CH))
    d.rounded_rectangle(body, radius=s(9), fill=BODY + (255,))
    # A sutured seam runs across the upper body: a thin line with cross-stitches.
    seam = [(CX + 10, CY + 24), (CX + 70, CY + 18), (CX + 140, CY + 26), (CX + CW - 10, CY + 20)]
    d.line([(s(x), s(y)) for x, y in seam], fill=STITCH + (255,), width=s(1.4))
    for (x0, y0), (x1, y1) in zip(seam, seam[1:]):
        for t in np.linspace(0.1, 0.9, 5):
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            d.line((s(x - 2), s(y - 5), s(x + 2), s(y + 5)), fill=STITCH + (255,), width=s(1.2))
    # Dark window band with a pale rim.
    wx0, wy0, wx1, wy1 = CX + 34, CY + 38, CX + CW - 34, CY + 82
    d.rounded_rectangle((s(wx0 - 3), s(wy0 - 3), s(wx1 + 3), s(wy1 + 3)), radius=s(25), fill=RIM + (255,))
    d.rounded_rectangle((s(wx0), s(wy0), s(wx1), s(wy1)), radius=s(22), fill=WINDOW + (255,))
    d.rectangle((s(CX + CW / 2 - 20), s(CY + 52), s(CX + CW / 2 + 20), s(CY + 68)), fill=MID + (255,))
    d.rectangle((s(CX + CW / 2 - 17), s(CY + 55), s(CX + CW / 2 + 17), s(CY + 65)), fill=DARK + (255,))
    # Bottom trapezoid with holes.
    by = CY + CH
    d.polygon([(s(CX + 40), s(by)), (s(CX + 50), s(by - 22)), (s(CX + CW - 50), s(by - 22)), (s(CX + CW - 40), s(by))],
              fill=SHELL + (255,))
    for hx in (CX + 70, CX + CW / 2 - 6, CX + CW / 2 + 6, CX + CW - 70):
        d.ellipse((s(hx - 3), s(by - 13), s(hx + 3), s(by - 7)), fill=DARK + (255,))


def reel_sprite(angle):
    size = px(REEL_R * 2 + 4) | 1
    img = Image.new("RGBA", (size * SS, size * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size * SS / 2
    r = s(REEL_R)
    d.ellipse((c - r, c - r, c + r, c + r), fill=REEL + (255,))
    d.ellipse((c - r * 0.82, c - r * 0.82, c + r * 0.82, c + r * 0.82), fill=MID + (255,))
    d.ellipse((c - r * 0.62, c - r * 0.62, c + r * 0.62, c + r * 0.62), fill=REEL + (255,))
    # Six hub teeth.
    for k in range(6):
        a = math.radians(angle + k * 60)
        x0, y0 = c + math.cos(a) * r * 0.22, c + math.sin(a) * r * 0.22
        x1, y1 = c + math.cos(a) * r * 0.6, c + math.sin(a) * r * 0.6
        d.line((x0, y0, x1, y1), fill=INK + (255,), width=s(2.2))
    d.ellipse((c - r * 0.24, c - r * 0.24, c + r * 0.24, c + r * 0.24), fill=INK + (255,))
    img = img.resize((size, size), Image.LANCZOS)
    return np.asarray(img).astype(np.float32) / 255.0


CASS_BOX = (px(CX) - 1, px(CY) - 1, px(CX + CW) + 1, px(CY + CH) + 1)  # full-size cassette crop, in panel pixels


def static_overlay():
    """Text layer (panel-size float RGBA) and the full-size cassette crop (float RGBA) to scale per frame."""
    full_w = max(PANEL_W_U, CX + CW + 2)
    cassette = Image.new("RGBA", (s(full_w), s(OH_U)), (0, 0, 0, 0))
    draw_cassette(cassette)
    cass = cassette.resize((px(full_w), px(OH_U)), Image.LANCZOS).crop(CASS_BOX)
    base = Image.new("RGBA", (s(PANEL_W_U), s(OH_U)), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    if PANEL_ALPHA:
        d.rounded_rectangle((0, 0, s(PANEL_W_U) - 1, s(OH_U) - 1), radius=s(14), fill=(255, 255, 255, PANEL_ALPHA))
    d.text((s(TX), s(CY + 24)), CHANNEL, font=font(*F_CHANNEL), fill=TEXT + (255,))
    d.text((s(TX), s(CY + 106)), "NOW PLAYING", font=font(*F_SMALL), fill=LABEL + (255,))
    panel = base.resize((px(PANEL_W_U), px(OH_U)), Image.LANCZOS)
    return np.asarray(panel).astype(np.float32) / 255.0, np.asarray(cass).astype(np.float32) / 255.0


def decode_mono(path):
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        check=True, capture_output=True,
    ).stdout
    return np.frombuffer(out, dtype=np.float32)


def band_levels(samples, n_frames):
    """Per-frame bar heights in [0, 1] from log-spaced FFT bands."""
    win = 4096
    hann = np.hanning(win).astype(np.float32)
    freqs = np.fft.rfftfreq(win, 1 / SR)
    edges = np.geomspace(50, 14000, N_BARS + 1)
    idx = [np.where((freqs >= edges[i]) & (freqs < edges[i + 1]))[0] for i in range(N_BARS)]
    pad = np.concatenate([np.zeros(win // 2, np.float32), samples, np.zeros(win, np.float32)])
    db = np.empty((n_frames, N_BARS), np.float32)
    for f in range(n_frames):
        start = int(f * SR / FPS)
        spec = np.abs(np.fft.rfft(pad[start:start + win] * hann))
        for b in range(N_BARS):
            db[f, b] = 20 * np.log10(np.mean(spec[idx[b]]) + 1e-6)
    top = np.percentile(db, 97, axis=0)
    lv = np.clip((db - (top - 34)) / 34, 0, 1) ** 1.4
    out = np.empty_like(lv)
    cur = np.zeros(N_BARS, np.float32)
    for f in range(n_frames):
        cur = np.where(lv[f] > cur, cur + (lv[f] - cur) * 0.7, cur * 0.82 + lv[f] * 0.18)
        out[f] = cur
    return out


def composite(dst, src, x, y):
    h, w = src.shape[:2]
    a = src[:, :, 3:4]
    region = dst[y:y + h, x:x + w]
    region[:, :, :3] = src[:, :, :3] * a + region[:, :, :3] * (1 - a)
    region[:, :, 3:4] = a + region[:, :, 3:4] * (1 - a)


def overlay_frame(static, sprites, levels, t):
    text, cass = static
    frame = text.copy()
    cass = cass.copy()
    step = len(sprites)
    a = int((t * 110) % 60 / 60 * step) % step  # 110 deg/s, sprites cover 60 deg
    for (rx, ry) in (REEL_L, REEL_R_POS):
        sp = sprites[a]
        half = sp.shape[0] // 2
        composite(cass, sp, px(rx) - half - CASS_BOX[0], px(ry) - half - CASS_BOX[1])
    cw, ch = round(cass.shape[1] * CS), round(cass.shape[0] * CS)
    small = np.asarray(Image.fromarray((cass * 255 + 0.5).astype(np.uint8), "RGBA").resize((cw, ch), Image.LANCZOS),
                       dtype=np.float32) / 255.0
    composite(frame, small, CASS_BOX[0], px(CY + CH / 2) - ch // 2)
    bw, step_x, base = px(BAR_W), px(BAR_W + BAR_GAP), px(BAR_BASE)
    for b, v in enumerate(levels):
        hgt = int(round(px(BAR_MINH) + (px(BAR_MAXH) - px(BAR_MINH)) * v))
        x0 = px(BAR_X) + b * step_x
        frame[base - hgt:base, x0:x0 + bw, :3] = np.array(BAR_INK) / 255.0
        frame[base - hgt:base, x0:x0 + bw, 3] = 1.0
    return frame


def burst_schedule(n_frames, rng):
    """Frame index -> alternate glitch index (or -1 for the steady frame)."""
    sched = np.full(n_frames, -1, np.int16)
    f = int(rng.uniform(*BURST_GAP) * FPS)
    while f < n_frames:
        for k in range(int(rng.integers(BURST_FRAMES[0], BURST_FRAMES[1] + 1))):
            if f + k < n_frames and rng.random() < 0.8:  # a dropped frame shows the steady image mid-burst
                sched[f + k] = rng.integers(ALT_COUNT)
        f += int(rng.uniform(*BURST_GAP) * FPS)
    return sched


def compose(img, ov, grain, ox, oy):
    """Image (float RGB 0-255) + panel, then grain over everything so the panel sits in the same film."""
    frame = img.copy()
    h, w = ov.shape[:2]
    region = frame[oy:oy + h, ox:ox + w]
    # Muted red/blue copies offset sideways under the panel, like the glitch's RGB split.
    for col, dx in zip(FRINGE, (-FRINGE_PX, FRINGE_PX)):
        fa = np.roll(ov[:, :, 3:4], dx, axis=1) * FRINGE_ALPHA
        region[:] = np.array(col, np.float32) * fa + region * (1 - fa)
    a = ov[:, :, 3:4]
    region[:] = ov[:, :, :3] * 255 * a + region * (1 - a)
    return (frame + grain).clip(0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", type=float, help="render only the first N seconds")
    ap.add_argument("--frame", type=float, help="write a single PNG still at this time")
    ap.add_argument("--out", default=str(HERE / "frankenstein_261101.mp4"))
    args = ap.parse_args()
    if Path(args.out).exists() and args.frame is None:
        sys.exit(f"refusing to overwrite {args.out}; pass a new --out")

    durations = [float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True).stdout) for p in TRACK_FILES]
    starts = np.concatenate([[0], np.cumsum(durations)])
    total = starts[-1]

    src = Image.open(IMAGE).convert("RGB")
    assert src.size == (W, H), src.size
    rng = np.random.default_rng(1101)
    base = np.asarray(glitch(src, **BASE), dtype=np.float32) + LIFT
    alts = [np.asarray(glitch(src, seed=100 + k, strength=float(rng.uniform(*ALT_STRENGTH)), gamma=BASE["gamma"], eyes=EYES),
                       dtype=np.float32) + LIFT for k in range(ALT_COUNT)]
    grains = [grain_field(rng, H, W, NOISE)[..., None] for _ in range(GRAIN_POOL)]
    sprites = [reel_sprite(d) for d in range(0, 60, 2)]
    static = static_overlay()
    ox, oy = W - static[0].shape[1] - MARGIN_R, MARGIN_T

    if args.frame is not None:
        i = int(np.searchsorted(starts, args.frame, side="right") - 1)
        lv = band_levels(decode_mono(TRACK_FILES[i]), int(durations[i] * FPS))
        fi = min(int((args.frame - starts[i]) * FPS), len(lv) - 1)
        out = HERE / f"still_{args.frame:.0f}s.png"
        Image.fromarray(compose(base, overlay_frame(static, sprites, lv[fi], args.frame), grains[0], ox, oy)).save(out)
        print(out)
        return

    limit = args.preview or total
    n_frames = int(math.ceil(limit * FPS))
    sched = burst_schedule(n_frames, rng)

    lines, meta = [], [";FFMETADATA1", f"title={TITLE}"]
    for i, t in enumerate(TRACKS):
        sec = int(starts[i])
        stamp = f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}" if total >= 3600 else f"{sec // 60:02d}:{sec % 60:02d}"
        lines.append(f"{stamp} {i + 1:02d}. {t}")
        meta += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(starts[i] * 1000)}",
                 f"END={int(starts[i + 1] * 1000)}", f"title={i + 1:02d}. {t}"]
    (HERE / "tracklist.txt").write_text("\n".join(lines) + "\n")
    (HERE / "chapters.txt").write_text("\n".join(meta) + "\n")
    (HERE / "concat.txt").write_text("".join(f"file '{str(p).replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'\n" for p in TRACK_FILES))
    (HERE / "tracks.json").write_text(json.dumps(
        [{"index": i + 1, "title": t, "file": str(p), "start": round(float(starts[i]), 3), "duration": d}
         for i, (t, p, d) in enumerate(zip(TRACKS, TRACK_FILES, durations))], indent=2, ensure_ascii=False))

    cmd = [
        "ffmpeg", "-y", "-v", "error", "-stats",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-framerate", str(FPS), "-i", "-",
        "-f", "concat", "-safe", "0", "-i", str(HERE / "concat.txt"),
        "-i", str(HERE / "chapters.txt"),
        "-map", "0:v", "-map", "1:a", "-map_metadata", "2", "-map_chapters", "2",
        "-c:v", "libx264", "-preset", "medium", "-crf", str(CRF), "-maxrate", MAXRATE, "-bufsize", "24M", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "320k",
        "-t", f"{limit:.3f}", "-movflags", "+faststart", args.out,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    grain = grains[0]
    frame_no = 0
    for i, p in enumerate(TRACK_FILES):
        if frame_no >= n_frames:
            break
        end_frame = min(int(round(starts[i + 1] * FPS)), n_frames)
        lv = band_levels(decode_mono(p), int(durations[i] * FPS) + 2)
        print(f"track {i + 1:02d} {TRACKS[i]}: {end_frame - frame_no} frames", file=sys.stderr)
        for f in range(frame_no, end_frame):
            if f % GRAIN_HOLD == 0:
                grain = grains[rng.integers(GRAIN_POOL)]
            img = base if sched[f] < 0 else alts[sched[f]]
            local = min(max(int(round((f / FPS - starts[i]) * FPS)), 0), len(lv) - 1)
            ov = overlay_frame(static, sprites, lv[local], f / FPS)
            proc.stdin.write(compose(img, ov, grain, ox, oy).tobytes())
        frame_no = end_frame
    proc.stdin.close()
    sys.exit(proc.wait())


if __name__ == "__main__":
    main()
