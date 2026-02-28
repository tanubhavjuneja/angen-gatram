@echo off
REM ===========================================
REM Forensic Tool - Docker Setup Script
REM ===========================================

echo.
echo ============================================
echo   Forensic Disk Analyzer - Docker Setup
echo ============================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Docker is NOT installed!
    echo.
    echo Please install Docker Desktop from:
    echo   https://www.docker.com/products/docker-desktop
    echo.
    echo After installation, make sure Docker is RUNNING.
    echo.
    pause
    exit /b 1
)

echo [+] Docker is installed
docker --version

echo.
echo [+] Pulling The Sleuth Kit Docker image...
echo    This may take a few minutes on first run...
echo.

docker pull dfirdudes/the-sleuth-kit:latest

if %errorlevel% neq 0 (
    echo [!] Failed to pull Docker image
    pause
    exit /b 1
)

echo.
echo [+] Docker setup complete!
echo.
echo ============================================
echo   Ready to analyze disk images!
echo ============================================
echo.
echo Run the forensic analyzer:
echo   python forensic_analyzer.py
echo.
pause
