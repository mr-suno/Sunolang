@echo off

REM Install Sunolang on PATH
REM Allows you (in a CLI) to call files: su <filename>

REM WARNING! This file is NOT to be tampered with
REM          Tampering can result it in not working as intended.

REM Code generated on August 3rd, 2024

setlocal EnableDelayedExpansion
set LF=^
echo.
echo(
for %%A in (
"     _____                   _                   "
"    / ____|                 | |                  "
"   | (___  _   _ _ __   ___ | | __ _ _ __   __ _ "
"    \___ \| | | | '_ \ / _ \| |/ _` | '_ \ / _` |"
"    ____) | |_| | | | | (_) | | (_| | | | | (_| |"
"   |_____/ \__,_|_| |_|\___/|_|\__,_|_| |_|\__, |"
"                                            __/ |"
"                                           |___/ "
) do (
   set "line=%%~A"
   echo(!line!
)
echo.
echo    [~] Starting Installation
echo    [~] Prompting Administrator Access (IF required)
color 06
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    goto UACPrompt
) else ( goto gotAdmin )
:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~f0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs" >nul 2>&1
    exit /B
:gotAdmin
    if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs" >nul 2>&1
    pushd "%CD%" >nul 2>&1
    CD /D "%~dp0" >nul 2>&1
echo    [~] Locating Directories
setlocal enabledelayedexpansion
set "INSTALL_DIR=%ProgramFiles%\Sunolang"
set "BUILD_DIR=%~dp0build"
if exist "%INSTALL_DIR%" (
    echo    [~] Removing Directories
    rmdir /s /q "%INSTALL_DIR%" >nul 2>&1
    if errorlevel 1 (
        pause
        exit /b 1
    )
)
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "PATH=%%B"
set "PATH=!PATH:%INSTALL_DIR%;=!"
setx PATH "%PATH%" /M >nul 2>&1
echo    [~] Installing Directories
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%" >nul 2>&1
echo @echo off > "%INSTALL_DIR%\su.bat"
echo python "%%~dp0sunolang.py" %%* >> "%INSTALL_DIR%\su.bat"
if not exist "%BUILD_DIR%\basic.py" (
    pause
    exit /b 1
)
if not exist "%BUILD_DIR%\sunolang.py" (
    pause
    exit /b 1
)
copy "%BUILD_DIR%\basic.py" "%INSTALL_DIR%\basic.py" >nul 2>&1
copy "%BUILD_DIR%\sunolang.py" "%INSTALL_DIR%\sunolang.py" >nul 2>&1
setx PATH "%PATH%;%INSTALL_DIR%" /M >nul 2>&1
echo.
color 0A
echo    [/] Installation Complete!
echo.
pause