import ctypes
import sys
from pathlib import Path


def enable_windows_dpi_awareness():
    if sys.platform != "win32":
        return
    try:
        set_dpi_context = ctypes.windll.user32.SetProcessDpiAwarenessContext
        set_dpi_context.argtypes = [ctypes.c_void_p]
        set_dpi_context.restype = ctypes.c_bool
        if set_dpi_context(ctypes.c_void_p(-4)):
            return
    except (AttributeError, OSError):
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


enable_windows_dpi_awareness()

import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox


class Notepad:
    def __init__(self, root):
        self.root = root
        self.file_path = None
        self.word_wrap = True
        self.status_visible = True
        self.dirty = False
        self.updating_text = False
        self.font_size = 11

        self.app_icon = tk.PhotoImage(width=16, height=16)
        self.app_icon.put("#2f6690", to=(0, 0, 16, 16))
        self.app_icon.put("#ffffff", to=(3, 2, 13, 14))
        self.app_icon.put("#e8eef2", to=(4, 3, 12, 4))
        self.app_icon.put("#2f6690", to=(5, 7, 11, 8))
        self.app_icon.put("#2f6690", to=(5, 10, 11, 11))
        root.iconphoto(True, self.app_icon)

        root.geometry("860x560")
        root.minsize(420, 260)
        root.protocol("WM_DELETE_WINDOW", self.exit_app)

        self.text_font = tkfont.Font(root, family="Consolas", size=self.font_size)
        editor_frame = tk.Frame(root)
        editor_frame.pack(fill="both", expand=True)

        self.text = tk.Text(
            editor_frame,
            undo=True,
            wrap="word",
            font=self.text_font,
            padx=8,
            pady=6,
            borderwidth=0,
            highlightthickness=0,
        )
        self.scrollbar = tk.Scrollbar(editor_frame, orient="vertical", command=self.text.yview)
        self.text.config(yscrollcommand=self.update_scrollbar)
        self.text.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.text.focus_set()
        self.text.bind("<<Modified>>", self.on_modified)
        self.text.bind("<KeyRelease>", self.update_status)
        self.text.bind("<ButtonRelease-1>", self.update_status)

        self.status = tk.Label(root, anchor="w", padx=8, pady=3, relief="sunken")
        self.status.pack(fill="x", side="bottom")

        self.build_menu()
        self.set_text("")
        self.update_title()
        self.update_status()

    def update_scrollbar(self, first, last):
        self.scrollbar.set(first, last)
        if float(first) <= 0 and float(last) >= 1:
            self.scrollbar.pack_forget()
        elif not self.scrollbar.winfo_ismapped():
            self.scrollbar.pack(side="right", fill="y")

    def load_file(self, path):
        path = Path(path).expanduser()
        try:
            content = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            messagebox.showerror("Notepad", f"Could not open the file.\n\n{error}")
            return False
        self.file_path = str(path.resolve())
        self.set_text(content)
        self.update_title()
        self.update_status()
        return True

    def build_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menu_bar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menu_bar, tearoff=False)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X", command=self.cut)
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C", command=self.copy)
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V", command=self.paste)
        edit_menu.add_command(label="Delete", accelerator="Del", command=self.delete)
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", accelerator="Ctrl+A", command=self.select_all)
        edit_menu.add_command(label="Time/Date", accelerator="F5", command=self.insert_time_date)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        format_menu = tk.Menu(menu_bar, tearoff=False)
        self.wrap_var = tk.BooleanVar(value=self.word_wrap)
        format_menu.add_checkbutton(
            label="Word Wrap", onvalue=True, offvalue=False,
            variable=self.wrap_var, command=self.toggle_word_wrap,
        )
        menu_bar.add_cascade(label="Format", menu=format_menu)

        view_menu = tk.Menu(menu_bar, tearoff=False)
        self.status_var = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Status Bar", variable=self.status_var, command=self.toggle_status)
        menu_bar.add_cascade(label="View", menu=view_menu)

        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-y>", lambda event: self.redo())
        self.root.bind("<Control-a>", lambda event: self.select_all())
        self.root.bind("<F5>", lambda event: self.insert_time_date())
        self.root.bind_all("<Control-KeyPress-equal>", lambda event: self.zoom_in())
        self.root.bind_all("<Control-KeyPress-plus>", lambda event: self.zoom_in())
        self.root.bind_all("<Control-KeyPress-minus>", lambda event: self.zoom_out())
        self.root.bind_all("<Control-KeyPress-0>", lambda event: self.reset_zoom())
        self.root.bind_all("<Control-MouseWheel>", self.zoom_with_wheel)

    def on_modified(self, _event=None):
        if self.updating_text:
            self.text.edit_modified(False)
            return
        if self.text.edit_modified():
            self.dirty = True
            self.update_title()
            self.update_status()
            self.text.edit_modified(False)

    def set_text(self, content):
        self.updating_text = True
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.edit_reset()
        self.text.edit_modified(False)
        self.updating_text = False
        self.dirty = False

    def update_title(self):
        name = Path(self.file_path).name if self.file_path else "Untitled"
        marker = "*" if self.dirty else ""
        self.root.title(f"{marker}{name} - Notepad")

    def update_status(self, _event=None):
        if not self.status_visible:
            return
        line, column = self.text.index("insert").split(".")
        self.status.config(text=f"Ln {line}, Col {int(column) + 1}")

    def ask_save(self):
        if not self.dirty:
            return True
        answer = messagebox.askyesnocancel("Notepad", "Do you want to save changes?")
        if answer is None:
            return False
        return self.save_file() if answer else True

    def new_file(self):
        if not self.ask_save():
            return "break"
        self.file_path = None
        self.set_text("")
        self.update_title()
        self.update_status()
        return "break"

    def open_file(self):
        if not self.ask_save():
            return "break"
        selected = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not selected:
            return "break"
        self.load_file(selected)
        return "break"

    def save_file(self):
        if not self.file_path:
            return self.save_as()
        return self.write_file(self.file_path)

    def save_as(self):
        selected = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not selected:
            return False
        self.file_path = selected
        return self.write_file(selected)

    def write_file(self, path):
        try:
            Path(path).write_text(self.text.get("1.0", "end-1c"), encoding="utf-8")
        except OSError as error:
            messagebox.showerror("Notepad", f"Could not save the file.\n\n{error}")
            return False
        self.dirty = False
        self.update_title()
        return True

    def exit_app(self):
        if self.ask_save():
            self.root.destroy()

    def toggle_word_wrap(self):
        self.word_wrap = self.wrap_var.get()
        self.text.config(wrap="word" if self.word_wrap else "none")

    def toggle_status(self):
        self.status_visible = self.status_var.get()
        if self.status_visible:
            self.status.pack(fill="x", side="bottom")
            self.update_status()
        else:
            self.status.pack_forget()

    def set_zoom(self, size):
        self.font_size = max(6, min(36, size))
        self.text_font.config(size=self.font_size)

    def zoom_in(self):
        self.set_zoom(self.font_size + 1)
        return "break"

    def zoom_out(self):
        self.set_zoom(self.font_size - 1)
        return "break"

    def reset_zoom(self):
        self.set_zoom(11)
        return "break"

    def zoom_with_wheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        elif event.delta < 0:
            self.zoom_out()
        return "break"

    def undo(self):
        try:
            self.text.edit_undo()
        except tk.TclError:
            pass
        return "break"

    def redo(self):
        try:
            self.text.edit_redo()
        except tk.TclError:
            pass
        return "break"

    def cut(self):
        self.text.event_generate("<<Cut>>")
        return "break"

    def copy(self):
        self.text.event_generate("<<Copy>>")
        return "break"

    def paste(self):
        self.text.event_generate("<<Paste>>")
        return "break"

    def delete(self):
        try:
            self.text.delete("sel.first", "sel.last")
        except tk.TclError:
            pass
        return "break"

    def select_all(self):
        self.text.tag_add("sel", "1.0", "end-1c")
        self.text.mark_set("insert", "1.0")
        self.text.see("insert")
        return "break"

    def insert_time_date(self):
        import datetime
        self.text.insert("insert", datetime.datetime.now().strftime("%H:%M %d/%m/%Y"))
        return "break"


def main():
    root = tk.Tk()
    app = Notepad(root)
    if len(sys.argv) > 1 and sys.argv[1].strip():
        app.load_file(sys.argv[1])
    root.mainloop()


if __name__ == "__main__":
    main()
