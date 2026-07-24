---
name: yoon-youtube-ppt-1
description: Convert a YouTube software tutorial into a verified Korean beginner follow-along PowerPoint. Use when Codex must analyze the full transcript, split the lesson into one observable action per slide, capture the matching native 1080p video frame at each timestamp, maximize screenshot size, build a complete 16:9 PPTX, and verify every slide against both speech and screen evidence. Do not use for a short video summary, a lecture-outline deck, or slides based on guessed UI steps.
---

# yoon_youtube_ppt_1

Create a screenshot-dominant tutorial deck that a first-time learner can follow without replaying the video. Treat transcript analysis, frame selection, slide construction, and final verification as one continuous evidence pipeline.

## Required behavior

- Analyze the entire video before designing slides.
- Put exactly one observable user action or one result check on each instructional slide.
- Use the matching video frame, not a generic stock image or reconstructed UI.
- Capture at the video's native `1920x1080` after selecting 1080p playback. Never label an upscaled lower-resolution frame as native 1080p.
- Make the screenshot the largest meaningful object on the slide.
- Preserve exact UI labels, prompts, warnings, keyboard shortcuts, and error-recovery steps shown in the source.
- Verify every slide against both nearby transcript text and visible screen evidence.
- Do not claim completion from a successful PPTX build alone. Render and inspect every slide.

Read [references/workflow-details.md](references/workflow-details.md) before starting capture or deck construction. Use [scripts/transcribe_video.py](scripts/transcribe_video.py) when captions are unavailable. Run [scripts/validate_project.py](scripts/validate_project.py) before delivery.

## Workflow

### 1. Establish the source

1. Record the YouTube URL, title, duration, publication date when available, and access date.
2. Check whether usable captions exist. If not, download authorized audio with `yt-dlp` and transcribe it locally.
3. Save timestamped transcript data as UTF-8 JSON and text.
4. Correct recognition errors only when the visible UI or surrounding context supports the correction. Record important corrections.

### 2. Build the action map

1. Read the complete transcript.
2. Divide the tutorial by real task boundaries, including preparation, mistakes, recovery, saving, sharing, alternatives, and mobile steps.
3. Write a `scene_plan.json` entry for every slide using the schema in the reference.
4. Phrase each title as a single beginner action, such as “업로드 버튼을 클릭한다” or “결과가 바뀌었는지 확인한다.”
5. Split combined actions into separate slides. Keep genuine result checks as their own slides.
6. Exclude commentary that does not help the learner act, but do not omit warnings or recovery paths that affect success.

### 3. Capture evidence frames

1. Set YouTube playback to 1080p and confirm `videoWidth=1920` and `videoHeight=1080`.
2. Seek to the planned timestamp and capture the exact state that proves the action.
3. Prefer extracting the HTML video frame at native dimensions. A viewport screenshot is acceptable only when native extraction is impossible and the captured content remains true 1920x1080.
4. Recapture when menus are closed, text is clipped, the cursor state is wrong, a loading overlay remains, or the transcript and screen refer to different actions.
5. Save frames with stable names and record their dimensions.
6. For mobile footage, preserve the complete phone UI and crop only irrelevant outer padding.

### 4. Verify before slide building

For every scene, compare:

- action title versus transcript around the timestamp;
- action title versus visible UI state;
- exact labels and prompt text versus the frame;
- timestamp versus the intended step order;
- frame dimensions versus the 1080p requirement.

Write one verification record per scene. Use `OK` only when both transcript and frame support the slide. Fix the plan or recapture the frame for every mismatch.

### 5. Build the PowerPoint

1. Load the available presentation-authoring skill and follow its build and render requirements.
2. Use a 16:9 layout.
3. Use a full-bleed screenshot or the maximum possible screenshot area.
4. Add only a compact action band containing step number, section, one-action title, and timestamp. Do not cover critical UI.
5. Use a short note only when the learner needs a warning, prerequisite, or recovery explanation not obvious from the frame.
6. For mobile scenes, enlarge the phone capture to maximum height and place a narrow explanation panel beside it.
7. Keep cover and section styling consistent, but never reduce instructional screenshots merely for decoration.
8. Add source attribution and the YouTube URL.

### 6. Render and inspect every slide

1. Render the full deck to exactly `1920x1080` images.
2. Inspect each rendered slide at original size, not only a montage.
3. Confirm legibility, image sharpness, no clipping, no overlap, correct step number, correct timestamp, and correct frame.
4. Recheck slides with dense menus, small text, dialog boxes, or mobile UI.
5. Run the presentation test utility supplied by the presentation skill when available.

### 7. Final evidence gate

Run:

```powershell
& .\.venv\Scripts\python.exe .\.agents\skills\yoon-youtube-ppt-1\scripts\validate_project.py `
  --scene-plan .\work\scene_plan.json `
  --frames .\work\frames `
  --pptx .\outputs\tutorial.pptx `
  --renders .\work\renders `
  --verification .\analysis\scene_verification.txt `
  --report .\analysis\final_validation.json
```

Deliver only when the report has zero errors. Report the PPTX path, slide count, rendered resolution, source URL, validation result, and SHA-256 hash. If the source does not offer 1080p, state that limitation before building and do not represent the deck as native 1080p.

## Completion standard

The work is complete only when:

- every planned slide has a matching verified frame;
- every instructional slide performs one action or one result check;
- every frame and render passes the resolution checks;
- PPTX slide count equals scene-plan and render counts;
- every slide has been visually inspected;
- the final PPTX opens as a valid OOXML archive;
- no unsupported or invented instruction remains.
