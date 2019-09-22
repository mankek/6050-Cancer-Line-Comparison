from tkinter import *
import os


class App:

    def __init__(self, master):

        frame_1 = Frame(master)
        frame_1.pack()
        w = Label(frame_1, text="Welcome to our application!")
        w.pack()

        frame = Frame(master)
        frame.pack()

        self.button = Button(
            frame, text="QUIT", fg="red", command=frame.quit
            )
        self.button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Open File Explorer", command=self.open_files)
        self.hi_there.pack(side=LEFT)

    @staticmethod
    def open_files():
        os.system("explorer C:\\")


root = Tk()

app = App(root)

root.mainloop()
