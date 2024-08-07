@echo off
set SCRIPT_NAME=CrimsonSystemScanner.exe
set SHORTCUT_NAME=CrimsonSystemScanner.lnk
set ICON_PATH=%~dp0icon.ico

set TARGET_PATH=%~dp0%SCRIPT_NAME%
set DESKTOP_PATH=%USERPROFILE%\Desktop\%SHORTCUT_NAME%

powershell -command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%DESKTOP_PATH%');$s.TargetPath='%TARGET_PATH%';$s.IconLocation='%ICON_PATH%';$s.Save()"
