import tkinter as tk
from GUI.drawingboard import DrawingBoard
import ctypes
import os


class MainWindow(tk.Tk):

    def __init__(self) -> None:
        tk.Tk.__init__(self)
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
        pass

    def set_icons(self):
        icon16 = tk.PhotoImage(file="icons/LPMS_16.png")
        icon32 = tk.PhotoImage(file="icons/LPMS_32.png")
        icon48 = tk.PhotoImage(file="icons/LPMS_48.png")
        icon64 = tk.PhotoImage(file="icons/LPMS_64.png")
        icon128 = tk.PhotoImage(file="icons/LPMS_128.png")
        icon256 = tk.PhotoImage(file="icons/LPMS_256.png")
        self.iconphoto(False, icon16, icon32, icon48, icon64, icon128, icon256)

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
        for i, f in enumerate(self.recent_files[::-1]):
            if i == 0:
                menu_recent.add_command(
                    label=os.path.basename(f) + "          ctrl+o", command=lambda f=f: self.open_file(f)
                )
            else:
                menu_recent.add_command(label=os.path.basename(f), command=lambda f=f: self.open_file(f))

        menu_file.add_command(label="Open", command=self.open_file)
        menu_file.add_command(label="Save             ctrl+s", command=self.save_file)
        menu_file.add_command(label="Close           ctrl+x", command=self.close_file)
        self.bind("<Control-s>", lambda e, f=self.filename: self.save_file(f))
        self.bind("<Control-o>", lambda e: self.open_most_recent_file())
        self.bind("<Control-x>", lambda e: self.close_file())

    def read_recent_files(self):
        with open("recent_files.log", "r") as f:
            filename = f.readline().strip("\n")
            if filename == "":
                return
            self.add_recent_file(filename)
    
    def write_recent_files(self):
        with open("recent_files.log", "w") as f:
            for filename in self.recent_files:
                f.write(filename+"\n")

    def add_recent_file(self, filename=None):
        if filename is None:
            return
        for f in self.recent_files:
            if filename == f:
                self.recent_files.remove(f)
        self.recent_files.append(filename)
        if len(self.recent_files) > 10:
            del self.read_recent_files[0]
        self.set_menubars()

    def new_file(self):
        del self.drbd
        self.filename = None
        self.drbd = DrawingBoard(self)

    def open_most_recent_file(self):
        try:
            filename = self.recent_files[-1]
            self.open_file(filename)
        except:
            self.open_file()
        return

    def open_file(self, filename=None):
        self.filename = self.drbd.load(filename)
        self.add_recent_file(self.filename)
        self.write_recent_files()
        return

    def save_file(self, filename=None):
        self.filename = self.drbd.save(filename)
        self.add_recent_file(self.filename)
        self.write_recent_files()
        return

    def close_file(self):
        return


if __name__ == "__main__":
    root = MainWindow()
    root.mainloop()
