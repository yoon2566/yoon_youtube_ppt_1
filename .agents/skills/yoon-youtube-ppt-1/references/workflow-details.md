# Workflow details

## Contents

1. Workspace layout
2. Transcript and terminology analysis
3. Scene-plan schema
4. Native frame capture
5. Slide layout
6. Verification records
7. Quality gates

## 1. Workspace layout

Keep sources, intermediate evidence, and deliverables separate:

```text
work/
  audio/
  transcript/
    transcript.json
    transcript.txt
  frames/
  renders/
  scene_plan.json
analysis/
  transcript_analysis.txt
  scene_verification.txt
  final_validation.json
src/
  build_deck.mjs
outputs/
  tutorial.pptx
```

Store large downloaded media and generated frames outside Git unless the user explicitly requests them. Keep source URLs and attribution in the analysis and deck.

## 2. Transcript and terminology analysis

When YouTube captions are absent or unreliable:

1. Download only the audio needed for analysis with `yt-dlp`.
2. Run `scripts/transcribe_video.py` in the workspace virtual environment.
3. Compare uncertain proper nouns against visible UI labels.
4. Preserve the raw transcript and list supported corrections separately.

Do not silently replace uncertain speech with a guessed product name. Use nearby visual evidence. If the UI has changed since the video, teach what the video actually shows and add a dated note instead of substituting current UI claims.

The transcript analysis should include:

- source URL, title, duration, language, and segment count;
- lesson flow in source order;
- corrected terminology with evidence;
- omissions or inaccessible portions;
- candidate timestamps for each observable action.

## 3. Scene-plan schema

Use a JSON array. Required fields:

```json
[
  {
    "id": 1,
    "section": "준비",
    "title": "Google에서 Gemini를 검색한다",
    "timestamp": "02:56",
    "seconds": 176,
    "frame": "007-0256.png",
    "evidence": "Google 검색 화면에서 Gemini 검색을 시작하는 상태가 보임",
    "note": "필요한 경우에만 추가",
    "layout": "full"
  }
]
```

Rules:

- Number `id` consecutively from 1.
- Keep `seconds` nondecreasing.
- Make `timestamp` agree with `seconds`.
- Use one imperative action or one result check in `title`.
- Describe visible proof, not an intention, in `evidence`.
- Use `layout: "mobile"` only for phone-oriented footage.
- Use `layout: "cover"` only for the cover.

## 4. Native frame capture

Preferred browser extraction sequence:

1. Open the YouTube video in the in-app browser.
2. Select 1080p playback.
3. Pause and seek using the HTML video element.
4. Confirm `video.videoWidth === 1920` and `video.videoHeight === 1080`.
5. Draw the video element into a canvas at those intrinsic dimensions.
6. Export PNG data from the canvas and save it to the frame folder.

Use a nearby timestamp when the exact second shows a transition, but keep the transcript evidence window honest. Do not capture the YouTube player controls unless they are relevant to the step.

Reject a frame when:

- its intrinsic dimensions are below 1920x1080;
- a menu required by the action is not open;
- important text is cut off;
- the frame shows before or after the action instead of the intended state;
- a tooltip, cursor, or overlay hides critical content;
- the action title cannot be proven from the pixels.

## 5. Slide layout

Default instructional layout:

- 16:9 slide;
- screenshot full width and as much height as possible;
- compact opaque action bar at the bottom;
- step number and section in small type;
- action title in large Korean type;
- timestamp aligned at the edge;
- no decorative cards over the UI.

Mobile layout:

- crop the phone screen cleanly;
- scale it to near full slide height;
- use a narrow side panel for the action and essential warning;
- do not enlarge beyond readable quality.

Keep instructional text short enough to read while looking at the screenshot. Put long explanations in speaker notes only if the output format and user request require them.

## 6. Verification records

Write one block per scene:

```text
[OK] 7 | 02:56 | Google에서 Gemini를 검색한다
  전사: Gemini 검색을 시작하라는 발화가 있음
  화면: Google 검색창과 Gemini 검색어가 보임
  파일: 007-0256.png (1920x1080)
```

Use `[FIX]` while unresolved. Never convert it to `[OK]` without changing either the plan or frame and checking again.

## 7. Quality gates

Before delivery, confirm:

- scene-plan count = verification count = PPTX slide count = render count;
- frame files exist and are exactly 1920x1080;
- rendered slides are exactly 1920x1080;
- timestamps and seconds agree;
- IDs are consecutive;
- every slide has been individually viewed at original resolution;
- the PPTX is a readable ZIP/OOXML package;
- no slide combines two separate learner actions;
- no generic image substitutes for source evidence;
- no unverified claims about current product behavior are presented as facts.
