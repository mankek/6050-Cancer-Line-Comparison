from tkinter import *
from tkinter import filedialog
import os


class App:

    def __init__(self, master):
        self.master = master
        self.chosen_files = []

        frame_1 = Frame(master)
        frame_1.pack()
        w = Label(frame_1, text="Welcome to our application!")
        w.pack()

        button_frame = Frame(master)
        button_frame.pack()

        self.quit_button = Button(
            button_frame, text="QUIT", fg="red", command=button_frame.quit
            )
        self.quit_button.pack(side=LEFT)

        self.file_button = Button(button_frame, text="Open File Explorer", command=self.open_files)
        self.file_button.pack(side=LEFT)

        self.analyze_button = Button(button_frame, text="Analyze files", command=self.analyze)
        self.analyze_button.pack(side=LEFT)

        self.frame_2 = Frame(master)
        self.frame_2.pack()

    def open_files(self):
        filename = filedialog.askopenfilename(initialdir="C:\\", title="Select File")
        self.chosen_files.append(filename)
        v = Label(self.frame_2, text=filename)
        v.pack()

    def analyze(self):
        root_2 = Tk()
        app_2 = Analyze(self.chosen_files, root_2)
        root_2.mainloop()


class Analyze:

    def __init__(self, file_list, master):
        frame_1 = Frame(master)
        frame_1.pack()
        w = Label(frame_1, text="Welcome to our application!")
        w.pack()

        frame_2 = Frame(master)
        frame_2.pack()
        a = Label(frame_2, text=str(len(file_list)) + " files chosen!")
        a.pack()


root = Tk()
app = App(root)
root.mainloop()
