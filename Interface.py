import requests
import json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np
import gzip
from tkinter import *
from tkinter import messagebox
import os

file_dir = "\\".join(os.path.dirname(os.path.abspath(__file__)).split("\\")[0:]) + r"\Data-Files"


class Interface:

    def __init__(self, master):
        self.top_frame = Frame(master)
        self.top_frame.pack()
        self.middle_frame = Frame(master, bd=10)
        self.middle_frame.pack()
        self.bottom_frame = Frame(master, bd=10)
        self.bottom_frame.pack()
        # self.organ_list = ["Kidney", "Lip", "Ovary", "Skin", "Bladder", "Blood"]
        self.gdc_organ_list = self.get_GDC_organs()
        self.ccle_organ_list = self.get_CCLE_organs()
        self.selected_gdc_organ = None
        self.selected_ccle_organ = None
        self.title_frame()
        self.GDC_frame()
        self.CCLE_frame()
        self.notifications()

    def get_GDC_organs(self):
        with open(r"Info-Files\GDC Tissue Types.tsv", "r") as organ_file:
            for i in organ_file.readlines():
                organ_list = i.rstrip().split("\t")
        return organ_list

    def get_CCLE_organs(self):
        with open(r"Info-Files\CCLE Tissue Types.csv", "r") as organ_file:
            organ_list = []
            for i in organ_file.readlines()[1:]:
                organ_list.append(i.split(",")[0])
            return organ_list

    def title_frame(self):
        frame_1 = Frame(self.top_frame)
        frame_1.pack()
        w = Label(frame_1, text="Welcome to our application!", pady=5)
        w.pack()
        button_frame = Frame(frame_1)
        button_frame.pack()
        self.analyze_button = Button(button_frame, text="Analyze files", command=self.analyze)
        self.analyze_button.pack(side=LEFT)

    def GDC_frame(self):
        gdc_frame = Frame(self.middle_frame)
        gdc_frame.pack(side=LEFT)
        gdc_title = Label(gdc_frame, text="GDC Menu", pady=5)
        gdc_title.pack()
        gdc_buttons = Frame(gdc_frame)
        gdc_buttons.pack()
        query_button = Button(gdc_buttons, text="Query Tissue", command=self.query)
        query_button.pack(side=LEFT)
        gdc_organs = Frame(gdc_frame, bd=10)
        gdc_organs.pack()
        scrollbar = Scrollbar(gdc_organs, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)
        organ_menu_title = Label(gdc_organs, text="Tissue Options", pady=5)
        organ_menu_title.pack()
        self.gdc_listbox = Listbox(gdc_organs, width=40, height=5, yscrollcommand=scrollbar.set, selectmode=SINGLE)
        self.gdc_listbox.pack()
        scrollbar.config(command=self.gdc_listbox.yview)
        for organ in self.gdc_organ_list:
            self.gdc_listbox.insert(END, organ)

    def CCLE_frame(self):
        ccle_frame = Frame(self.middle_frame)
        ccle_frame.pack(side=LEFT)
        ccle_title = Label(ccle_frame, text="CCLE Menu", pady=5)
        ccle_title.pack()
        ccle_buttons = Frame(ccle_frame)
        ccle_buttons.pack()
        select_button = Button(ccle_buttons, text="Select Tissue", command=self.selection)
        select_button.pack(side=LEFT)
        ccle_organs = Frame(ccle_frame, bd=10)
        ccle_organs.pack()
        scrollbar = Scrollbar(ccle_organs, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)
        organ_menu_title = Label(ccle_organs, text="Tissue Options", pady=5)
        organ_menu_title.pack()
        self.ccle_listbox = Listbox(ccle_organs, width=40, height=5, yscrollcommand=scrollbar.set, selectmode=SINGLE)
        self.ccle_listbox.pack()
        scrollbar.config(command=self.ccle_listbox.yview)
        for organ in self.ccle_organ_list:
            self.ccle_listbox.insert(END, organ)

    def notifications(self):
        note_frame = Frame(self.bottom_frame, bd=5, relief=SUNKEN)
        note_frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(note_frame, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)
        note_title = Label(note_frame, text="Notifications", pady=5)
        note_title.pack()
        self.text_box = Text(note_frame, height=5, width=50, state=DISABLED, yscrollcommand=scrollbar.set)
        self.text_box.pack()
        scrollbar.config(command=self.text_box.yview)

    def query(self):
        if self.gdc_listbox.curselection():
            clicked_ind = self.gdc_listbox.curselection()[0]
            self.selected_gdc_organ = str(self.gdc_organ_list[clicked_ind])
            self.text_box.config(state="normal")
            self.text_box.insert(INSERT, self.selected_gdc_organ + " was selected!\n")
            self.text_box.config(state="disabled")
            self.query_obj = GDCQuery(self.selected_gdc_organ)
            resp, files = self.query_obj.query_files()
            self.text_box.config(state="normal")
            self.text_box.insert(INSERT, "Response: " + str(resp) + "\nFiles found: " + str(len(files)) + "\n")
            self.text_box.insert(INSERT, "Querying data...\n")
            self.text_box.config(state="disabled")
            result_text = self.query_obj.query_data(5)
            self.text_box.config(state="normal")
            self.text_box.insert(INSERT, result_text + "\n")
            self.text_box.config(state="disabled")
        else:
            self.text_box.config(state="normal")
            self.text_box.insert(INSERT, "No GDC tissue is selected.\n")
            self.text_box.config(state="disabled")

    def selection(self):
        if self.ccle_listbox.curselection():
            clicked_ind = self.ccle_listbox.curselection()[0]
            self.selected_ccle_organ = str(self.ccle_organ_list[clicked_ind])
            self.text_box.config(state="normal")
            self.text_box.insert(INSERT, self.selected_ccle_organ + " was selected!\n")
            self.text_box.config(state="disabled")
        else:
            self.text_box.config(state="normal")
            self.text_box.insert(INSERT, "No CCLE tissue is selected.\n")
            self.text_box.config(state="disabled")

    def analyze(self):
        if self.selected_gdc_organ and self.selected_ccle_organ:
            # self.query_button.config(state="disabled")
            self.analyze_button.config(state="disabled")
            self.root_2 = Tk()
            self.root_2.protocol("WM_DELETE_WINDOW", self.close_analyze)
            app_2 = Analyze(self.root_2, self.query_obj)
            self.root_2.mainloop()
        elif not self.selected_gdc_organ:
            self.text_box.config(state="normal")
            self.text_box.insert(INSERT, "No GDC tissue is selected.\n")
            self.text_box.config(state="disabled")
        elif not self.selected_ccle_organ:
            self.text_box.config(state="normal")
            self.text_box.insert(INSERT, "No CCLE tissue is selected.\n")
            self.text_box.config(state="disabled")

    def close_analyze(self):
        if messagebox.askokcancel("Quit", "Do you want to quit? All queried info will be lost."):
            self.root_2.destroy()
            self.analyze_button.config(state="normal")


