import tkinter as tk
from GUI.drawingboard import DrawingBoard
import ctypes
import os


class MainWindow(tk.Tk):

    ICON_PATHS = [
        "icons/LPMS_16.png",
        "icons/LPMS_32.png",
        "icons/LPMS_48.png",
        "icons/LPMS_64.png",
        "icons/LPMS_128.png",
        "icons/LPMS_256.png",
    ]
    RECENT_FILES_LOG = "recent_files.log"
    MAX_RECENT_FILES = 10

    def __init__(self) -> None:
        super().__init__()
        self.title("LPMS")

        myappid = "LPMS.0.1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.drbd = DrawingBoard(self)
        self.recent_files = []
        self.filename = None
        self.read_recent_files()
        self.set_icons()
        self.set_menubars()

    def set_icons(self):
        icons = [tk.PhotoImage(file=path) for path in self.ICON_PATHS]
        self.iconphoto(False, *icons)

    def set_menubars(self):
        self.option_add("*tearOff", False)
        menubar = tk.Menu(self)
        self["menu"] = menubar
        menu_file = tk.Menu(menubar)
        menu_edit = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label="File")
        menubar.add_cascade(menu=menu_edit, label="Edit")

        menu_file.add_command(label="New", command=self.new_file)
        menu_recent = tk.Menu(menu_file)
        menu_file.add_cascade(menu=menu_recent, label="Open Recent")
        for i, f in enumerate(reversed(self.recent_files)):
            accelerator = "Ctrl+o" if i == 0 else None
            menu_recent.add_command(
                label=os.path.basename(f), command=lambda f=f: self.open_file(f), accelerator=accelerator
            )

        menu_file.add_command(label="Open", command=self.open_file)
        menu_file.add_command(label="Save", command=self.save_file, accelerator="Ctrl+s")
        menu_file.add_command(label="Close", command=self.close_file, accelerator="Ctrl+x")
        self.bind("<Control-s>", lambda e: self.save_file(self.filename))
        self.bind("<Control-o>", lambda e: self.open_most_recent_file())
        self.bind("<Control-x>", lambda e: self.close_file())

    def read_recent_files(self):
        if os.path.exists(self.RECENT_FILES_LOG):
            with open(self.RECENT_FILES_LOG, "r") as f:
                self.recent_files = [line.strip() for line in f if line.strip()]
        self.recent_files = list(set(self.recent_files))

    def write_recent_files(self):
        with open(self.RECENT_FILES_LOG, "w") as f:
            for filename in self.recent_files:
                f.write(filename + "\n")

    def add_recent_file(self, filename=None):
        if filename and filename not in self.recent_files:
            self.recent_files.append(filename)
        if len(self.recent_files) > self.MAX_RECENT_FILES:
            self.recent_files = self.recent_files[-self.MAX_RECENT_FILES :]
        self.set_menubars()

    def new_file(self):
        self.drbd.destroy()
        self.filename = None
        self.drbd = DrawingBoard(self)

    def open_most_recent_file(self):
        if self.recent_files:
            self.open_file(self.recent_files[-1])
        else:
            self.open_file()

    def open_file(self, filename=None):
        self.drbd.destroy()
        self.drbd = DrawingBoard(self)
        self.filename = self.drbd.load(filename)
        self.add_recent_file(self.filename)
        self.write_recent_files()

    def save_file(self, filename=None):
        self.filename = self.drbd.save(filename)
        self.add_recent_file(self.filename)
        self.write_recent_files()

    def close_file(self):
        # Placeholder for actual close file logic
        pass


if __name__ == "__main__":
    root = MainWindow()
    root.mainloop()
