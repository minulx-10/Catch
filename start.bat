@echo off
title CatchBot Auto-Updater
chcp 65001 > nul

:loop
echo ====================================================
echo [CatchBot] 최신 코드를 깃허브에서 가져옵니다 (git pull)...
git pull origin main

echo.
echo [CatchBot] 라이브러리 업데이트 확인 중...
pip install -r requirements.txt -q

echo.
echo [CatchBot] 봇을 실행합니다! (중단하려면 Ctrl+C)
python main.py

echo.
echo ====================================================
echo [CatchBot] 봇이 종료되었습니다. (오류 또는 재시작 명령)
echo [CatchBot] 5초 후 깃허브에서 최신 버전을 다운로드하고 다시 시작합니다...
timeout /t 5
goto loop
