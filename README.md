# yt-transcript (Claude Code 스킬)

유튜브 영상의 자막을 **요약 없이 원문 텍스트 그대로** `.txt` 파일로 저장하는 Claude Code 스킬입니다. Windows(cmd / Git Bash)를 기준으로 만들었고 macOS·Linux에서도 동작합니다.

## 설치 (Windows)

1. Python 3을 설치합니다: https://www.python.org/downloads/ (설치할 때 **Add python.exe to PATH** 체크)
2. cmd에서 다음을 실행합니다.

```cmd
git clone https://github.com/moonjinpark/practice1.git %USERPROFILE%\practice1
cd /d %USERPROFILE%\practice1
git checkout claude/wonderful-pascal-3sknmq
install.cmd
```

`install.cmd`는 스킬을 `%USERPROFILE%\.claude\skills\yt-transcript`에 복사하고 `youtube-transcript-api`를 설치합니다. 설치 후 Claude Code를 다시 실행하세요.

## 사용법 (Claude Code 안에서)

```
/yt-transcript https://www.youtube.com/watch?v=VIDEO_ID
```

자연어로 요청해도 됩니다.

- `이 영상 자막 뽑아줘 https://youtu.be/...`
- `영어 자막으로 타임스탬프 빼고 텍스트만 저장해줘 https://youtu.be/...`
- `이 영상에 어떤 자막 언어가 있는지 알려줘 https://youtu.be/...`

결과는 현재 폴더의 `transcripts\<VIDEO_ID>.txt`에 저장됩니다.

## 스크립트 단독 사용

Claude 없이 cmd에서 바로 써도 됩니다.

```cmd
python %USERPROFILE%\.claude\skills\yt-transcript\scripts\get_transcript.py "https://youtu.be/VIDEO_ID" --out 자막.txt
```

| 옵션 | 설명 |
|---|---|
| `--lang ko,en` | 선호 언어 순서 (기본 `ko,en`). 없으면 있는 자막 중 하나를 쓰고 `LANG_WARN:`을 출력 |
| `--no-timestamps` | `[M:SS]` 없이 본문만 |
| `--out 파일.txt` | UTF-8 파일로 저장 (생략 시 화면 출력) |
| `--list` | 사용 가능한 자막 언어 목록만 표시 |

## 제한

- 자막(수동 또는 자동 생성)이 있는 영상만 됩니다. 자막이 없는 영상은 음성 인식이 필요해 지원하지 않습니다.
- 짧은 시간에 너무 많이 요청하면 YouTube가 IP를 일시적으로 차단할 수 있습니다.
