#!/usr/bin/env python3
"""Create timestamped UTF-8 transcript files with faster-whisper."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from faster_whisper import WhisperModel


def timestamp(seconds: float) -> str:
    total = max(0, int(round(seconds)))
    return f"{total // 60:02d}:{total % 60:02d}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--model", default="small")
    parser.add_argument("--language", default="ko")
    parser.add_argument("--initial-prompt", default="")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments_iter, info = model.transcribe(
        str(args.audio),
        language=args.language,
        beam_size=5,
        best_of=5,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 450},
        condition_on_previous_text=True,
        initial_prompt=args.initial_prompt or None,
    )

    rows = []
    for index, segment in enumerate(segments_iter, start=1):
        text = segment.text.strip()
        if not text:
            continue
        rows.append(
            {
                "index": index,
                "start": round(segment.start, 3),
                "end": round(segment.end, 3),
                "start_text": timestamp(segment.start),
                "end_text": timestamp(segment.end),
                "text": text,
                "avg_logprob": getattr(segment, "avg_logprob", None),
                "no_speech_prob": getattr(segment, "no_speech_prob", None),
            }
        )

    payload = {
        "model": args.model,
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "segments": rows,
    }
    (args.output_dir / "transcript.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (args.output_dir / "transcript.txt").write_text(
        "\n".join(
            f"[{row['start_text']}-{row['end_text']}] {row['text']}" for row in rows
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "segments": len(rows),
                "duration": info.duration,
                "language": info.language,
                "language_probability": info.language_probability,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
