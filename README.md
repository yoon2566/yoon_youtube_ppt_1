# yoon_youtube_ppt_1

유튜브의 소프트웨어 사용법 영상을 분석하여 **초보자가 그대로 따라 할 수 있는 1080p PowerPoint**로 만드는 Codex 워크스페이스 로컬 스킬입니다.

단순한 영상 요약이 아니라 다음 과정을 하나의 검증 파이프라인으로 수행합니다.

```text
유튜브 영상
  → 전체 스크립트 분석
  → 한 장당 한 행동으로 장면 계획
  → 해당 시점의 1920×1080 프레임 캡처
  → 스크립트와 화면의 이중 검증
  → 스크린샷 중심 PPTX 제작
  → 전체 슬라이드 렌더·육안 검사
  → 장면 수·해상도·PPTX 구조 최종 검증
```

## 핵심 원칙

- 한 슬라이드에는 하나의 행동 또는 하나의 결과 확인만 넣습니다.
- 영상의 실제 장면을 사용하고 일반 이미지나 재구성한 UI로 대체하지 않습니다.
- 영상이 제공하는 네이티브 1920×1080 프레임을 사용합니다.
- 스크린샷을 슬라이드에서 가능한 한 크게 배치합니다.
- 메뉴명, 프롬프트, 경고, 단축키와 오류 복구 과정을 원본 그대로 보존합니다.
- 모든 슬라이드를 스크립트와 화면 증거 양쪽에서 검증합니다.
- PPTX 생성 성공만으로 완료 처리하지 않고 전체 슬라이드를 1920×1080으로 렌더하여 검사합니다.

## 저장 위치와 호출 이름

이 저장소에서는 Codex가 자동으로 탐색하는 워크스페이스 로컬 경로에 스킬을 저장합니다.

```text
.agents/skills/yoon-youtube-ppt-1/
```

- 저장소·표시 이름: `yoon_youtube_ppt_1`
- Codex 내부 스킬 이름: `yoon-youtube-ppt-1`
- 호출 방법: `$yoon-youtube-ppt-1`

Codex 스킬 이름 규격이 소문자·숫자·하이픈만 허용하므로 내부 이름의 밑줄은 하이픈으로 정규화되어 있습니다.

## 사용 방법

저장소를 내려받아 Codex에서 이 폴더를 워크스페이스로 열거나, `.agents/skills/yoon-youtube-ppt-1` 폴더를 사용할 프로젝트의 같은 위치에 복사합니다.

예시 요청:

```text
$yoon-youtube-ppt-1
https://www.youtube.com/watch?v=VIDEO_ID 영상을 분석해서
초보자용 따라하기 PPT로 만들어줘.
한 장에는 한 행동만 넣고, 해당 장면을 1080p로 캡처해서
이미지를 최대 크기로 배치한 뒤 전체 내용을 다시 검증해줘.
```

## 작업 결과물

권장 작업 폴더 구조:

```text
work/
  transcript/
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

대용량 영상, 음성, 캡처 이미지와 PPTX는 기본적으로 Git에 포함하지 않습니다.

## 포함 파일

| 파일 | 역할 |
|---|---|
| `SKILL.md` | 전체 작업 순서와 완료 기준 |
| `references/workflow-details.md` | 장면 계획 스키마, 캡처 방식, 레이아웃과 검증 규칙 |
| `scripts/transcribe_video.py` | 자막이 없을 때 `faster-whisper`로 타임스탬프 전사 생성 |
| `scripts/validate_project.py` | 장면·프레임·검증 기록·PPTX·렌더 결과 일괄 검증 |
| `agents/openai.yaml` | Codex UI 표시 이름과 기본 호출 프롬프트 |

## 최종 검증

Windows PowerShell 예시:

```powershell
& .\.venv\Scripts\python.exe `
  .\.agents\skills\yoon-youtube-ppt-1\scripts\validate_project.py `
  --scene-plan .\work\scene_plan.json `
  --frames .\work\frames `
  --pptx .\outputs\tutorial.pptx `
  --renders .\work\renders `
  --verification .\analysis\scene_verification.txt `
  --report .\analysis\final_validation.json
```

검증기는 다음 항목을 확인합니다.

- 장면 ID와 시간 순서
- 장면 프레임 존재 여부와 1920×1080 해상도
- 장면별 `[OK]` 검증 기록
- PPTX OOXML 압축 구조와 슬라이드 수
- 전체 렌더 이미지 수와 1920×1080 해상도
- 최종 PPTX SHA-256

이 스크립트는 실제 75장 PPT 작업을 대상으로 장면 75개, 검증 기록 75개, PPT 슬라이드 75장, 렌더 75장이 모두 일치하는 조건에서 테스트했습니다.

## 필요한 환경

- Codex와 PowerPoint 제작 기능
- 웹 브라우저 또는 영상 프레임을 정확히 추출할 수 있는 도구
- Python 가상환경
- 자막이 없는 영상의 경우 `yt-dlp`, `faster-whisper`

영상과 캡처 이미지는 사용 권한을 확인하고, 결과물에 원본 YouTube URL과 출처를 표기하세요.
