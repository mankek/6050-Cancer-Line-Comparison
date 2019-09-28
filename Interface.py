import requests
import json
import re
import gzip
from tkinter import *
# from tkinter import filedialog
import os


class Interface:

    def __init__(self, master):
        self.master = master
        self.organ_list = ["Kidney", "Lip", "Ovary", "Skin", "Bladder", "Blood"]
        self.selected_organ = ""
        self.title_frame()
        self.button_menu()
        self.organ_menu()
        self.notifications()

    def title_frame(self):
        frame_1 = Frame(self.master)
        frame_1.pack()
        w = Label(frame_1, text="Welcome to our application!", pady=5)
        w.pack()

    def button_menu(self):
        button_frame = Frame(self.master)
        button_frame.pack()
        quit_button = Button(
            button_frame, text="QUIT", fg="red", command=button_frame.quit
            )
        quit_button.pack(side=LEFT)
        query_button = Button(button_frame, text="Query files", command=self.query)
        query_button.pack(side=LEFT)
        analyze_button = Button(button_frame, text="Analyze files", command=self.analyze)
        analyze_button.pack(side=LEFT)

    def organ_menu(self):
        frame_2 = Frame(self.master, bd=10)
        frame_2.pack()
        scrollbar = Scrollbar(frame_2, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)
        frame_2_title = Label(frame_2, text="Organ Options", pady=5)
        frame_2_title.pack()
        self.listbox = Listbox(frame_2, height=5, yscrollcommand=scrollbar.set, selectmode=SINGLE)
        self.listbox.pack()
        scrollbar.config(command=self.listbox.yview)
        for organ in self.organ_list:
            self.listbox.insert(END, organ)
        # self.listbox.bind("<Button-1>", self.notify_organ_selection)

    def notifications(self):
        frame_3 = Frame(self.master, bd=10)
        frame_3.pack()
        frame_3_title = Label(frame_3, text="Notifications", pady=5)
        frame_3_title.pack()
        self.text_box = Text(frame_3, height=5, width=30)
        self.text_box.pack()

    # def notify_organ_selection(self, event):
    #     clicked_ind = self.listbox.curselection()
    #     print(clicked_ind)
        # self.selected_organ = str(self.organ_list[clicked_ind])

    def query(self):
        clicked_ind = self.listbox.curselection()[0]
        self.selected_organ = str(self.organ_list[clicked_ind])
        query_obj = GDCQuery(self.selected_organ)
        self.text_box.insert(INSERT, self.selected_organ + " was selected and query has begun!\n")
        resp, files = query_obj.query_files()
        self.text_box.insert(INSERT, "Response: " + str(resp) + "\nFiles found: " + str(len(files)))
        # query_obj.query_data(5)

    def analyze(self):
        root_2 = Tk()
        app_2 = Analyze(root_2)
        root_2.mainloop()


class Analyze:

    def __init__(self, master):
        frame_1 = Frame(master)
        frame_1.pack()
        w = Label(frame_1, text="Welcome to our application!")
        w.pack()

class GDCQuery:

    def __init__(self, organ):
        self.files_endpt = "https://api.gdc.cancer.gov/files"
        self.organ = organ
        self.data_endpt = "https://api.gdc.cancer.gov/data"
        self.file_uuid_list = []

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
                    "value": ["HTSeq - Counts", "STAR - Counts"]
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
            "size": "1000"
            }
        return params

    def query_files(self):
        response = requests.get(self.files_endpt, params=self.param_construct())
        # This step populates the download list with the file_ids from the previous query
        for file_entry in json.loads(response.content.decode("utf-8"))["data"]["hits"]:
            self.file_uuid_list.append(file_entry["file_id"])

        return response, self.file_uuid_list

    def query_data(self, num_patients):
        sub_file_ids = self.file_uuid_list[:num_patients]
        for file_id in sub_file_ids:
            params = {"ids": file_id}
            response = requests.post(self.data_endpt, data=json.dumps(params), headers={"Content-Type": "application/json"})
            self.parse_data(response)

    def parse_data(self, response):
        response_head_cd = response.headers["Content-Disposition"]
        file_name = re.findall("filename=(.+)", response_head_cd)[0]
        file_path = os.path.join(r"6050-Cancer-Line-Comparison/Data-Files", file_name)
        with open(file_path, "wb") as output_file:
            output_file.write(response.content)

        with gzip.open(file_path, "rb") as gene_exp:
            for i in gene_exp.readlines()[:5]:
                print(i.decode("utf8"))
            print("\n")


root = Tk()
app = Interface(root)
root.mainloop()



