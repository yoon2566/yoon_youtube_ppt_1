#!/usr/bin/env python3
"""Validate scene evidence, 1080p renders, and PPTX structure."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import zipfile
from pathlib import Path

REQUIRED = {"id", "section", "title", "timestamp", "seconds", "frame", "evidence"}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        if handle.read(8) != PNG_SIGNATURE:
            raise ValueError("not a PNG")
        length = struct.unpack(">I", handle.read(4))[0]
        kind = handle.read(4)
        if kind != b"IHDR" or length < 8:
            raise ValueError("missing PNG IHDR")
        return struct.unpack(">II", handle.read(8))


def parse_timestamp(value: str) -> int:
    match = re.fullmatch(r"(\d+):([0-5]\d)", value)
    if not match:
        raise ValueError("expected MM:SS")
    return int(match.group(1)) * 60 + int(match.group(2))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene-plan", required=True, type=Path)
    parser.add_argument("--frames", required=True, type=Path)
    parser.add_argument("--pptx", required=True, type=Path)
    parser.add_argument("--renders", required=True, type=Path)
    parser.add_argument("--verification", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    scenes = json.loads(args.scene_plan.read_text(encoding="utf-8"))
    if isinstance(scenes, dict):
        scenes = scenes.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise SystemExit("scene plan must be a non-empty JSON array")

    expected_ids = list(range(1, len(scenes) + 1))
    actual_ids = [scene.get("id") for scene in scenes]
    if actual_ids != expected_ids:
        errors.append("scene ids must be consecutive from 1")

    previous_seconds = -1
    frame_dimensions: dict[str, list[int]] = {}
    for position, scene in enumerate(scenes, start=1):
        missing = sorted(REQUIRED - set(scene))
        if missing:
            errors.append(f"scene {position}: missing {', '.join(missing)}")
            continue
        seconds = scene["seconds"]
        if not isinstance(seconds, (int, float)):
            errors.append(f"scene {position}: seconds must be numeric")
            continue
        if seconds < previous_seconds:
            errors.append(f"scene {position}: seconds are not nondecreasing")
        previous_seconds = seconds
        try:
            if abs(parse_timestamp(scene["timestamp"]) - round(seconds)) > 1:
                errors.append(f"scene {position}: timestamp does not match seconds")
        except (TypeError, ValueError) as exc:
            errors.append(f"scene {position}: invalid timestamp ({exc})")

        title = str(scene["title"]).strip()
        if not title:
            errors.append(f"scene {position}: empty title")
        if len(title) > 55:
            warnings.append(f"scene {position}: title may be too long for an action band")

        frame = args.frames / str(scene["frame"])
        if not frame.is_file():
            errors.append(f"scene {position}: frame missing: {frame.name}")
            continue
        try:
            size = png_size(frame)
            frame_dimensions[frame.name] = [size[0], size[1]]
            if size != (1920, 1080):
                errors.append(f"scene {position}: frame is {size[0]}x{size[1]}, not 1920x1080")
        except ValueError as exc:
            errors.append(f"scene {position}: {frame.name}: {exc}")

    verification = args.verification.read_text(encoding="utf-8")
    ok_ids = [int(value) for value in re.findall(r"(?m)^\[OK\]\s+(\d+)\b", verification)]
    if ok_ids != expected_ids:
        errors.append("verification must contain one ordered [OK] record for every scene")
    if re.search(r"(?m)^\[FIX\]", verification):
        errors.append("verification still contains unresolved [FIX] records")

    slide_count = 0
    if not args.pptx.is_file():
        errors.append("PPTX file is missing")
    else:
        try:
            with zipfile.ZipFile(args.pptx) as archive:
                bad_file = archive.testzip()
                if bad_file:
                    errors.append(f"PPTX archive contains a bad file: {bad_file}")
                slide_count = len(
                    [
                        name
                        for name in archive.namelist()
                        if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
                    ]
                )
        except zipfile.BadZipFile:
            errors.append("PPTX is not a readable OOXML ZIP archive")
        if slide_count != len(scenes):
            errors.append(f"PPTX has {slide_count} slides; expected {len(scenes)}")

    renders = sorted(args.renders.glob("slide-*.png"))
    if len(renders) != len(scenes):
        errors.append(f"render folder has {len(renders)} PNGs; expected {len(scenes)}")
    render_dimensions: dict[str, list[int]] = {}
    for render in renders:
        try:
            size = png_size(render)
            render_dimensions[render.name] = [size[0], size[1]]
            if size != (1920, 1080):
                errors.append(f"render {render.name} is {size[0]}x{size[1]}, not 1920x1080")
        except ValueError as exc:
            errors.append(f"render {render.name}: {exc}")

    report = {
        "status": "OK" if not errors else "ERROR",
        "scene_count": len(scenes),
        "verified_scene_count": len(ok_ids),
        "pptx_slide_count": slide_count,
        "render_count": len(renders),
        "frame_dimensions": frame_dimensions,
        "render_dimensions": render_dimensions,
        "pptx_sha256": sha256(args.pptx) if args.pptx.is_file() else None,
        "warnings": warnings,
        "errors": errors,
    }
    output = json.dumps(report, ensure_ascii=False, indent=2)
    print(output)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output + "\n", encoding="utf-8")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
