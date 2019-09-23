from tkinter import *
from tkinter import filedialog
import os


class App:

    def __init__(self, master):
        self.master = master
        self.chosen_files = []

        frame_1 = Frame(master)
        frame_1.pack()
        w = Label(frame_1, text="Welcome to our application!", pady=5)
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

        self.frame_2 = Frame(master, bd=10)
        self.frame_2.pack()
        scrollbar = Scrollbar(self.frame_2, orient=HORIZONTAL)
        scrollbar.pack(side=BOTTOM, fill=X)
        frame_2_title = Label(self.frame_2, text="Selected Files", pady=5)
        frame_2_title.pack()
        self.listbox = Listbox(self.frame_2, width=30, height=5, xscrollcommand=scrollbar.set)
        self.listbox.pack()
        scrollbar.config(command=self.listbox.xview)

    def open_files(self):
        filename = filedialog.askopenfilename(initialdir="C:\\", title="Select File")
        self.chosen_files.append(filename)
        self.listbox.insert(END, filename)

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
