"""Make the three-loop 261101 video from the finished single-pass render.

The video stream is copied three times without re-encoding; the audio is the original WAVs
played three times, encoded to AAC once. Chapters and the tracklist cover all passes.

Run: python3 scripts/playlist/loop_261101.py
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "runs/playlist_261101"
SRC = HERE / "frankenstein_261101.mp4"
OUT = HERE / "frankenstein_261101_3loops.mp4"
LOOPS = 3


def stamp(sec, hours):
    sec = int(sec)
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}" if hours else f"{sec // 60:02d}:{sec % 60:02d}"


def quote(p):
    return "file '" + str(p).replace("'", "'\\''") + "'\n"


def main():
    if OUT.exists():
        sys.exit(f"refusing to overwrite {OUT}")
    tracks = json.loads((HERE / "tracks.json").read_text())
    one = sum(t["duration"] for t in tracks)
    total = one * LOOPS

    (HERE / "concat_video_3loops.txt").write_text(quote(SRC) * LOOPS)
    (HERE / "concat_audio_3loops.txt").write_text("".join(quote(t["file"]) for t in tracks) * LOOPS)

    lines, meta = [], [";FFMETADATA1", "title=Frankenstein - Mary Shelley"]
    for loop in range(LOOPS):
        for t in tracks:
            start = loop * one + t["start"]
            lines.append(f"{stamp(start, total >= 3600)} {t['index']:02d}. {t['title']}")
            meta += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(start * 1000)}",
                     f"END={int((start + t['duration']) * 1000)}", f"title={t['index']:02d}. {t['title']}"]
    (HERE / "tracklist_3loops.txt").write_text("\n".join(lines) + "\n")
    (HERE / "chapters_3loops.txt").write_text("\n".join(meta) + "\n")

    subprocess.run([
        "ffmpeg", "-v", "error", "-stats",
        "-f", "concat", "-safe", "0", "-i", str(HERE / "concat_video_3loops.txt"),
        "-f", "concat", "-safe", "0", "-i", str(HERE / "concat_audio_3loops.txt"),
        "-i", str(HERE / "chapters_3loops.txt"),
        "-map", "0:v", "-map", "1:a", "-map_metadata", "2", "-map_chapters", "2",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
        "-t", f"{total:.3f}", "-movflags", "+faststart", str(OUT),
    ], check=True)
    print(OUT)


if __name__ == "__main__":
    main()
