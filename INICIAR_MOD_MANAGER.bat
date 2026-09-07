@echo off
title Cyberpunk 2077 - Modpack Manager ^& Launcher
chcp 65001 >nul
cd /d "%~dp0"

echo =======================================================
echo    CYBERPUNK 2077 // MODPACK AUTO-MANAGER ^& LAUNCHER
echo =======================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] No se ha encontrado Python en este equipo.
    echo Por favor instala Python 3.10 o superior desde https://www.python.org
    echo y asegurate de marcar la casilla "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)

echo Comprobando dependencias necesarias (OpenCV, Pillow, NumPy)...
python -c "import cv2, PIL, numpy" >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando dependencias automaticamente...
    pip install --quiet opencv-python Pillow numpy
)

echo Iniciando aplicacion grafica...
echo.

start "" pythonw cp2077_mod_manager.py

if %errorlevel% neq 0 (
    python cp2077_mod_manager.py
)

exit /b 0
