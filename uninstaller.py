import shutil
import subprocess
import sys
import winreg
from pathlib import Path
from tkinter import messagebox
import tkinter as tk

APP_NAME = "Classic Notepad"
INSTALL_DIR = Path.home() / "AppData" / "Local" / "Classic Notepad"
SHORTCUT = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Classic Notepad.lnk"
UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\ClassicNotepad"
TXT_KEY = r"Software\Classes\.txt"
PROG_ID_KEY = r"Software\Classes\ClassicNotepad.Text"


def remove_registry_entry():
    previous = ""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY) as key:
            previous = winreg.QueryValueEx(key, "PreviousTxtAssociation")[0]
    except FileNotFoundError:
        pass
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, TXT_KEY) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, previous)
    except OSError:
        pass
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, PROG_ID_KEY + r"\shell\open\command")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, PROG_ID_KEY + r"\shell\open")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, PROG_ID_KEY + r"\shell")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, PROG_ID_KEY)
    except FileNotFoundError:
        pass
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY)
    except FileNotFoundError:
        pass


def remove_install_folder():
    folder = str(INSTALL_DIR).replace("'", "''")
    command = f"Start-Sleep -Milliseconds 600; Remove-Item -LiteralPath '{folder}' -Recurse -Force"
    subprocess.Popen(
        ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", command],
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def uninstall():
    root = tk.Tk()
    root.withdraw()
    try:
        if messagebox.askyesno("Classic Notepad", "Uninstall Classic Notepad?"):
            SHORTCUT.unlink(missing_ok=True)
            remove_registry_entry()
            remove_install_folder()
            messagebox.showinfo("Classic Notepad", "Classic Notepad was uninstalled.")
    finally:
        root.destroy()


if __name__ == "__main__":
    uninstall()
