import requests
import json
import matplotlib.pyplot as plt
from CompareCPM import CCLE, Sample, GeneCompare
from lasso_selector_demo_sgskip import SelectFromCollection
import gzip
from tkinter import *
import tkinter
import os
import pandas
import numpy as np
import time
import random

# Path to the directory that holds downloaded GDC files
file_dir = "\\".join(os.path.dirname(os.path.abspath(__file__)).split("\\")[0:]) + r"\Data-Files"
if not os.path.exists(file_dir):
    os.mkdir(file_dir)


class Interface:
    """Creates the initial interface for tissue selection and analysis initiation.

    The interface has two menus. The left menu allows for selection of tissue for the query to the GDC database.
    The right menu allows for selection of tissue for data extraction from the local CCLE data. Tissue is selected
    via clicking within the textbox. Attempting to initialize analysis without both a GDC and CCLE tissue selected
    will fail. The Notification text box contains feedback on selection and querying, as well as any potential error
    messages.

    Parameters
    ----------
    master : :class:`tkinter.Tk`
            Tkinter root widget
    """

    def __init__(self, master):
        # defines behavior for quitting main interface window
        master.protocol("WM_DELETE_WINDOW", self.close_app)
        self.master = master
        # defines frames of interface
        self.top_frame = Frame(master)
        self.top_frame.pack()
        self.middle_frame = Frame(master, bd=10)
        self.middle_frame.pack()
        self.bottom_frame = Frame(master, bd=10)
        self.bottom_frame.pack()
        # extracts list of GDC and CCLE tissues for selection menus
        self.gdc_organ_list = self.get_GDC_organs()
        self.ccle_organ_list = self.get_CCLE_organs()
        # holds user-selected tissue values
        self.selected_gdc_organ = None
        self.selected_ccle_organ = None
        # initializes frames that hold content in interface
        self.title_frame()
        self.GDC_frame()
        self.CCLE_frame()
        self.notifications()
        # number of samples to query (user-chosen)
        self.num_samples = 0

    # If analysis window is open when closing main interface window, analysis window is also closed along with any plots
    def close_app(self):
        try:
            self.root_2.destroy()
            self.master.destroy()
            plt.close()
        except:
            self.master.destroy()

    # Extracts all GDC tissue types from file in Info-Files directory
    # File should be tab-separated file
    @staticmethod
    def get_GDC_organs():
        with open(r"Info-Files\GDC Tissue Types.tsv", "r") as organ_file:
            for i in organ_file.readlines():
                organ_list = i.rstrip().split("\t")
        return organ_list

    # Extracts all CCLE tissue types from file in Info-Files directory
    # File should be comma-separated file
    @staticmethod
    def get_CCLE_organs():
        with open(r"Info-Files\CCLE Tissue Types.csv", "r") as organ_file:
            organ_list = []
            for i in organ_file.readlines()[1:]:
                organ_list.append(i.split(",")[0])
            return organ_list

    # defines title frame
    # fills title frame with app title and analyze button
    def title_frame(self):
        frame_1 = Frame(self.top_frame)
        frame_1.pack()
        w = Label(frame_1, text="Welcome to our application!", pady=5)
        w.pack()
        button_frame = Frame(frame_1)
        button_frame.pack()
        self.analyze_button = Button(button_frame, text="Analyze files", command=self.analyze)
        self.analyze_button.pack(side=LEFT)

    # defines GDC menu frame
    # fills GDC menu frame with button for performing query and menu of selectable tissues
    def GDC_frame(self):
        gdc_frame = Frame(self.middle_frame)
        gdc_frame.pack(side=LEFT)
        gdc_title = Label(gdc_frame, text="GDC Menu", pady=5)
        gdc_title.pack()
        gdc_buttons = Frame(gdc_frame, pady=10)
        gdc_buttons.pack()
        query_button = Button(gdc_buttons, text="Query Tissue", command=self.query)
        query_button.pack(side=LEFT)
        gdc_options = Frame(gdc_frame)
        gdc_options.pack()
        num_label = Label(gdc_options, text="Select number of samples to Query")
        num_label.pack()
        num_samples = Scale(gdc_options, from_=0, to=20, orient=HORIZONTAL, command=self.get_sample_num)
        # num_samples.set(5)
        num_samples.pack()
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

    # defines CCLE menu frame
    # fills CCLE menu frame with button for extracting CCLE data and menu of selectable tissues
    def CCLE_frame(self):
        ccle_frame = Frame(self.middle_frame)
        ccle_frame.pack(side=LEFT)
        ccle_title = Label(ccle_frame, text="CCLE Menu", pady=5)
        ccle_title.pack()
        ccle_buttons = Frame(ccle_frame, pady=10)
        ccle_buttons.pack()
        select_button = Button(ccle_buttons, text="Select Tissue", command=self.selection)
        select_button.pack(side=LEFT)
        ccle_options = Frame(ccle_frame, height=60, pady=10)
        ccle_options.pack()
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

    # defines notification frame
    # fills notification frame with text box
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

    # if a GDC tissue has been selected
    # the user is notified and a GDCQuery object is created
    def query(self):
        if self.gdc_listbox.curselection():
            clicked_ind = self.gdc_listbox.curselection()[0]
            self.selected_gdc_organ = str(self.gdc_organ_list[clicked_ind])
            self.text_box.config(state="normal")
            self.text_box.insert(INSERT, self.selected_gdc_organ + " was selected!\n")
            self.text_box.config(state="disabled")
            self.query_obj = GDCQuery(self.selected_gdc_organ, self.num_samples)
            resp, files = self.query_obj.query_files()
            self.text_box.config(state="normal")
            self.text_box.insert(INSERT, "Response: " + str(resp) + "\nFiles found: " + str(len(files)) + "\n")
            self.text_box.insert(INSERT, "Querying data...\n")
            self.text_box.config(state="disabled")
            result_text = self.query_obj.query_data()
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
            self.ccle_object = CCLE(r"Info-Files\CCLE_RNAseq_genes_counts_20180929.gct", self.selected_ccle_organ)
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

    def get_sample_num(self, val):
        self.num_samples = val

    def close_analyze(self):
        self.root_2.destroy()
        plt.close()
        self.analyze_button.config(state="normal")


