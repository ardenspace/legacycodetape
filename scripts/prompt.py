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


def build_messages(brief, count):
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


def validate_result(result, count):
    if not isinstance(result, dict) or not isinstance(result.get("candidates"), list):
        raise ValueError("응답에 candidates 배열이 없습니다.")
    if len(result["candidates"]) != count:
        raise ValueError("요청한 후보 수와 응답이 다릅니다.")
    for item in result["candidates"]:
        if not isinstance(item, dict):
            raise ValueError("후보가 객체가 아닙니다.")
        for field in ("name", "image_prompt", "animation_notes"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"후보의 {field}가 비어 있습니다.")
        if not isinstance(item.get("reference_ids"), list) or not all(
            isinstance(ref, str) for ref in item["reference_ids"]
        ):
            raise ValueError("reference_ids는 문자열 배열이어야 합니다.")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--brief")
    source.add_argument("--brief-file", type=Path)
    parser.add_argument("--count", type=int, choices=range(1, 4), default=3)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout", type=float, default=600)
    args = parser.parse_args()
    brief = args.brief if args.brief is not None else args.brief_file.read_text()
    if not brief.strip():
        parser.error("장면 설명을 입력하세요.")
    messages = build_messages(brief, args.count)
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
               "max_tokens": 4000, "response_format": {"type": "json_object"}}
    (run / "request.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Gemma 생성 중 · {model}\n기록: {run}", flush=True)
    response = request_json(base + "/chat/completions", payload=payload, timeout=args.timeout)
    (run / "response.json").write_text(json.dumps(response, ensure_ascii=False, indent=2))
    choice = response["choices"][0]
    if choice.get("finish_reason") != "stop":
        raise ValueError("응답이 정상 종료되지 않았습니다. 저장된 response.json을 확인하세요.")
    result = validate_result(json.loads(choice["message"]["content"]), args.count)
    (run / "candidates.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    for i, candidate in enumerate(result["candidates"], 1):
        (run / f"prompt-{i:02d}.txt").write_text(candidate["image_prompt"] + "\n")
        print(f"{i}. {candidate['name']}")
    print(f"완료: {run / 'candidates.json'}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, IndexError, TypeError, urllib.error.URLError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        sys.exit(1)
