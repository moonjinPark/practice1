#!/usr/bin/env python3
"""YouTube 자막을 텍스트로 추출합니다 (Windows / macOS / Linux 공용).

사용법:
  python get_transcript.py <URL 또는 VIDEO_ID> [--lang ko,en] [--no-timestamps] [--out 파일.txt]
  python get_transcript.py <URL 또는 VIDEO_ID> --list

출력:
  성공 시 stdout 첫 줄들에 VIDEO_ID: / LANG: / TYPE: 헤더, 빈 줄, 그다음 자막 본문.
  --out 을 주면 본문을 UTF-8 파일로 저장하고 SAVED: <절대경로> 를 출력합니다.
  실패 시 stderr 에 ERROR:<코드> <메시지> 를 출력하고 종료 코드 1.
"""
import argparse
import pathlib
import re
import sys

# Windows 콘솔(cp949 등)에서 한글/이모지 출력 시 UnicodeEncodeError 방지
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
URL_PATTERNS = [
    r"[?&]v=([A-Za-z0-9_-]{11})",
    r"youtu\.be/([A-Za-z0-9_-]{11})",
    r"youtube\.com/(?:shorts|embed|live|v)/([A-Za-z0-9_-]{11})",
]


def fail(code, msg):
    print(f"ERROR:{code} {msg}", file=sys.stderr)
    sys.exit(1)


def extract_video_id(text):
    text = text.strip().strip('"').strip("'")
    if ID_RE.match(text):
        return text
    for pat in URL_PATTERNS:
        m = re.search(pat, text)
        if m:
            return m.group(1)
    fail("INVALID_INPUT", f"유튜브 URL 또는 11자리 영상 ID가 아닙니다: {text}")


def fmt_time(seconds):
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def list_transcripts(video_id):
    """youtube-transcript-api 1.x(인스턴스 API)와 0.6.x(정적 API) 모두 지원."""
    from youtube_transcript_api import YouTubeTranscriptApi
    if hasattr(YouTubeTranscriptApi, "list_transcripts"):
        return YouTubeTranscriptApi.list_transcripts(video_id)
    return YouTubeTranscriptApi().list(video_id)


def pick_transcript(tlist, langs):
    """요청 언어 순서대로 (언어마다 수동 → 자동 자막), 없으면 아무 자막이나."""
    from youtube_transcript_api import NoTranscriptFound
    for lang in langs:
        for finder in (tlist.find_manually_created_transcript,
                       tlist.find_generated_transcript):
            try:
                return finder([lang]), False
            except NoTranscriptFound:
                pass
    all_t = list(tlist)
    if not all_t:
        fail("NO_TRANSCRIPT", "이 영상에는 자막이 없습니다.")
    all_t.sort(key=lambda t: t.is_generated)  # 수동 자막 우선
    return all_t[0], bool(langs)


def snippet_fields(s):
    if isinstance(s, dict):
        return s.get("start", 0), s.get("text", "")
    return s.start, s.text


def main():
    ap = argparse.ArgumentParser(description="YouTube 자막 텍스트 추출")
    ap.add_argument("video", help="유튜브 URL 또는 영상 ID")
    ap.add_argument("--lang", default="ko,en",
                    help="선호 언어 코드, 쉼표 구분 (기본: ko,en)")
    ap.add_argument("--no-timestamps", action="store_true",
                    help="타임스탬프 없이 본문만 출력")
    ap.add_argument("--out", help="저장할 텍스트 파일 경로")
    ap.add_argument("--list", action="store_true",
                    help="사용 가능한 자막 언어 목록만 출력")
    args = ap.parse_args()

    try:
        import youtube_transcript_api as yta
    except ImportError:
        fail("LIBRARY_MISSING", "pip install youtube-transcript-api 를 먼저 실행하세요.")

    video_id = extract_video_id(args.video)
    langs = [l.strip() for l in args.lang.split(",") if l.strip()]

    errors = {
        "TranscriptsDisabled": ("CAPTIONS_DISABLED", "이 영상은 자막이 비활성화되어 있습니다."),
        "VideoUnavailable": ("VIDEO_UNAVAILABLE", "영상을 찾을 수 없거나 비공개입니다."),
        "AgeRestricted": ("AGE_RESTRICTED", "연령 제한 영상이라 자막을 가져올 수 없습니다."),
        "InvalidVideoId": ("INVALID_VIDEO_ID", "잘못된 영상 ID입니다."),
        "IpBlocked": ("IP_BLOCKED", "YouTube가 현재 IP를 차단했습니다. 잠시 후 다시 시도하세요."),
        "RequestBlocked": ("REQUEST_BLOCKED", "YouTube가 요청을 차단했습니다. 잠시 후 다시 시도하세요."),
    }

    try:
        tlist = list_transcripts(video_id)

        if args.list:
            print(f"VIDEO_ID: {video_id}")
            for t in tlist:
                kind = "auto" if t.is_generated else "manual"
                print(f"{t.language_code}\t{kind}\t{t.language}")
            return

        transcript, lang_fallback = pick_transcript(tlist, langs)
        data = transcript.fetch()
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001 - 라이브러리 버전마다 예외 클래스가 달라 이름으로 분기
        name = type(e).__name__
        code, msg = errors.get(name, ("TRANSCRIPT_FETCH_FAILED", f"{name}: {str(e).splitlines()[0] if str(e) else ''}"))
        if isinstance(e, getattr(yta, "NoTranscriptFound", ())):
            code, msg = "NO_TRANSCRIPT", "요청한 언어의 자막이 없습니다."
        fail(code, msg)

    lines = []
    for s in data:
        start, text = snippet_fields(s)
        text = " ".join(text.split())  # 자막 내부 줄바꿈 정리
        if not text:
            continue
        lines.append(text if args.no_timestamps else f"[{fmt_time(start)}] {text}")
    body = "\n".join(lines) + "\n"

    print(f"VIDEO_ID: {video_id}")
    print(f"LANG: {transcript.language_code} ({transcript.language})")
    print(f"TYPE: {'auto' if transcript.is_generated else 'manual'}")
    if lang_fallback:
        print(f"LANG_WARN: 요청한 언어({','.join(langs)}) 자막이 없어 {transcript.language_code} 자막을 사용했습니다.")

    if args.out:
        out = pathlib.Path(args.out).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
        print(f"LINES: {len(lines)}")
        print(f"SAVED: {out}")
    else:
        print()
        sys.stdout.write(body)


if __name__ == "__main__":
    main()
