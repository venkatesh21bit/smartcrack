@echo off
chcp 65001 > nul
color 0A
title Brute Force Password Cracker

:menu
cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║        BRUTE FORCE PASSWORD CRACKER                            ║
echo ║        Dictionary and Brute Force Attacks                      ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo [1] Dictionary Attack (Single File)
echo [2] Dictionary Attack (Batch - All Files)
echo [3] Hybrid Attack (Dictionary + Mutations)
echo [4] Brute Force Attack (Single File)
echo [5] Check Wordlist Statistics
echo [6] View Previous Results
echo [7] Exit
echo.
set /p choice="Select option (1-7): "

if "%choice%"=="1" goto single_dict
if "%choice%"=="2" goto batch_dict
if "%choice%"=="3" goto hybrid
if "%choice%"=="4" goto brute
if "%choice%"=="5" goto stats
if "%choice%"=="6" goto results
if "%choice%"=="7" goto end

echo Invalid option!
timeout /t 2 > nul
goto menu

:single_dict
cls
echo.
echo ════════════════════════════════════════════════════════════════
echo DICTIONARY ATTACK - SINGLE FILE
echo ════════════════════════════════════════════════════════════════
echo.
set /p target="Enter target file path: "
echo.
echo Available wordlists:
echo [1] RockYou 12+ (2.8M passwords)
echo [2] Custom wordlist
echo.
set /p wl_choice="Select wordlist (1-2): "

if "%wl_choice%"=="1" (
    set wordlist=wordlists\rockyou-12plus.txt
) else (
    set /p wordlist="Enter wordlist path: "
)

echo.
set /p max="Max passwords to try (leave empty for all): "

if "%max%"=="" (
    python cracker.py "%target%" -w "%wordlist%" -t dictionary
) else (
    python cracker.py "%target%" -w "%wordlist%" -t dictionary -m %max%
)

echo.
pause
goto menu

:batch_dict
cls
echo.
echo ════════════════════════════════════════════════════════════════
echo BATCH DICTIONARY ATTACK - ALL FILES
echo ════════════════════════════════════════════════════════════════
echo.
echo This will crack all files in Level1 and Level2 folders
echo.
set /p confirm="Continue? (Y/N): "
if /i not "%confirm%"=="Y" goto menu

echo.
echo Starting batch attack...
echo.

python batch_cracker.py -d ..\Level1\Level1\Level1 ..\Level2\Level2 -w wordlists\rockyou-12plus.txt -t dictionary -o results

echo.
pause
goto menu

:hybrid
cls
echo.
echo ════════════════════════════════════════════════════════════════
echo HYBRID ATTACK - DICTIONARY + MUTATIONS
echo ════════════════════════════════════════════════════════════════
echo.
set /p target="Enter target file path: "
echo.

python cracker.py "%target%" -w wordlists\rockyou-12plus.txt -t hybrid

echo.
pause
goto menu

:brute
cls
echo.
echo ════════════════════════════════════════════════════════════════
echo BRUTE FORCE ATTACK
echo ════════════════════════════════════════════════════════════════
echo.
echo ⚠ WARNING: Brute force can take VERY long for passwords > 6 chars
echo.
set /p target="Enter target file path: "
echo.
set /p min_len="Minimum length (default 1): "
set /p max_len="Maximum length (default 6): "

if "%min_len%"=="" set min_len=1
if "%max_len%"=="" set max_len=6

echo.
echo Character sets:
echo [1] Digits only (0-9)
echo [2] Lowercase only (a-z)
echo [3] Alphanumeric (a-z, A-Z, 0-9)
echo [4] All printable
echo.
set /p cs_choice="Select charset (1-4): "

if "%cs_choice%"=="1" set charset=0123456789
if "%cs_choice%"=="2" set charset=abcdefghijklmnopqrstuvwxyz
if "%cs_choice%"=="3" set charset=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
if "%cs_choice%"=="4" set charset=

echo.
if defined charset (
    python cracker.py "%target%" -t brute_force --min-length %min_len% --max-length %max_len% --charset "%charset%"
) else (
    python cracker.py "%target%" -t brute_force --min-length %min_len% --max-length %max_len%
)

echo.
pause
goto menu

:stats
cls
echo.
echo ════════════════════════════════════════════════════════════════
echo WORDLIST STATISTICS
echo ════════════════════════════════════════════════════════════════
echo.

if exist "wordlists\rockyou-12plus.txt" (
    echo Analyzing wordlist...
    echo.
    
    for /f %%A in ('powershell -command "Get-Content wordlists\rockyou-12plus.txt | Measure-Object -Line | Select-Object -ExpandProperty Lines"') do set line_count=%%A
    echo Total passwords: %line_count%
    
    for /f %%A in ('powershell -command "(Get-Item wordlists\rockyou-12plus.txt).length / 1MB"') do set file_size=%%A
    echo File size: %file_size% MB
    
    echo.
    echo First 10 passwords:
    powershell -command "Get-Content wordlists\rockyou-12plus.txt -First 10"
    
    echo.
    echo Last 10 passwords:
    powershell -command "Get-Content wordlists\rockyou-12plus.txt -Last 10"
) else (
    echo ✗ Wordlist not found: wordlists\rockyou-12plus.txt
    echo.
    echo Please copy the RockYou filtered dataset to this folder.
)

echo.
pause
goto menu

:results
cls
echo.
echo ════════════════════════════════════════════════════════════════
echo PREVIOUS RESULTS
echo ════════════════════════════════════════════════════════════════
echo.

if exist "results" (
    dir /b /o-d results\cracked_passwords_*.txt 2>nul
    
    if errorlevel 1 (
        echo No results found yet.
    ) else (
        echo.
        set /p result_file="Enter filename to view (or press Enter to skip): "
        
        if not "!result_file!"=="" (
            if exist "results\!result_file!" (
                type "results\!result_file!"
            ) else (
                echo File not found!
            )
        )
    )
) else (
    echo No results directory found yet.
    echo Run a cracking session first.
)

echo.
pause
goto menu

:end
echo.
echo Exiting...
exit /b 0
