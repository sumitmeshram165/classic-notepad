@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=D:\anaconda3\python.exe"
if not exist "%PYTHON%" set "PYTHON=python"
if not exist "%PYTHON%" (
	echo Python was not found. Please install Python and try again.
	exit /b 1
)

echo Installing the small build tool if needed...
"%PYTHON%" -m pip install --user pyinstaller
if errorlevel 1 exit /b 1
"%PYTHON%" make_icon.py
if errorlevel 1 exit /b 1

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist notepad.spec del /q notepad.spec
if exist uninstall.spec del /q uninstall.spec
if exist setup.spec del /q setup.spec

echo Building ClassicNotepad.exe...
"%PYTHON%" -m PyInstaller --noconfirm --clean --onefile --windowed --manifest classic_notepad.manifest --icon classic_notepad.ico --name ClassicNotepad notepad.py
if errorlevel 1 exit /b 1

echo Building Uninstall.exe...
"%PYTHON%" -m PyInstaller --noconfirm --clean --onefile --windowed --manifest classic_notepad.manifest --icon classic_notepad.ico --name Uninstall uninstaller.py
if errorlevel 1 exit /b 1

echo Building Setup.exe...
"%PYTHON%" -m PyInstaller --noconfirm --clean --onefile --windowed --manifest classic_notepad.manifest --icon classic_notepad.ico --name Setup --add-binary "dist\ClassicNotepad.exe;." --add-binary "dist\Uninstall.exe;." installer.py
if errorlevel 1 exit /b 1

echo.
echo Finished. Give dist\Setup.exe to the user.
