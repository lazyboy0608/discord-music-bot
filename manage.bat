@echo off
setlocal EnableDelayedExpansion
title Discord Music Bot Manager

set "PATH=C:\Program Files\Docker\Docker\resources\bin;%PATH%"

:MENU
cls
echo ===================================================
echo           DISCORD MUSIC BOT MANAGER
echo ===================================================
echo [1] Start All (Lavalink + Bot)
echo [2] View Lavalink Logs (YouTube OAuth Code)
echo [3] View Bot Logs
echo [4] Stop All (docker compose down)
echo [5] Restart Bot
echo [0] Exit
echo ===================================================
set /p opt="Select an option (0-5): "

if "%opt%"=="1" goto START_ALL
if "%opt%"=="2" goto LOGS_LAVALINK
if "%opt%"=="3" goto LOGS_BOT
if "%opt%"=="4" goto STOP_ALL
if "%opt%"=="5" goto RESTART_BOT
if "%opt%"=="0" exit /b
goto MENU

:START_ALL
echo Starting Lavalink and Bot...
docker compose up -d
echo Done! Both containers are running in the background.
pause
goto MENU

:LOGS_LAVALINK
echo Press Ctrl + C to exit logs.
docker compose logs -f lavalink
goto MENU

:LOGS_BOT
echo Press Ctrl + C to exit logs.
docker compose logs -f bot
goto MENU

:STOP_ALL
echo Stopping containers...
docker compose down
echo Stopped!
pause
goto MENU

:RESTART_BOT
echo Restarting bot...
docker compose restart bot
echo Done!
pause
goto MENU