class Analyze:

    def __init__(self, master, query_obj):

        self.query_object = query_obj
        self.files_left = len(query_obj.file_uuid_list)
        self.selected_file = ""
        self.top_frame = Frame(master, bd=10)
        self.top_frame.pack()
        self.bottom_frame = Frame(master, bd=10)
        self.bottom_frame.pack(side=BOTTOM)
        self.title_frame()
        self.file_frame()
        self.graph_frame()

    def title_frame(self):
        title_frame = Frame(self.top_frame)
        title_frame.pack()
        w = Label(title_frame, text="Welcome to our application!")
        w.pack()

    def file_frame(self):
        file_frame = Frame(self.bottom_frame, relief=RAISED, pady=5, bd=5)
        file_frame.pack(side=LEFT, fill=BOTH, expand=1)
        files_left = Label(file_frame, text=str(self.files_left) + " patient files left!", pady=5)
        files_left.pack()
        files_here = Label(file_frame, text="Patient data currently available:")
        files_here.pack()
        scrollbar = Scrollbar(file_frame, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)
        file_listbox = Listbox(file_frame, width=40, height=5, yscrollcommand=scrollbar.set, selectmode=SINGLE)
        file_listbox.pack()
        scrollbar.config(command=file_listbox.yview)
        for patient in self.query_object.data_list:
            patient_id = "".join([i for i in patient.keys()])
            file_listbox.insert(END, patient_id)
            # y = Label(file_frame, text=str(patient_id), pady=5)
            # y.pack()

    def graph_frame(self):
        graph_frame = Frame(self.bottom_frame, relief=RAISED, pady=5, bd=5)
        graph_frame.pack(side=LEFT)
        graph_title = Label(graph_frame, text="Gene Expression Graph", pady=5)
        graph_title.pack()
        fig = Figure(figsize=(5, 4), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

        canvas = FigureCanvasTkAgg(fig, master=graph_frame)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack()


class GDCQuery:

    def __init__(self, organ):
        self.files_endpt = "https://api.gdc.cancer.gov/files"
        self.organ = organ
        self.data_endpt = "https://api.gdc.cancer.gov/data"
        self.file_uuid_list = []
        self.data_list = list()

    def param_construct(self):
        filters = {
            "op": "and",
            "content":[
                {
                "op": "in",
                "content":{
                    "field": "files.access",
                    "value": ["open"]
                    }
                },
                {
                "op": "in",
                "content":{
                    "field": "files.analysis.workflow_type",
                    "value": ["HTSeq - Counts"]
                    }
                },
                {
                    "op": "in",
                    "content": {
                        "field": "files.cases.primary_site",
                        "value": [self.organ]
                    }
                },
                {
                    "op": "in",
                    "content":{
                        "field": "files.data_type",
                        "value": ["Gene Expression Quantification"]
                    }
                }
            ]
        }
        # Here a GET is used, so the filter parameters should be passed as a JSON string.

        params = {
            "filters": json.dumps(filters),
            "fields": "file_id",
            "format": "JSON",
            "size": "20"
            }
        return params

    def query_files(self):
        response = requests.get(self.files_endpt, params=self.param_construct())
        # This step populates the download list with the file_ids from the previous query
        for file_entry in json.loads(response.content.decode("utf-8"))["data"]["hits"]:
            self.file_uuid_list.append(file_entry["file_id"])

        return response, self.file_uuid_list

    def query_data(self, num_patients):
        if len(self.file_uuid_list) == 0:
            return "No data available!\n"
        else:
            sub_file_ids = self.file_uuid_list[:num_patients]
            for file_index, file_id in enumerate(sub_file_ids):
                self.file_uuid_list.remove(file_id)
                params = {"ids": file_id}
                response = requests.post(self.data_endpt, data=json.dumps(params), headers={"Content-Type": "application/json"})
                self.parse_data(response)
            return "Data from " + str(num_patients) + " files has been parsed!\n"

    def parse_data(self, response):
        response_head_cd = response.headers["Content-Disposition"]
        file_name = re.findall("filename=(.+)", response_head_cd)[0]
        file_path = os.path.join(file_dir, file_name)
        with open(file_path, "wb") as output_file:
            output_file.write(response.content)
        self.read_data(file_path, file_name)

    def read_data(self, filepath, filename):
        data_dict = dict()
        data_dict[filename] = {}
        with gzip.open(filepath, "rb") as gene_exp:
            for i in gene_exp.readlines():
                i_split = i.decode().split("\t")
                gene_id = i_split[0]
                gene_count = i_split[1]
                data_dict[filename][gene_id] = gene_count
        self.data_list.append(data_dict)
        os.remove(filepath)


root = Tk()
app = Interface(root)
root.mainloop()
