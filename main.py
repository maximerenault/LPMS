import tkinter as tk
from GUI.drawingboard import DrawingBoard

if __name__=="__main__" :
    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    canv = DrawingBoard(root)

    root.mainloop()