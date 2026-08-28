import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import notepad


class FakeRoot:
    def __init__(self):
        self.title_text = ""

    def title(self, value):
        self.title_text = value


class FakeText:
    def __init__(self):
        self.content = ""

    def delete(self, *_args):
        self.content = ""

    def insert(self, _index, content):
        self.content = content

    def edit_reset(self):
        pass

    def edit_modified(self, _value=None):
        return False

    def get(self, *_args):
        return self.content


class FileIoTests(unittest.TestCase):
    def make_app(self):
        app = notepad.Notepad.__new__(notepad.Notepad)
        app.root = FakeRoot()
        app.text = FakeText()
        app.file_path = None
        app.dirty = False
        app.updating_text = False
        app.status_visible = False
        return app

    def test_loads_and_saves_file_with_spaces(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample file.txt"
            path.write_text("existing data", encoding="utf-8")
            app = self.make_app()

            self.assertTrue(app.load_file(path))
            self.assertEqual(app.text.content, "existing data")
            self.assertEqual(app.file_path, str(path.resolve()))
            self.assertEqual(app.root.title_text, "sample file.txt - Notepad")

            app.text.content = "updated data"
            app.dirty = True
            self.assertTrue(app.save_file())
            self.assertEqual(path.read_text(encoding="utf-8"), "updated data")
            self.assertFalse(app.dirty)

    def test_missing_file_reports_error(self):
        app = self.make_app()
        with patch.object(notepad.messagebox, "showerror") as showerror:
            self.assertFalse(app.load_file("missing file.txt"))
            showerror.assert_called_once()


if __name__ == "__main__":
    unittest.main()
