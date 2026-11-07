@echo off
title Stop Discord Music Bot (Native)
echo ========================================================
echo Dang tat toan bo tien trinh Lavalink Server va Music Bot...
echo ========================================================

taskkill /f /fi "WINDOWTITLE eq Lavalink-Server-Music67*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq Discord Music Bot (Native)*" >nul 2>&1
taskkill /f /im java.exe /fi "MEMUSAGE gt 50000" >nul 2>&1

echo Da tat sach se cac tien trinh chay ngam!
timeout /t 2 >nul
