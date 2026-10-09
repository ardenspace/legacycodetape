#!/usr/bin/env python3
"""Small, dependency-free client for the existing local Gemma service."""
import argparse
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def request_json(url, *, payload=None, timeout=15):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def build_messages(brief, count, mode="image", genre=None, vocals="instrumental",
                   lyrics=False, lyrics_language=None):
    if mode == "music":
        context = {"brief": brief, "genre": genre, "vocals": "vocals" if lyrics else vocals,
                   "include_lyrics": lyrics}
        if lyrics:
            context["lyrics_language"] = lyrics_language or "Follow the brief; otherwise Korean"
        system = (
            "You write situation-based Suno music prompts for Legacy Code Tape, a playlist channel "
            "for people who build software, electronics and machines. Return only a JSON object "
            f"with a candidates array containing exactly {count} entries. "
            "Each entry has name (short Korean situation label), situation (one Korean sentence "
            "describing the everyday moment and musical mood), and suno_prompt (copyable English "
            "music direction, roughly 70-110 words). These labels are not song lyrics. "
            "Connect each situation to concrete musical choices: genre, approximate BPM, instruments, "
            "rhythm, texture, energy, arrangement and transitions. Offer distinct but coherent variations; "
            "do not merely rename the same music. The prompt must stand alone when pasted into Suno. "
            "Honor the requested genre and brief. If genre is unspecified, choose genres fitting the brief. "
            "Never assume lo-fi, jazz, slow tempo, vinyl noise, night-time, or sleepy moods by default. "
            "Focus music can be rhythmic and energetic when requested. Use only relevant exclusions. "
            "For instrumental, explicitly request no vocals or spoken words. For vocals, describe vocal "
            "character fitting the brief. User details in the brief take precedence for creative direction. "
            "Do not claim to generate audio or guarantee exact musical results."
        )
        if lyrics:
            system += (
                " Also include lyrics (a nonempty string) in each candidate. Write original, singable "
                "lyrics in lyrics_language, matching the brief and each candidate's musical direction. "
                "Use natural phrasing, concrete imagery, a memorable chorus, and a coherent emotional arc. "
                "Use section labels such as [Verse 1], [Pre-Chorus], [Chorus], [Verse 2], [Bridge], "
                "and [Final Chorus] as appropriate; honor a requested structure or length. Write repeated "
                "choruses in full. Keep actual sung words exclusively in lyrics, separate from the English "
                "suno_prompt, which describes vocal style and language. Do not add translations or commentary "
                "inside lyrics unless requested. Encode lyric line breaks as JSON newline escapes. "
                "Do not force coding themes or fantasy lore when the brief asks for other subjects."
            )
        else:
            system += " Do not write or include lyrics; this request is for music direction only."
        return [{"role": "system", "content": system},
                {"role": "user", "content": json.dumps(context, ensure_ascii=False)}]
    style = json.loads((ROOT / "config/style.json").read_text())
    references = json.loads((ROOT / "references/catalog.json").read_text())
    # Explicit text context. Merely storing image files does not send their pixels.
    context = {"style": style, "reference_notes": references, "brief": brief}
    system = (
        "You write image-generation prompts for Legacy Code Tape. Treat supplied material as creative context. "
        "Follow the style and user brief, and offer distinct compositions without imposing a channel layout. "
        "Reference images are NOT attached: only their written notes are available. "
        "Return only a JSON object with a candidates array containing exactly " + str(count) + " entries. "
        "Each entry has name (Korean), image_prompt (detailed English ready for an image generator), "
        "animation_notes (Korean), and reference_ids (array of reference IDs used). "
        "Do not generate an image or title, and do not promise identical characters across generations."
    )
    return [{"role": "system", "content": system},
            {"role": "user", "content": json.dumps(context, ensure_ascii=False)}]


