import shutil
import subprocess
import sys
import winreg
from pathlib import Path
from tkinter import messagebox
import tkinter as tk

APP_NAME = "Classic Notepad"
INSTALL_DIR = Path.home() / "AppData" / "Local" / "Classic Notepad"
START_MENU_DIR = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\ClassicNotepad"
TXT_KEY = r"Software\Classes\.txt"
PROG_ID_KEY = r"Software\Classes\ClassicNotepad.Text"
COMPATIBILITY_KEY = r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"


def bundled_file(name):
    return Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / name


def make_shortcut(target, shortcut):
    shortcut.parent.mkdir(parents=True, exist_ok=True)
    script = (
        "$ws = New-Object -ComObject WScript.Shell; "
        f"$s = $ws.CreateShortcut('{shortcut}'); "
        f"$s.TargetPath = '{target}'; "
        f"$s.WorkingDirectory = '{target.parent}'; "
        "$s.Save()"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True, creationflags=subprocess.CREATE_NO_WINDOW)


def register_uninstaller(uninstaller):
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY) as key:
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
        winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.0")
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Classic Notepad")
        winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(INSTALL_DIR))
        winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, str(uninstaller))
        winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)


def register_file_association(app):
    previous = ""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, TXT_KEY) as key:
            previous = winreg.QueryValueEx(key, "")[0]
    except FileNotFoundError:
        pass
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, PROG_ID_KEY + r"\shell\open\command") as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{app}" "%1"')
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, PROG_ID_KEY) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, APP_NAME)
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, TXT_KEY) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "ClassicNotepad.Text")
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY) as key:
        winreg.SetValueEx(key, "PreviousTxtAssociation", 0, winreg.REG_SZ, previous)


def remove_old_dpi_override(app):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, COMPATIBILITY_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, str(app))
    except FileNotFoundError:
        pass


def install():
    root = tk.Tk()
    root.withdraw()
    try:
        INSTALL_DIR.mkdir(parents=True, exist_ok=True)
        app = INSTALL_DIR / "ClassicNotepad.exe"
        uninstaller = INSTALL_DIR / "Uninstall.exe"
        remove_old_dpi_override(app)
        shutil.copy2(bundled_file("ClassicNotepad.exe"), app)
        shutil.copy2(bundled_file("Uninstall.exe"), uninstaller)
        make_shortcut(app, START_MENU_DIR / "Classic Notepad.lnk")
        register_file_association(app)
        register_uninstaller(uninstaller)
        messagebox.showinfo("Classic Notepad", "Classic Notepad was installed.")
    except (OSError, subprocess.SubprocessError, FileNotFoundError) as error:
        messagebox.showerror("Classic Notepad", f"Installation failed.\n\n{error}")
        raise SystemExit(1)
    finally:
        root.destroy()


if __name__ == "__main__":
    install()
