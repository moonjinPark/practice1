@echo off
setlocal
rem Installs the yt-transcript skill for Claude Code on Windows.
rem Usage: double-click, or run "install.cmd" from this folder.

set "SRC=%~dp0skills\yt-transcript"
set "DEST=%USERPROFILE%\.claude\skills\yt-transcript"

if not exist "%SRC%\SKILL.md" (
  echo [ERROR] skills\yt-transcript not found next to install.cmd
  exit /b 1
)

echo Copying skill to %DEST% ...
xcopy /E /I /Y "%SRC%" "%DEST%" >nul || (echo [ERROR] copy failed & exit /b 1)

set "PY="
python -c "import sys" >nul 2>&1 && set "PY=python"
if not defined PY py -3 -c "import sys" >nul 2>&1 && set "PY=py -3"
if not defined PY (
  echo [WARN] Python 3 not found. Install it from https://www.python.org/downloads/
  echo        ^(check "Add python.exe to PATH"^), then run:
  echo        pip install youtube-transcript-api
  exit /b 0
)

echo Installing youtube-transcript-api with %PY% ...
%PY% -m pip install --upgrade youtube-transcript-api || (echo [ERROR] pip install failed & exit /b 1)

echo.
echo Done. Restart Claude Code, then try:
echo   /yt-transcript https://www.youtube.com/watch?v=VIDEO_ID
endlocal
