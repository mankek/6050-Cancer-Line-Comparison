import requests
import json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from CompareTPM import GeneFrame, GeneList, CCLE, Sample
from matplotlib.figure import Figure
import numpy as np
import gzip
from tkinter import *
from tkinter import messagebox
import os
import pandas

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
            self.ccle_object = CCLE("Info-Files\CCLE_RNAseq_rsem_genes_tpm_20180929.txt", self.selected_ccle_organ)
        else:
            self.text_box.config(state="normal")
            self.text_box.insert(INSERT, "No CCLE tissue is selected.\n")
            self.text_box.config(state="disabled")

    def analyze(self):
        if self.selected_gdc_organ and self.selected_ccle_organ and (len(self.query_obj.file_uuid_list) != 0):
            # self.query_button.config(state="disabled")
            self.analyze_button.config(state="disabled")
            self.root_2 = Tk()
            self.root_2.protocol("WM_DELETE_WINDOW", self.close_analyze)
            app_2 = Analyze(self.root_2, self.query_obj, self.ccle_object)
            self.root_2.mainloop()
        elif not self.selected_gdc_organ:
            self.text_box.config(state="normal")
            self.text_box.insert(INSERT, "No GDC tissue is selected.\n")
            self.text_box.config(state="disabled")
        elif not self.selected_ccle_organ:
            self.text_box.config(state="normal")
            self.text_box.insert(INSERT, "No CCLE tissue is selected.\n")
            self.text_box.config(state="disabled")
        elif len(self.query_obj.file_uuid_list) == 0:
            self.text_box.config(state="normal")
            self.text_box.insert(INSERT, "No GDC data available.\n")
            self.text_box.config(state="disabled")

    def close_analyze(self):
        if messagebox.askokcancel("Quit", "Do you want to quit? All queried info will be lost."):
            self.root_2.destroy()
            self.analyze_button.config(state="normal")


