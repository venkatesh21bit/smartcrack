@echo off
REM PassGAN Password Cracker - Windows Batch Script

echo ============================================================
echo PassGAN Password Cracker - Quick Start
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if in correct directory
if not exist "pasgan\main.py" (
    echo Error: Please run this script from the smartcrack directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo.
echo Select operation:
echo   1. Install dependencies
echo   2. Download password datasets (RockYou)
echo   3. Train model
echo   4. Generate passwords
echo   5. Crack files (Level1 and Level2)
echo   6. Run complete pipeline (all steps)
echo   7. Exit
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto dataset
if "%choice%"=="3" goto train
if "%choice%"=="4" goto generate
if "%choice%"=="5" goto crack
if "%choice%"=="6" goto all
if "%choice%"=="7" goto end
goto invalid

:install
echo.
echo Installing dependencies...
python -m pip install -r pasgan\requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo.
echo Dependencies installed successfully!
pause
goto end

:dataset
echo.
echo ============================================================
echo Password Dataset Download
echo ============================================================
echo.
echo For better password cracking results, download RockYou dataset
echo (14+ million real passwords from data breach)
echo.
echo This will:
echo   - Download RockYou dataset (~133 MB)
echo   - Filter passwords for 12+ characters
echo   - Prepare for training
echo.
set /p confirm="Download dataset? (y/n): "
if /i not "%confirm%"=="y" goto end

echo.
python pasgan\download_datasets.py
pause
goto end

:train
echo.
REM Check if dataset exists
if exist "datasets\rockyou.txt" (
    echo ✓ RockYou dataset found - will use real password data
    echo   This provides much better results!
) else if exist "datasets\rockyou-12plus.txt" (
    echo ✓ Filtered RockYou dataset found - will use real password data
) else (
    echo ⚠ No password dataset found
    echo   Training will use synthetic data (limited effectiveness)
    echo.
    echo For better results, select option 2 to download RockYou dataset
    echo.
    set /p continue="Continue with synthetic data? (y/n): "
    if /i not "%continue%"=="y" goto end
)
echo.
echo Training PassGAN model...
echo This may take 10-60 minutes depending on your hardware
python pasgan\main.py --train --epochs 100
pause
goto end

:generate
echo.
echo Generating passwords...
python pasgan\main.py --generate --num-passwords 10000 --min-length 12
pause
goto end

:crack
echo.
echo Cracking files in Level1 and Level2...
python pasgan\main.py --crack --targets Level1\Level1\Level1 Level2\Level2
pause
goto end

:all
echo.
echo ============================================================
echo Complete Pipeline
echo ============================================================
echo.
REM Check if dataset exists
if exist "datasets\rockyou.txt" (
    echo ✓ RockYou dataset found - will use real password data
) else if exist "datasets\rockyou-12plus.txt" (
    echo ✓ Filtered RockYou dataset found
) else (
    echo ⚠ WARNING: No password dataset found!
    echo.
    echo For MUCH better results, download RockYou dataset first:
    echo   Select option 2 from the main menu
    echo.
    echo Continue with synthetic data? (NOT RECOMMENDED)
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" goto end
)
echo.
echo Running complete pipeline...
echo This will: 1) Train model, 2) Generate passwords, 3) Crack files
echo This may take 30-90 minutes depending on your hardware
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" goto end

python pasgan\main.py --all --epochs 100 --num-passwords 10000 --targets Level1\Level1\Level1 Level2\Level2
pause
goto end

:invalid
echo.
echo Invalid choice. Please select 1-7.
pause
goto end

:end
echo.
echo Goodbye!