def validate_result(result, count, mode="image", lyrics=False):
    if not isinstance(result, dict) or not isinstance(result.get("candidates"), list):
        raise ValueError("응답에 candidates 배열이 없습니다.")
    if len(result["candidates"]) != count:
        raise ValueError("요청한 후보 수와 응답이 다릅니다.")
    for item in result["candidates"]:
        if not isinstance(item, dict):
            raise ValueError("후보가 객체가 아닙니다.")
        fields = ("name", "situation", "suno_prompt") if mode == "music" else (
            "name", "image_prompt", "animation_notes")
        if mode == "music" and lyrics:
            fields += ("lyrics",)
        elif "lyrics" in item:
            raise ValueError("요청하지 않은 가사가 포함되어 있습니다.")
        for field in fields:
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"후보의 {field}가 비어 있습니다.")
        if mode == "image" and (not isinstance(item.get("reference_ids"), list) or not all(
            isinstance(ref, str) for ref in item["reference_ids"]
        )):
            raise ValueError("reference_ids는 문자열 배열이어야 합니다.")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("image", "music"), default="image")
    parser.add_argument("--genre", help="Music genre; omitted means chosen from the brief")
    parser.add_argument("--vocals", choices=("instrumental", "vocals"), default=None)
    parser.add_argument("--lyrics", action="store_true", help="Generate lyrics as well as music direction (implies vocals)")
    parser.add_argument("--lyrics-language", help="Lyric language, e.g. Korean, Japanese, English; requires --lyrics")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--brief")
    source.add_argument("--brief-file", type=Path)
    parser.add_argument("--count", type=int, choices=range(1, 7), default=3)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout", type=float, default=600)
    args = parser.parse_args()
    if args.mode != "music" and (args.genre is not None or args.vocals is not None
                                 or args.lyrics or args.lyrics_language is not None):
        parser.error("음악·가사 옵션은 --mode music에서 사용하세요.")
    if args.lyrics_language is not None and (not args.lyrics or not args.lyrics_language.strip()):
        parser.error("--lyrics-language는 --lyrics와 함께 비어 있지 않은 언어를 지정하세요.")
    if args.lyrics and args.vocals == "instrumental":
        parser.error("--lyrics와 --vocals instrumental은 함께 사용할 수 없습니다.")
    brief = args.brief if args.brief is not None else args.brief_file.read_text()
    if not brief.strip():
        parser.error("장면 또는 음악 상황 설명을 입력하세요.")
    messages = build_messages(brief, args.count, args.mode, args.genre,
                              args.vocals or "instrumental", args.lyrics, args.lyrics_language)
    if args.dry_run:
        print(json.dumps(messages, ensure_ascii=False, indent=2))
        return
    base = os.environ.get("GEMMA_BASE_URL", "http://127.0.0.1:8080/v1").rstrip("/")
    model = os.environ.get("GEMMA_MODEL")
    if not model:
        models = request_json(base + "/models").get("data", [])
        if len(models) != 1:
            raise ValueError("모델이 없거나 여러 개입니다. GEMMA_MODEL을 지정하세요.")
        model = models[0]["id"]
    run = ROOT / "runs" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"-{time.time_ns() % 1000000000:09d}")
    run.mkdir(parents=True)
    payload = {"model": model, "messages": messages, "temperature": 0.7,
               "max_tokens": max(4000, args.count * (3000 if args.lyrics else 1000)),
               "response_format": {"type": "json_object"}}
    (run / "request.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Gemma 생성 중 · {model}\n기록: {run}", flush=True)
    response = request_json(base + "/chat/completions", payload=payload, timeout=args.timeout)
    (run / "response.json").write_text(json.dumps(response, ensure_ascii=False, indent=2))
    choice = response["choices"][0]
    if choice.get("finish_reason") != "stop":
        raise ValueError("응답이 정상 종료되지 않았습니다. 저장된 response.json을 확인하세요.")
    result = validate_result(json.loads(choice["message"]["content"]), args.count, args.mode, args.lyrics)
    (run / "candidates.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    for i, candidate in enumerate(result["candidates"], 1):
        prompt = candidate["suno_prompt" if args.mode == "music" else "image_prompt"]
        (run / f"prompt-{i:02d}.txt").write_text(prompt + "\n")
        print(f"{i}. {candidate['name']}")
        if args.mode == "music":
            print(f"{candidate['situation']}\n\n{prompt}\n")
        if args.lyrics:
            (run / f"lyrics-{i:02d}.txt").write_text(candidate["lyrics"] + "\n")
            print(f"가사:\n{candidate['lyrics']}\n")
    print(f"완료: {run / 'candidates.json'}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, IndexError, TypeError, urllib.error.URLError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        sys.exit(1)
