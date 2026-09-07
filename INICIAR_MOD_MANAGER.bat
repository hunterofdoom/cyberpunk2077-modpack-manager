@echo off
title Cyberpunk 2077 - Modpack Manager ^& Launcher
chcp 65001 >nul
cd /d "%~dp0"

echo =======================================================
echo    CYBERPUNK 2077 // MODPACK AUTO-MANAGER ^& LAUNCHER
echo =======================================================
echo.
echo Comprobando entorno de Python...

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] No se ha encontrado Python instalado en el sistema.
    echo Por favor instala Python 3.10 o superior desde python.org
    echo y asegurate de marcar "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

echo [OK] Python detectado.
echo Iniciando aplicacion grafica...
echo.

start "" pythonw cp2077_mod_manager.py

if %errorlevel% neq 0 (
    python cp2077_mod_manager.py
)

exit /b 0