class Analyze:

    def __init__(self, master, query_obj, ccle_object):
        self.master = master
        self.query_object = query_obj
        self.ccle_object = ccle_object
        self.compare_obj = GeneCompare(self.query_object.data_dict, self.ccle_object)
        self.num_components = 2
        self.chosen_comp_1 = StringVar(master)
        self.chosen_comp_1.set("1")
        self.chosen_comp_2 = StringVar(master)
        self.chosen_comp_2.set("2")
        # self.comp_options = [str(i) for i in range(1, (self.num_components + 1))]
        self.compare_obj.calcPCA(self.num_components)
        self.top_frame = Frame(master, bd=10)
        self.top_frame.pack()
        self.bottom_frame = Frame(master, bd=10)
        self.bottom_frame.pack(side=BOTTOM)
        self.report_menu()
        self.title_frame()
        # self.analysis()
        self.pca_frame()

    def report_menu(self):
        report_menu = Menu(self.master)
        report_submenu = Menu(report_menu, tearoff=False)
        report_submenu.add_command(label="Report Option 1")
        report_menu.add_cascade(label="Report Options", menu=report_submenu)
        self.master.config(menu=report_menu)

    def title_frame(self):
        title_frame = Frame(self.top_frame)
        title_frame.pack()
        w = Label(title_frame, text="Welcome to our application!")
        w.pack()
        menu_frame = Frame(self.top_frame)
        menu_frame.pack()
        scale_label = Label(menu_frame, text="Number of PCA Components")
        scale_label.pack()
        num_components_scale = Scale(menu_frame, from_=2, to=6, orient=HORIZONTAL, command=self.change_num_components)
        num_components_scale.set(2)
        num_components_scale.pack()
        select_label = Label(menu_frame, text="Select the Graphed Components")
        select_label.pack()
        comp_options = [str(i) for i in range(1, 3)]
        self.comp_1 = OptionMenu(menu_frame, self.chosen_comp_1, *tuple(comp_options))
        self.comp_1.pack(side=LEFT)
        self.comp_2 = OptionMenu(menu_frame, self.chosen_comp_2, *tuple(comp_options))
        self.comp_2.pack(side=LEFT)
        num_button = Button(menu_frame, text="Generate Graphs", command=self.analysis)
        num_button.pack(side=BOTTOM)

    def pca_frame(self):
        pca_frame = Frame(self.bottom_frame, relief=RAISED, pady=5, bd=5)
        pca_frame.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar = Scrollbar(pca_frame, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.component_listbox = Listbox(pca_frame, width=40, height=5, yscrollcommand=scrollbar.set, selectmode=SINGLE)
        self.component_listbox.pack()
        scrollbar.config(command=self.component_listbox.yview)
        for index, percentage in enumerate(np.nditer(self.compare_obj.percVar)):
            self.component_listbox.insert(END, "PC " + str(index + 1) + " - Percent Variance: " + str(percentage))

    def change_num_components(self, val):
        self.compare_obj.calcPCA(int(val))
        self.comp_1["menu"].delete(0, "end")
        self.comp_2["menu"].delete(0, "end")
        for i in range(1, (int(val) + 1)):
            self.comp_1["menu"].add_command(label=str(i), command=lambda value=str(i): self.chosen_comp_1.set(value))
            self.comp_2["menu"].add_command(label=str(i), command=lambda value=str(i): self.chosen_comp_2.set(value))
        self.component_listbox.delete(0, "end")
        for index, percentage in enumerate(np.nditer(self.compare_obj.percVar)):
            self.component_listbox.insert(END, "PC " + str(index + 1) + " Percent Variance: " + str(percentage))

    def analysis(self):
        self.create_graph(self.compare_obj.PCA, int(self.chosen_comp_1.get()), int(self.chosen_comp_2.get()))

    def create_graph(self, df_in, comp_1, comp_2):
        plt.close()
        comp_1 = "PC" + str(comp_1)
        comp_2 = "PC" + str(comp_2)
        self.fig, self.ax = plt.subplots()
        pts = self.ax.scatter(df_in[comp_1], df_in[comp_2])
        self.selector = SelectFromCollection(self.ax, pts)
        self.fig.canvas.mpl_connect("key_press_event", self.accept)
        self.ax.set_title("Press enter to accept selected points")
        plt.xlabel(comp_1)
        plt.ylabel(comp_2)
        plt.show()

    def accept(self, event):
        comp_1 = "PC" + str(self.chosen_comp_1.get())
        comp_2 = "PC" + str(self.chosen_comp_2.get())
        if event.key == "enter":
            print("Selected points:")
            print(self.compare_obj.co_PCA(comp_1, comp_2, self.selector.xys[self.selector.ind]))
            # self.selector.disconnect()
            self.ax.set_title("")
            self.fig.canvas.draw()


class GDCQuery:

    def __init__(self, organ, num_samples):
        self.files_endpt = "https://api.gdc.cancer.gov/files"
        self.organ = organ
        self.data_endpt = "https://api.gdc.cancer.gov/data"
        self.file_uuid_list = []
        self.data_dict = dict()
        self.num_samples = num_samples

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
            "size": str(self.num_samples)
            }
        return params

    def query_files(self):
        response = requests.get(self.files_endpt, params=self.param_construct())
        # This step populates the download list with the file_ids from the previous query
        for file_entry in json.loads(response.content.decode("utf-8"))["data"]["hits"]:
            self.file_uuid_list.append(file_entry["file_id"])
        return response, self.file_uuid_list

    def query_data(self):
        if len(self.file_uuid_list) == 0:
            return "No data available!\n"
        else:
            num_patients = len(self.file_uuid_list)
            #     num_patients = len(self.file_uuid_list)
            # sub_file_ids = self.file_uuid_list[:num_patients]
            for file_index, file_id in enumerate(self.file_uuid_list):
                time.sleep(0.001)
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
                else:
                    continue
        file_data = pandas.DataFrame(self.data_dict[filename], index=self.data_dict[filename]["gene_id"])
        self.data_dict[filename] = Sample(filename, file_data)
        os.remove(filepath)


root = Tk()
app = Interface(root)
root.mainloop()
