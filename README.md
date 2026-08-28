# Classic Notepad

A small Windows notepad built with Python and Tkinter. It uses only the Python standard library at runtime, so the installed app needs no Python or Java.

## Build the installer

On Windows with Python installed, double-click `build_release.bat`. It installs the small PyInstaller build tool and creates:

- `dist\\Setup.exe`: the installer to distribute
- `dist\\ClassicNotepad.exe`: the standalone app
- `dist\\Uninstall.exe`: the uninstaller

Run `dist\\Setup.exe` to install Classic Notepad. It installs into your local user profile, creates a Start Menu shortcut, and adds an entry to Windows Apps. Use `Uninstall.exe` or Windows Settings to remove it.

## Run from source

Double-click `Run Notepad.bat`, or run:

```text
python notepad.py
```
To open an existing file from a terminal:

```text
python notepad.py "sample file.txt"
```

The app supports plain text editing, New/Open/Save/Save As, undo and redo, clipboard commands, word wrap, a status bar, F5 time/date, and zoom with Ctrl plus `+`, `-`, `0`, or the mouse wheel.

Run the file handling checks with:

```text
python -m unittest test_file_io.py
```
