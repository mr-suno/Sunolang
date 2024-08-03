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
   "%temp%\getadmin.vbs"
   exit /B
:gotAdmin
   if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
   pushd "%CD%"
   CD /D "%~dp0"
echo    [~] Installing Direcotires (IF required)
setlocal enabledelayedexpansion
set "INSTALL_DIR=%ProgramFiles%\Sunolang"
set "BUILD_DIR=%~dp0build"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%" >nul 2>&1
>nul echo @echo off > "%INSTALL_DIR%\su.bat"
>>nul echo python "%%~dp0sunolang.py" %%* >> "%INSTALL_DIR%\su.bat"
if not exist "%BUILD_DIR%\basic.py" (
   exit /b 1
)
if not exist "%BUILD_DIR%\sunolang.py" (
   exit /b 1
)
echo    [~] Copying Files
>nul copy "%BUILD_DIR%\basic.py" "%INSTALL_DIR%\basic.py"
>nul copy "%BUILD_DIR%\sunolang.py" "%INSTALL_DIR%\sunolang.py"
echo    [~] Configuring in PATH
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH') do set "CURRENT_PATH=%%B"
if not "!CURRENT_PATH:~-1!"==";" set "CURRENT_PATH=!CURRENT_PATH!;"
if "!CURRENT_PATH:%INSTALL_DIR%=!"=="!CURRENT_PATH!" (
   >nul 2>&1 setx PATH "!CURRENT_PATH!%INSTALL_DIR%;" /M
)
echo.
color 0A
echo    [/] Installation Complete!
echo.
pause