class Analyze:

    def __init__(self, master, query_obj, ccle_object):

        self.query_object = query_obj
        self.ccle_object = ccle_object
        self.files_left = len(query_obj.file_uuid_list)
        self.selected_file = ""
        self.selected_cor = ""
        self.top_frame = Frame(master, bd=10)
        self.top_frame.pack()
        self.bottom_frame = Frame(master, bd=10)
        self.bottom_frame.pack(side=BOTTOM)
        self.title_frame()
        self.file_frame()
        self.graphs_frame()
        self.analysis()

    def title_frame(self):
        title_frame = Frame(self.top_frame)
        title_frame.pack()
        w = Label(title_frame, text="Welcome to our application!")
        w.pack()

    def file_frame(self):
        file_frame = Frame(self.bottom_frame, relief=RAISED, pady=5, bd=5)
        file_frame.pack(side=LEFT, fill=BOTH, expand=1)

        patient_frame = Frame(file_frame)
        patient_frame.pack()
        files_left = Label(patient_frame, text=str(self.files_left) + " patient files left!", pady=5)
        files_left.pack()
        files_here = Label(patient_frame, text="Patient data currently available:")
        files_here.pack()
        scrollbar = Scrollbar(patient_frame, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.file_listbox = Listbox(patient_frame, width=50, height=5, yscrollcommand=scrollbar.set, selectmode=SINGLE)
        self.file_listbox.pack()
        scrollbar.config(command=self.file_listbox.yview)
        for patient in self.query_object.data_dict.keys():
            # patient_id = "".join([i for i in patient.keys()])
            self.file_listbox.insert(END, patient)

        button_frame = Frame(file_frame, pady=10)
        button_frame.pack()
        add_button = Button(button_frame, text="Add 5 more patients")
        add_button.pack(side=LEFT)
        analyze_button = Button(button_frame, text="Generate Graphs", command=self.analysis)
        analyze_button.pack(side=LEFT)

        line_frame = Frame(file_frame, pady=10)
        line_frame.pack()
        line_data = Label(line_frame, text="Cancer Cell Line and Correlation Statistics")
        line_data.pack()
        scrollbar = Scrollbar(line_frame, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.line_listbox = Listbox(line_frame, width=50, height=5)
        self.line_listbox.pack()
        scrollbar.config(command=self.line_listbox.yview)
        # for number in range(0, 5):
        #     line_listbox.insert(END, number)

    def choose_patient(self):
        if self.file_listbox.curselection():
            clicked_ind = self.file_listbox.curselection()[0]
            self.selected_file = self.file_listbox.get(clicked_ind)
        else:
            self.file_listbox.activate(1)
            self.selected_file = self.file_listbox.get(1)

    def choose_cor(self):
        if self.line_listbox.curselection():
            clicked_ind = self.line_listbox.curselection()[0]
            self.selected_cor = self.line_listbox.get(clicked_ind)
        else:
            self.line_listbox.activate(2)
            self.selected_cor = self.line_listbox.get(2)

    def analysis(self):
        self.choose_patient()
        gene_list = GeneList("Info-Files/Gene_List.csv")
        sample_df = self.query_object.data_dict[self.selected_file]
        sample_obj = Sample(self.selected_file, sample_df, gene_list)
        sample_obj.compareCCLE(self.ccle_object)
        self.correlation(sample_obj.cor)
        self.choose_cor()
        self.create_graph(sample_obj.df, self.selected_cor)

    def graphs_frame(self, fig=None):
        self.graph_frame = Frame(self.bottom_frame, relief=RAISED, pady=5, bd=5)
        self.graph_frame.pack(side=LEFT)
        graph_title = Label(self.graph_frame, text="Gene Expression Graph", pady=5)
        graph_title.pack()
        # t = np.arange(0, 3, .01)
        # fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))
        if fig:
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)  # A tk.DrawingArea.
            canvas.draw()
            canvas.get_tk_widget().pack()
            toolbar = NavigationToolbar2Tk(canvas, self.graph_frame)
            toolbar.update()
            canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    def create_graph(self, df_in, sel_cor):
        self.graph_frame.destroy()
        fig = Figure(figsize=(5, 4), dpi=100)
        tissue = sel_cor.split(" ")[0]
        fig.add_subplot(111).scatter(df_in[tissue], df_in["tpm"])
        self.graphs_frame(fig)

    def correlation(self, df_in):
        for i, r in df_in.iterrows():
            entry = str(r[0]) + " " + str(r[1]) + " " + str(r[2])
            # print(r)
            self.line_listbox.insert(END, entry)


class GDCQuery:

    def __init__(self, organ):
        self.files_endpt = "https://api.gdc.cancer.gov/files"
        self.organ = organ
        self.data_endpt = "https://api.gdc.cancer.gov/data"
        self.file_uuid_list = []
        self.data_dict = dict()

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
            if num_patients > len(self.file_uuid_list):
                num_patients = len(self.file_uuid_list)
            sub_file_ids = self.file_uuid_list[:num_patients]
            for file_index, file_id in enumerate(sub_file_ids):
                self.file_uuid_list.remove(file_id)
                params = {"ids": file_id}
                response = requests.post(self.data_endpt, data=json.dumps(params), headers={"Content-Type": "application/json"})
                if response.status_code != 200:
                    num_patients = num_patients - 1
                    continue
                else:
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
        self.data_dict[filename] = {"gene_id": [], "gene_count": []}
        with gzip.open(filepath, "rb") as gene_exp:
            for i in gene_exp.readlines():
                i_split = i.decode().split("\t")
                gene_id = i_split[0].split(".")[0]  # ensemble gene ID without version number
                if gene_id.startswith("E"):
                    gene_count = i_split[1].rstrip()
                    self.data_dict[filename]["gene_id"].append(gene_id)
                    self.data_dict[filename]["gene_count"].append(int(gene_count))
                    # data_dict[filename][gene_id] = gene_count
                else:
                    continue
        file_data = pandas.DataFrame(self.data_dict[filename], index=self.data_dict[filename]["gene_id"])
        self.data_dict[filename] = file_data
        # self.data_list.append(data_dict)
        os.remove(filepath)


root = Tk()
app = Interface(root)
root.mainloop()
