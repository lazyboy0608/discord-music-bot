@echo off
title Discord Music Bot (Native)
cd /d "%~dp0"

echo ========================================================
echo     DISCORD MUSIC BOT - CHE DO NATIVE (SIEU TIET KIEM RAM)
echo ========================================================
echo [1/2] Dang khoi dong Lavalink Server...
start "Lavalink-Server-Music67" /min java "-Duser.language=en" "-Duser.country=US" -Xmx512M -jar Lavalink.jar

echo [2/2] Cho Lavalink san sang trong 4 giay...
timeout /t 4 /nobreak >nul

echo [3/3] Dang khoi dong Discord Music Bot...
echo ========================================================
echo Bot dang chay! Nhac da san sang tren Discord.
echo De tat bot, ban chi can chay file stop_native.bat
echo hoac dong cua so nay.
echo ========================================================
python bot.py

pause
