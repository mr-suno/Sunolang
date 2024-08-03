@echo off

REM Removing All Aspects of Sunolang

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
echo    [~] Starting Removal Process
echo    [~] Prompting Administrator Access (IF required)
color 06
setlocal enabledelayedexpansion
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    goto UACPrompt
) else ( goto gotAdmin )
echo    [~] Creating Shell Application
:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~f0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B
:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"
echo    [~] Removing Installation Directory
set "INSTALL_DIR=%ProgramFiles%\Sunolang"
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%" 2>nul
    if errorlevel 1 (
        echo    [*] Failed to remove Sunolang directory.
        echo    [*] Please close any applications that might be using Sunolang and try again.
        goto end
    )
    echo.
    color 0A
    echo    [/] Sunolang has been uninstalled from your computer.
) else (
    echo.
    color 0C
    echo    [*] Sunolang does not exist on your computer!
)
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH') do set "PATH=%%B"
set "PATH=!PATH:%INSTALL_DIR%;=!"
setx PATH "%PATH%" /M >nul 2>&1
:end
echo.
pause