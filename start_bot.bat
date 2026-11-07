@echo off
title Start Discord Music Bot
set "PATH=C:\Program Files\Docker\Docker\resources\bin;%PATH%"

echo ===================================================
echo Dang khoi dong Discord Music Bot...
echo ===================================================
docker compose up -d

echo.
echo ===================================================
echo Bot va Lavalink da duoc bat thanh cong trong Docker!
echo Ban co the tat cua so nay. Bot van se chay ngam.
echo ===================================================
echo.
pause
