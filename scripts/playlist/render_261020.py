"""Render the 261020 BG Tape UK garage playlist video (star beanie).

Run: uv run --with pillow --with numpy python scripts/playlist/render_261020.py [--preview SECONDS] [--frame SECONDS]
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

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "runs/playlist_261020"  # render outputs (not tracked by Git)
HERE.mkdir(parents=True, exist_ok=True)
MUSIC = ROOT / "music/261020 uk garage"
IMAGE = ROOT / "runs/euno/drafts/2026-10-21_fisheye_beanie/fisheye_beanie_v2.png"

# Track order is the number before the title in each file name ("1. Title.wav";
# tolerates a misplaced space such as "8 .Title.wav").
NAME_RE = re.compile(r"^\s*(\d+)\s*\.\s*(.+)$")
TRACK_FILES = sorted(MUSIC.glob("*.wav"), key=lambda p: int(NAME_RE.match(p.stem).group(1)))
TRACKS = [NAME_RE.match(p.stem).group(2).strip() for p in TRACK_FILES]

CHANNEL = "BG TAPE"
W, H, FPS = 1920, 1080, 24
SR = 48000

# Overlay geometry is in design units; K scales it to output pixels.
K = 0.72
SS = 4  # supersampling for static drawing
OH_U = 176
PANEL_W_U = 650  # fixed panel width; fits "01 / Half Asleep, Wide Awake" on one line
PAD_R = 26  # panel padding right of the text
LINE_H = 24  # extra height per wrapped title line
MARGIN_R, MARGIN_T = 0, 16  # panel touches the right edge; its padding keeps text off the edge
PANEL_ALPHA = 166  # 0 = no backing panel; 236 was the earlier white panel

FONT_BOLD = "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"
FONT_REG = "/System/Library/Fonts/Supplemental/Courier New.ttf"

# Overlay colour follows the star beanie: charcoal knit (sampled median RGB 50, 46, 46)
# with its dusty-pink stars (sampled RGB 183, 164, 165).
INK = (50, 46, 46)
GREY = (84, 78, 78)
LIGHT = (150, 140, 140)
DARK = (30, 28, 28)  # tape window and bottom shell
MID = (96, 90, 90)  # screws, tape holes
STAR = (186, 166, 167)
RIB = (60, 56, 56)  # faint knit ribs on the cassette body
BAR_INK = (164, 136, 139)  # star colour, deepened so the meter reads on the white panel

# Cassette (design units inside the panel).
CX, CY, CW, CH = 22, 22, 214, 136
REEL_R = 17
REEL_L = (CX + 66, CY + 60)
REEL_R_POS = (CX + CW - 66, CY + 60)

# Text / meter.
TX = CX + CW + 30
N_BARS, BAR_W, BAR_GAP, BAR_MAXH, BAR_MINH = 19, 9, 7, 30, 5
BAR_X, BAR_BASE = TX, CY + 106


def font(path, size):
    return ImageFont.truetype(path, round(size * K * SS))


def s(v):
    return int(round(v * K * SS))


def px(v):
    return int(round(v * K))


F_CHANNEL = (FONT_BOLD, 22)
F_TITLE = (FONT_REG, 20)
F_SMALL = (FONT_REG, 12)
BARS_W_U = N_BARS * (BAR_W + BAR_GAP) - BAR_GAP


def text_w(spec, text):
    return font(*spec).getlength(text) / (K * SS)


def title_lines(index, title):
    """Wrap '01 / title' at word boundaries; continuation lines align after the prefix."""
    prefix = f"{index:02d} / "
    max_w = PANEL_W_U - TX - PAD_R
    indent = " " * len(prefix)  # monospace font
    lines, cur = [], prefix
    for word in title.split():
        trial = cur + word if cur.endswith(" ") else f"{cur} {word}"
        if text_w(F_TITLE, trial) <= max_w or cur.strip() in ("", prefix.strip()):
            cur = trial
        else:
            lines.append(cur)
            cur = indent + word
    lines.append(cur)
    return lines


def panel_h(index, title):
    return OH_U + (len(title_lines(index, title)) - 1) * LINE_H


def star(cx, cy, r, rot=0.0):
    """Five-point star polygon in supersampled pixels; rot in degrees."""
    pts = []
    for k in range(10):
        a = math.radians(-90 + rot + k * 36)
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((s(cx + math.cos(a) * rr), s(cy + math.sin(a) * rr)))
    return pts


def draw_cassette(img):
    d = ImageDraw.Draw(img)
    # Body: charcoal knit with faint vertical ribs.
    body = (s(CX), s(CY), s(CX + CW), s(CY + CH))
    d.rounded_rectangle(body, radius=s(9), fill=INK + (255,))
    for rx in range(CX + 6, CX + CW - 3, 5):
        d.line((s(rx), s(CY + 3), s(rx), s(CY + CH - 3)), fill=RIB + (255,), width=s(1))
    # Stars placed like the beanie: a big one top-right, smaller ones on the left and right edge.
    # The window band is drawn afterwards, so the big star tucks under it like the knit pattern.
    for cx, cy, r, rot in ((CX + 166, CY + 29, 22, -10), (CX + 19, CY + 40, 12, 8),
                           (CX + CW - 13, CY + 112, 9, -6), (CX + 24, CY + 116, 7, 12)):
        d.polygon(star(cx, cy, r, rot), fill=STAR + (255,))
    # Window band with reels sits straight on the body; no sticker label.
    wx0, wy0, wx1, wy1 = CX + 34, CY + 38, CX + CW - 34, CY + 82
    d.rounded_rectangle((s(wx0 - 3), s(wy0 - 3), s(wx1 + 3), s(wy1 + 3)), radius=s(25), fill=(255, 255, 255, 255))
    d.rounded_rectangle((s(wx0), s(wy0), s(wx1), s(wy1)), radius=s(22), fill=INK + (255,))
    d.rectangle((s(CX + CW / 2 - 20), s(CY + 52), s(CX + CW / 2 + 20), s(CY + 68)), fill=MID + (255,))
    d.rectangle((s(CX + CW / 2 - 17), s(CY + 55), s(CX + CW / 2 + 17), s(CY + 65)), fill=DARK + (255,))
    # Bottom trapezoid with holes.
    by = CY + CH
    d.polygon([(s(CX + 40), s(by)), (s(CX + 50), s(by - 22)), (s(CX + CW - 50), s(by - 22)), (s(CX + CW - 40), s(by))],
              fill=DARK + (255,))
    for hx in (CX + 70, CX + CW / 2 - 6, CX + CW / 2 + 6, CX + CW - 70):
        d.ellipse((s(hx - 3), s(by - 13), s(hx + 3), s(by - 7)), fill=LIGHT + (255,))


def reel_sprite(angle):
    size = px(REEL_R * 2 + 4) | 1
    img = Image.new("RGBA", (size * SS, size * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size * SS / 2
    r = s(REEL_R)
    d.ellipse((c - r, c - r, c + r, c + r), fill=(235, 235, 235, 255))
    d.ellipse((c - r * 0.82, c - r * 0.82, c + r * 0.82, c + r * 0.82), fill=MID + (255,))
    d.ellipse((c - r * 0.62, c - r * 0.62, c + r * 0.62, c + r * 0.62), fill=(240, 240, 240, 255))
    # Six hub teeth.
    for k in range(6):
        a = math.radians(angle + k * 60)
        x0, y0 = c + math.cos(a) * r * 0.22, c + math.sin(a) * r * 0.22
        x1, y1 = c + math.cos(a) * r * 0.6, c + math.sin(a) * r * 0.6
        d.line((x0, y0, x1, y1), fill=INK + (255,), width=s(2.2))
    d.ellipse((c - r * 0.24, c - r * 0.24, c + r * 0.24, c + r * 0.24), fill=INK + (255,))
    img = img.resize((size, size), Image.LANCZOS)
    return np.asarray(img).astype(np.float32) / 255.0


def static_overlay(index, title, canvas_h):
    """Fixed-width panel, top-aligned in the canvas; long titles wrap and grow it downward.

    Returns the canvas as float RGBA plus pixel y offsets for the reels and the meter.
    """
    lines = title_lines(index, title)
    extra = (len(lines) - 1) * LINE_H
    h_u = OH_U + extra
    base = Image.new("RGBA", (s(PANEL_W_U), s(h_u)), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    if PANEL_ALPHA:
        d.rounded_rectangle((0, 0, s(PANEL_W_U) - 1, s(h_u) - 1), radius=s(14), fill=(255, 255, 255, PANEL_ALPHA))
    cassette = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw_cassette(cassette)
    base.alpha_composite(cassette, (0, s(extra / 2)))  # keep the cassette vertically centred
    items = [(CY + 14, CHANNEL, F_CHANNEL, INK)]
    items += [(CY + 46 + k * LINE_H, line, F_TITLE, GREY) for k, line in enumerate(lines)]
    items += [(CY + 116 + extra, "NOW PLAYING", F_SMALL, LIGHT)]
    for y, txt, spec, col in items:
        d.text((s(TX), s(y)), txt, font=font(*spec), fill=col + (255,))
    panel = base.resize((px(PANEL_W_U), px(h_u)), Image.LANCZOS)
    canvas = Image.new("RGBA", (px(PANEL_W_U), canvas_h), (0, 0, 0, 0))
    y0 = 0
    canvas.paste(panel, (0, y0))
    return np.asarray(canvas).astype(np.float32) / 255.0, y0 + px(extra / 2), y0 + px(extra)


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


def background():
    img = Image.open(IMAGE).convert("RGB")
    assert img.size == (W, H), img.size  # already a 1920x1080 frame
    return img


def overlay_frame(static, sprites, levels, t):
    static, reel_dy, bar_dy = static
    frame = static.copy()
    step = len(sprites)
    a = int((t * 110) % 60 / 60 * step) % step  # 110 deg/s, sprites cover 60 deg
    for (rx, ry) in (REEL_L, REEL_R_POS):
        sp = sprites[a]
        half = sp.shape[0] // 2
        composite(frame, sp, px(rx) - half, reel_dy + px(ry) - half)
    bw, step_x, base = px(BAR_W), px(BAR_W + BAR_GAP), bar_dy + px(BAR_BASE)
    for b, v in enumerate(levels):
        hgt = int(round(px(BAR_MINH) + (px(BAR_MAXH) - px(BAR_MINH)) * v))
        x0 = px(BAR_X) + b * step_x
        frame[base - hgt:base, x0:x0 + bw, :3] = np.array(BAR_INK) / 255.0
        frame[base - hgt:base, x0:x0 + bw, 3] = 1.0
    return (frame * 255 + 0.5).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", type=float, help="render only the first N seconds")
    ap.add_argument("--frame", type=float, help="write a single PNG still at this time")
    ap.add_argument("--title", help="with --frame: override the track title (layout test)")
    ap.add_argument("--out", default=str(HERE / "bg_tape_261020.mp4"))
    args = ap.parse_args()
    if Path(args.out).exists() and args.frame is None:
        sys.exit(f"refusing to overwrite {args.out}; pass a new --out")

    paths = TRACK_FILES
    for p in paths:
        if not p.exists():
            sys.exit(f"missing: {p}")
    durations = [float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True).stdout) for p in paths]
    starts = np.concatenate([[0], np.cumsum(durations)])
    total = starts[-1]

    bg = background()
    bg_path = HERE / "background.png"
    bg.save(bg_path)
    sprites = [reel_sprite(d) for d in range(0, 60, 2)]
    ow = px(PANEL_W_U)
    oh = max(px(panel_h(i + 1, t)) for i, t in enumerate(TRACKS))
    ox, oy = W - ow - MARGIN_R, MARGIN_T

    if args.frame is not None:
        i = int(np.searchsorted(starts, args.frame, side="right") - 1)
        title = args.title or TRACKS[i]
        st = static_overlay(i + 1, title, px(panel_h(i + 1, title)))
        lv = band_levels(decode_mono(paths[i]), int((durations[i]) * FPS))
        fi = min(int((args.frame - starts[i]) * FPS), len(lv) - 1)
        ov = Image.fromarray(overlay_frame(st, sprites, lv[fi], args.frame), "RGBA")
        frame = bg.convert("RGBA")
        frame.alpha_composite(ov, (ox, oy))
        out = HERE / (f"still_{args.frame:.0f}s" + ("_title" if args.title else "") + ".png")
        frame.convert("RGB").save(out)
        print(out)
        return

    limit = args.preview or total
    n_total = int(math.ceil(limit * FPS))

    # Chapters + tracklist.
    lines, meta = [], [";FFMETADATA1", f"title={CHANNEL} 261020"]
    for i, t in enumerate(TRACKS):
        sec = int(starts[i])
        stamp = f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}" if total >= 3600 else f"{sec // 60:02d}:{sec % 60:02d}"
        lines.append(f"{stamp} {i + 1:02d}. {t}")
        meta += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(starts[i] * 1000)}",
                 f"END={int(starts[i + 1] * 1000)}", f"title={i + 1:02d}. {t}"]
    (HERE / "tracklist.txt").write_text("\n".join(lines) + "\n")
    (HERE / "chapters.txt").write_text("\n".join(meta) + "\n")
    (HERE / "concat.txt").write_text("".join(f"file '{str(p).replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'\n" for p in paths))
    (HERE / "tracks.json").write_text(json.dumps(
        [{"index": i + 1, "title": t, "file": str(p), "start": round(float(starts[i]), 3), "duration": d}
         for i, (t, p, d) in enumerate(zip(TRACKS, paths, durations))], indent=2, ensure_ascii=False))

    cmd = [
        "ffmpeg", "-y", "-v", "error", "-stats",
        "-loop", "1", "-framerate", str(FPS), "-i", str(bg_path),
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{ow}x{oh}", "-framerate", str(FPS), "-i", "-",
        "-f", "concat", "-safe", "0", "-i", str(HERE / "concat.txt"),
        "-i", str(HERE / "chapters.txt"),
        "-filter_complex", f"[0:v][1:v]overlay={ox}:{oy}:shortest=1,format=yuv420p[v]",
        "-map", "[v]", "-map", "2:a", "-map_metadata", "3", "-map_chapters", "3",
        "-c:v", "libx264", "-preset", "medium", "-tune", "stillimage", "-crf", "18",
        "-r", str(FPS), "-c:a", "aac", "-b:a", "320k",
        "-t", f"{limit:.3f}", "-movflags", "+faststart", args.out,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    frame_no = 0
    for i, p in enumerate(paths):
        if frame_no >= n_total:
            break
        st = static_overlay(i + 1, TRACKS[i], oh)
        end_frame = min(int(round(starts[i + 1] * FPS)), n_total)
        count = end_frame - frame_no
        lv = band_levels(decode_mono(p), int(durations[i] * FPS) + 2)
        print(f"track {i + 1:02d} {TRACKS[i]}: {count} frames", file=sys.stderr)
        for k in range(count):
            t = (frame_no + k) / FPS
            local = min(int(round((t - starts[i]) * FPS)), len(lv) - 1)
            proc.stdin.write(overlay_frame(st, sprites, lv[max(local, 0)], t).tobytes())
        frame_no = end_frame
    proc.stdin.close()
    sys.exit(proc.wait())


if __name__ == "__main__":
    main()
