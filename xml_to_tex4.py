import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter.simpledialog import askstring

from bs4 import BeautifulSoup


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("XML to TEX converter")
        self.geometry("800x700")
        self.resizable(True, True)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.select_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.select_tab, text="Select File")

        self.use_default_path = tk.BooleanVar(value=True)
        self.default_path_checkbox = ttk.Checkbutton(self.select_tab, text="Выбрать другой путь для XML",
                                                     variable=self.use_default_path, command=self.toggle_default_path)
        self.default_path_checkbox.pack(pady=10)

        self.default_path_label = ttk.Label(self.select_tab, text="Выбранный путь для XML:")
        self.default_path_label.pack()

        self.default_folder_path = tk.StringVar()
        self.default_folder_path_entry = ttk.Entry(self.select_tab, textvariable=self.default_folder_path,
                                                   state="disabled")
        self.default_folder_path_entry.pack()

        self.default_folder_button = ttk.Button(self.select_tab, text="Выбрать папку",
                                                command=self.select_default_folder, state="disabled")
        self.default_folder_button.pack()

        self.file_label = ttk.Label(self.select_tab, text="XML-файлы в выбранной папке:")
        self.file_label.pack()

        self.file_treeview = ttk.Treeview(self.select_tab)
        self.file_treeview.pack(fill=tk.BOTH, expand=True)

        self.start_button = ttk.Button(self.select_tab, text="Старт", command=self.process_file, state="disabled")
        self.start_button.pack(pady=10)

        self.result_tabs = []
        self.text_str_db = {}

        self.current_frame = None
        self.cnt_frame = 0

        self.dict_of_frame = {}

        self.update_folder()

    def toggle_default_path(self):
        if self.use_default_path.get():
            self.default_folder_path_entry.config(state="disabled")
            self.default_folder_button.config(state="disabled")
        else:
            self.default_folder_path_entry.config(state="enabled")
            self.default_folder_button.config(state="enabled")

    def select_default_folder(self):
        folder_path = filedialog.askdirectory()
        self.default_folder_path.set(folder_path)
        self.update_folder()

    def update_folder(self):
        if self.use_default_path.get():
            folder_path = os.path.dirname(os.path.abspath(__file__))
        else:
            folder_path = self.default_folder_path.get()

        if os.path.isdir(folder_path):
            file_list = [f for f in os.listdir(folder_path) if f.endswith(".xml")]
            self.file_treeview.delete(*self.file_treeview.get_children())
            for file in file_list:
                self.file_treeview.insert("", "end", text=file, values=(file,))
            if file_list:
                self.start_button.config(state="enabled")
            else:
                self.start_button.config(state="disabled")
        else:
            self.file_treeview.delete(*self.file_treeview.get_children())
            self.start_button.config(state="disabled")

    def process_file(self):
        selected_item = self.file_treeview.focus()
        if selected_item:
            selected_file = self.file_treeview.item(selected_item)["text"]
            if self.use_default_path.get():
                folder_path = os.path.dirname(os.path.abspath(__file__))
            else:
                folder_path = self.default_folder_path.get()
            file_path = os.path.join(folder_path, selected_file)
            self.create_results_tabs(file_path)

    def create_results_tabs(self, file_path):

        fd = open(file_path, 'r')
        xml_file = fd.read()
        soup = BeautifulSoup(xml_file, 'lxml')
        result_set = soup.find('tr:resultset')

        results_tab = ttk.Frame(self.notebook)

        self.notebook.add(results_tab, text="Results")

        self.results_notebook = ttk.Notebook(results_tab)

        self.results_notebook.pack(fill=tk.BOTH, expand=True)

        print('label')

        # test_groups = root.findall(".//TestGroup")
        # idx = 0
        counter = 0

        for n, i in enumerate(result_set.children):
            if i.name == 'tr:test' or i.name == 'tr:testgroup':
                callername = None
                status = None
                try:
                    status = i.find('tr:outcome')['qualifier']
                except:
                    status = i.find('tr:outcome')['value']

                try:
                    callername = i.attrs['callername']
                except:
                    callername = i.attrs['name']

                if status != 'Skipped':
                    counter += 1

                    tex_str = ''
                    list_treeview = []
                    test_group_tab = ttk.Frame(self.results_notebook)
                    self.results_notebook.add(test_group_tab, text=callername)
                    tex_str += callername + '\n\n'
                    self.result_tabs.append(test_group_tab)

                    main_tab = ttk.Frame(test_group_tab)
                    main_tab.pack(fill='both', expand=True)

                    frame_for_btn = ttk.Frame(main_tab)
                    frame_for_btn.pack(pady=(5, 20))

                    canvas = tk.Canvas(frame_for_btn, height=30, width=1920)
                    canvas.pack(fill="both", expand=True)

                    scrollbar = ttk.Scrollbar(frame_for_btn, orient="horizontal", command=canvas.xview)
                    scrollbar.pack(fill='x')

                    button_frame = tk.Frame(canvas)
                    canvas.create_window((0, 0), window=button_frame, anchor="nw")

                    global frame_for_treeview, name_or_callerName
                    frame_for_treeview = ttk.Frame(main_tab)

                    frame_for_treeview.pack(pady=(10, 15), fill='both', expand=True)

                    global x_max
                    x_max = 100

                    def update_width_scrollbar(wid):
                        global x_max
                        x_max += wid * 2
                        canvas.configure(scrollregion=(0, 0, x_max, 0))

                    # Привяжите xscrollbar к холсту
                    canvas.configure(xscrollcommand=scrollbar.set)

                    width_const = 3.40
                    if not isinstance(i, str):
                        for h, child in enumerate(i.children):
                            if child.name == 'tr:test' or child.name == 'tr:testgroup':
                                if child.name == 'tr:testgroup' or child.name == 'tr:sessionaction':
                                    try:
                                        name2 = child.attrs['callername']
                                        # treeview.insert("", "end", values=(name2, child.find('tr:outcome')['qualifier'], 'None'))
                                        tex_str += f"{name2}  {child.find('tr:outcome')['qualifier']}  None\n"

                                        # notebook_2.add(new_tab, text=name2)
                                        # update_width_scrollbar(len(name2)*width_const)
                                        # print(notebook_2.winfo_reqwidth(), ' - ', notebook_2.winfo_width())
                                        new_tab = ttk.Frame(frame_for_treeview)
                                        self.cnt_frame += 1
                                        self.dict_of_frame[self.cnt_frame] = new_tab

                                        print(self.cnt_frame)

                                        try:
                                            if child.find('c:datum')['xsi:type'] == 'ts:TS_string':
                                                string_val = child.find('c:datum').find('c:value').text
                                                # print(string_val.text)
                                            else:
                                                string_val = " - "
                                        except:
                                            pass

                                        treeview = ttk.Treeview(new_tab, show="headings")
                                        treeview.bind("<Button-3>",
                                                      lambda event, tree=treeview: self.on_right_click(event, tree))
                                        treeview.bind("<Double-1>",
                                                      lambda event, tree=treeview: self.on_cell_edit(event, tree))
                                        treeview.pack(fill='both', expand=True)
                                        treeview["columns"] = ("Name", "Status", "Value", "Dop", "String")
                                        treeview.heading("Name", text="Test")
                                        treeview.heading("Status", text="Status")
                                        treeview.heading("Value", text="Значение")
                                        treeview.heading("Dop", text="Допустимое значение")
                                        treeview.heading("String", text="String")
                                        treeview.insert("", "end", values=(
                                            name2, child.find('tr:outcome')['qualifier'], 'None', '-', string_val))
                                        list_treeview.append(treeview)

                                        button = ttk.Button(button_frame, text=name2,
                                                            command=lambda id_btn=self.cnt_frame: self.update_frame(
                                                                id_btn))
                                        button.pack(side='left', padx=2, pady=5)
                                        update_width_scrollbar(len(name2) * width_const)
                                    except:
                                        name2 = child.attrs['callername']
                                        # treeview.insert("", "end", values=(name2, child.find('tr:outcome')['value'], 'None'))
                                        tex_str += f"{name2}  {child.find('tr:outcome')['value']}  None\n"
                                        new_tab = ttk.Frame(frame_for_treeview)
                                        self.cnt_frame += 1
                                        self.dict_of_frame[self.cnt_frame] = new_tab
                                        print(self.cnt_frame)

                                        button = ttk.Button(button_frame, text=name2,
                                                            command=lambda id_btn=self.cnt_frame: self.update_frame(
                                                                id_btn))
                                        button.pack(side='left', padx=2, pady=5)
                                        update_width_scrollbar(len(name2) * width_const)

                                        try:
                                            if child.find('c:datum')['xsi:type'] == 'ts:TS_string':
                                                string_val = child.find('c:datum').find('c:value').text
                                                # print(string_val.text)
                                            else:
                                                string_val = " - "
                                        except:
                                            pass

                                        treeview = ttk.Treeview(new_tab, show="headings")
                                        treeview.bind("<Button-3>",
                                                      lambda event, tree=treeview: self.on_right_click(event, tree))
                                        treeview.bind("<Double-1>",
                                                      lambda event, tree=treeview: self.on_cell_edit(event, tree))
                                        treeview.pack(fill='both', expand=True)
                                        treeview["columns"] = ("Name", "Status", "Value", "Dop", "String")
                                        treeview.heading("Name", text="Test")
                                        treeview.heading("Status", text="Status")
                                        treeview.heading("Value", text="Значение")
                                        treeview.heading("Dop", text="Допустимое значение")
                                        treeview.heading("String", text="String")

                                        treeview.insert("", "end", values=(
                                            name2, child.find('tr:outcome')['value'], 'None', '-', string_val))
                                        list_treeview.append(treeview)

                                        # new_tab = ttk.Frame(notebook_2, width=50)
                                        # notebook_2.add(new_tab, text=name2)
                                        # update_width_scrollbar(len(name2)*width_const)
                                        # print(notebook_2.winfo_reqwidth(), ' - ', notebook_2.winfo_width())

                                try:
                                    if child.find('c:datum'):
                                        if child.find('c:datum').find('value'):
                                            try:
                                                name2 = child.attrs['callername']
                                            except:
                                                name2 = child.attrs['name']

                                            new_tab = ttk.Frame(frame_for_treeview)
                                            self.cnt_frame += 1
                                            self.dict_of_frame[self.cnt_frame] = new_tab
                                            print(self.cnt_frame)

                                            # treeview.insert("", "end", values=(name2, child.find('tr:outcome')['qualifier'], child.find('c:datum').find('value')))
                                            tex_str += f"{name2}  {child.find('tr:outcome')['qualifier']}  {child.find('c:datum').find('value')}\n"
                                            button = ttk.Button(button_frame, text=name2,
                                                                command=lambda id_btn=self.cnt_frame: self.update_frame(
                                                                    id_btn))
                                            button.pack(side='left', padx=2, pady=5)
                                            update_width_scrollbar(len(name2) * width_const)

                                            try:
                                                if child.find('c:datum')['xsi:type'] == 'ts:TS_string':
                                                    string_val = child.find('c:datum').find('c:value').text
                                                    # print(string_val.text)
                                                else:
                                                    string_val = " - "
                                            except:
                                                pass

                                            treeview = ttk.Treeview(new_tab, show="headings")
                                            treeview.bind("<Button-3>",
                                                          lambda event, tree=treeview: self.on_right_click(event, tree))
                                            treeview.bind("<Double-1>",
                                                          lambda event, tree=treeview: self.on_cell_edit(event, tree))
                                            treeview.pack(fill='both', expand=True)
                                            treeview["columns"] = ("Name", "Status", "Value", "Dop", "String")

                                            treeview.heading("Name", text="Test")
                                            treeview.heading("Status", text="Status")
                                            treeview.heading("Value", text="Значение")
                                            treeview.heading("Dop", text="Допустимое значение")
                                            treeview.heading("String", text="String")

                                            treeview.insert("", "end", values=(
                                                name2, child.find('tr:outcome')['qualifier'],
                                                child.find('c:datum').find('value'), '-', string_val))
                                            list_treeview.append(treeview)
                                            # new_tab = ttk.Frame(notebook_2, width=50)
                                            # notebook_2.add(new_tab, text=name2)
                                            # update_width_scrollbar(len(name2)*width_const)
                                            # print(notebook_2.winfo_reqwidth(), ' - ', notebook_2.winfo_width())
                                        # print('\n    ',child.attrs['name'], ' - ',child.attrs['id'] ,' - ',child.find('tr:outcome')['qualifier'], ' - ', child.find('c:datum').find('value')  ,'\n')
                                    else:
                                        try:
                                            name2 = child.attrs['callername']
                                        except:
                                            name2 = child.attrs['name']
                                        # treeview.insert("", "end", values=(name2, child.find('tr:outcome')['qualifier'], 'None'))
                                        tex_str += f"{name2}  {child.find('tr:outcome')['qualifier']}  None\n"
                                        new_tab = ttk.Frame(frame_for_treeview)
                                        self.cnt_frame += 1
                                        self.dict_of_frame[self.cnt_frame] = new_tab
                                        print(self.cnt_frame)

                                        button = ttk.Button(button_frame, text=name2,
                                                            command=lambda id_btn=self.cnt_frame: self.update_frame(
                                                                id_btn))
                                        button.pack(side='left', padx=2, pady=5)
                                        update_width_scrollbar(len(name2) * width_const)

                                        try:
                                            if child.find('c:datum')['xsi:type'] == 'ts:TS_string':
                                                string_val = child.find('c:datum').find('c:value').text
                                                # print(string_val.text)
                                            else:
                                                string_val = " - "
                                        except:
                                            pass

                                        treeview = ttk.Treeview(new_tab, show="headings")
                                        treeview.bind("<Button-3>",
                                                      lambda event, tree=treeview: self.on_right_click(event, tree))
                                        treeview.bind("<Double-1>",
                                                      lambda event, tree=treeview: self.on_cell_edit(event, tree))
                                        treeview.pack(fill='both', expand=True)
                                        treeview["columns"] = ("Name", "Status", "Value", "Dop", "String")

                                        treeview.heading("Name", text="Test")
                                        treeview.heading("Status", text="Status")
                                        treeview.heading("Value", text="Значение")
                                        treeview.heading("Dop", text="Допустимое значение")
                                        treeview.heading("String", text="String")

                                        treeview.insert("", "end", values=(
                                            name2, child.find('tr:outcome')['qualifier'], 'None', '-', string_val))
                                        list_treeview.append(treeview)

                                        # new_tab = ttk.Frame(notebook_2, width=50)
                                    # notebook_2.add(new_tab, text=name2)
                                    # update_width_scrollbar(len(name2)*width_const)
                                    # print(notebook_2.winfo_reqwidth(), ' - ', notebook_2.winfo_width())
                                    #  print('\n    ',child.attrs['name'], ' - ',child.attrs['id'] ,' - ',child.find('tr:outcome')['qualifier'],' - ','None','\n')
                                except:
                                    if child.find('c:datum'):
                                        if child.find('c:datum').find('value'):
                                            # ' - ', child.find('c:datum').find('value')  ,
                                            try:
                                                name2 = child.attrs['callername']
                                            except:
                                                name2 = child.attrs['name']
                                            #   treeview.insert("", "end", values=(name2, child.find('tr:outcome')['value'], child.find('c:datum').find('value')))
                                            tex_str += f"{name2}  {child.find('tr:outcome')['value']}  {child.find('c:datum').find('value')}\n"
                                            new_tab = ttk.Frame(frame_for_treeview)
                                            self.cnt_frame += 1
                                            self.dict_of_frame[self.cnt_frame] = new_tab
                                            print(self.cnt_frame)

                                            button = ttk.Button(button_frame, text=name2,
                                                                command=lambda id_btn=self.cnt_frame: self.update_frame(
                                                                    id_btn))
                                            button.pack(side='left', padx=2, pady=5)
                                            update_width_scrollbar(len(name2) * width_const)

                                            try:
                                                if child.find('c:datum')['xsi:type'] == 'ts:TS_string':
                                                    string_val = child.find('c:datum').find('c:value').text
                                                    # print(string_val.text)
                                                else:
                                                    string_val = " - "
                                            except:
                                                pass

                                            treeview = ttk.Treeview(new_tab, show="headings")
                                            treeview.bind("<Button-3>",
                                                          lambda event, tree=treeview: self.on_right_click(event, tree))
                                            treeview.bind("<Double-1>",
                                                          lambda event, tree=treeview: self.on_cell_edit(event, tree))
                                            # treeview.bind("<Double-1>", lambda event, tree=treeview: self.on_cell_edit(event,tree))
                                            treeview.pack(fill='both', expand=True)
                                            treeview["columns"] = ("Name", "Status", "Value", "Dop", "String")

                                            treeview.heading("Name", text="Test")
                                            treeview.heading("Status", text="Status")
                                            treeview.heading("Value", text="Значение")
                                            treeview.heading("Dop", text="Допустимое значение")
                                            treeview.heading("String", text="String")

                                            treeview.insert("", "end", values=(name2, child.find('tr:outcome')['value'],
                                                                               child.find('c:datum').find('value'), '-',
                                                                               string_val))
                                            list_treeview.append(treeview)
                                        #  new_tab = ttk.Frame(notebook_2, width=50)
                                        # notebook_2.add(new_tab, text=name2)
                                        # update_width_scrollbar(len(name2)*width_const)
                                        # print(new_tab.winfo_reqwidth(), ' - ', new_tab.winfo_width())
                                        # print('\n    ',child.attrs['name'], ' - ', child.attrs['id'] ,' - ', child.find('tr:outcome')['value'],' - ', child.find('c:datum').find('value')  ,'\n')
                                    else:
                                        try:
                                            name2 = child.attrs['callername']
                                        except:
                                            name2 = child.attrs['name']
                                        # treeview.insert("", "end", values=(name2, child.find('tr:outcome')['value'], 'None'))
                                        tex_str += f"{name2}  {child.find('tr:outcome')['value']}  None\n"
                                        new_tab = ttk.Frame(frame_for_treeview)
                                        self.cnt_frame += 1
                                        self.dict_of_frame[self.cnt_frame] = new_tab
                                        print(self.cnt_frame)

                                        button = ttk.Button(button_frame, text=name2,
                                                            command=lambda id_btn=self.cnt_frame: self.update_frame(
                                                                id_btn))
                                        button.pack(side='left', padx=2, pady=5)
                                        update_width_scrollbar(len(name2) * width_const)

                                        try:
                                            if child.find('c:datum')['xsi:type'] == 'ts:TS_string':
                                                string_val = child.find('c:datum').find('c:value').text
                                                # print(string_val.text)
                                            else:
                                                string_val = " - "
                                        except:
                                            pass

                                        treeview = ttk.Treeview(new_tab, show="headings")
                                        treeview.bind("<Button-3>",
                                                      lambda event, tree=treeview: self.on_right_click(event, tree))
                                        treeview.bind("<Double-1>",
                                                      lambda event, tree=treeview: self.on_cell_edit(event, tree))
                                        treeview.pack(fill='both', expand=True)
                                        treeview["columns"] = ("Name", "Status", "Value", "Dop", "String")

                                        treeview.heading("Name", text="Test")
                                        treeview.heading("Status", text="Status")
                                        treeview.heading("Value", text="Значение")
                                        treeview.heading("Dop", text="Допустимое значение")
                                        treeview.heading("String", text="String")

                                        treeview.insert("", "end", values=(
                                            name2, child.find('tr:outcome')['value'], 'None', '-', string_val))
                                        list_treeview.append(treeview)

                                        # new_tab = ttk.Frame(notebook_2, width=50)
                                        # notebook_2.add(new_tab, text=name2)
                                    # update_width_scrollbar(len(name2)*width_const)
                                    # print(new_tab.winfo_reqwidth(), ' - ', new_tab.winfo_width())
                                    # print('\n    ',child.attrs['name'], ' - ', child.attrs['id'] ,' - ', child.find('tr:outcome')['value'],' - ','None','\n')

                            if not isinstance(child, str):
                                for child2 in child.children:
                                    if child2.name == 'tr:test' or child2.name == 'tr:testgroup' or child2.name == 'tr:tr:sessionaction':
                                        GE = None
                                        LE = None
                                        val = None
                                        try:

                                            limits = child2.find_all('c:limit')
                                            val = child2.find('tr:testdata').find('c:datum').attrs['value']
                                            for limit in limits:
                                                if limit.attrs['comparator'] == 'GE':
                                                    GE = limit.find('c:datum').attrs['value']
                                                if limit.attrs['comparator'] == 'LE':
                                                    LE = limit.find('c:datum').attrs['value']
                                            try:
                                                if child.find('c:datum')['xsi:type'] == 'ts:TS_string':
                                                    string_val = child.find('c:datum').find('c:value').text
                                                    # print(string_val.text)
                                                else:
                                                    string_val = " - "
                                            except:
                                                pass

                                            treeview.insert("", "end", values=(f"{child2.attrs['callerName']}",
                                                                               child.find('tr:outcome')['qualifier'],
                                                                               val, f'{GE} ÷ {LE}', string_val))
                                            tex_str += f"{child2.attrs['callerName']}  {child.find('tr:outcome')['qualifier']}  {GE} < {val} < {LE}\n"
                                            # print('\n        ',child2.attrs['name'], ' - ', child2.find('tr:outcome')['qualifier'], f'  GE = {GE}  val = {val}  LE = {LE}' ,'\n')
                                        except:
                                            if GE and LE:
                                                try:
                                                    if child.find('c:datum')['xsi:type'] == 'ts:TS_string':
                                                        string_val = child.find('c:datum').find('c:value').text
                                                        # print(string_val.text)
                                                    else:
                                                        string_val = " - "
                                                except:
                                                    pass
                                                name_or_callerName = child2.attrs.get('callerName',
                                                                                      child2.attrs.get('name', ''))
                                                treeview.insert("", "end", values=(
                                                    f"            {name_or_callerName}",
                                                    child.find('tr:outcome')['value'], val, f'{GE} ÷ {LE}', string_val))
                                                tex_str += f"            {child2.attrs['name']}  {child.find('tr:outcome')['value']}  {GE} < {val} < {LE}\n"
                                                # print('\n        ',child2.attrs['name'], ' - ', child2.find('tr:outcome')['value'], f'  {GE} < {val} < {LE}' ,'\n')
                                            else:
                                                # try:

                                                if child2 is not None:
                                                    limits2 = child2.find('tr:limits')

                                                    if limits2:

                                                        val = limits2.find('c:datum').attrs['value']
                                                    else:
                                                        if child2.find('tr:testdata'):
                                                            val = child2.find('tr:testdata').find('c:datum').attrs[
                                                                'value']
                                                        else:
                                                            val = None
                                                    # except:
                                                    pass

                                                try:
                                                    if child.find('c:datum')['xsi:type'] == 'ts:TS_string':
                                                        string_val = child.find('c:datum').find('c:value').text
                                                        # print(string_val.text)
                                                    else:
                                                        string_val = " - "
                                                except:
                                                    pass
                                                treeview.insert("", "end", values=(
                                                    f"  {name_or_callerName}",
                                                    child.find('tr:outcome')['value'], val, '-', string_val))
                                                tex_str += f"  {name_or_callerName}  {child.find('tr:outcome')['value']}  {val}\n"
                                            # print('\n        ',child2.attrs['name'], ' - ', child2.find('tr:outcome')['value'], f'  {val}' ,'\n')

                    # treeview.insert("", "end", values=(name, status, value))

                    # self.generate_button = ttk.Button(test_group_tab, text="Generate", command=lambda idx=callername: self.generate_tex_file(idx))
                    self.generate_button = ttk.Button(test_group_tab, text="Generate",
                                                      command=lambda main_name=callername,
                                                                     idx=list_treeview: self.parse_treeview_data(idx,
                                                                                                                 main_name))
                    self.generate_button.pack(pady=10)

                    self.text_str_db[callername] = tex_str
                # print(self.dict_of_frame)

        self.notebook.select(results_tab)

    # print(self.text_str_db)

    def on_right_click(self, event, tree):
        item = tree.identify_row(event.y)
        column = tree.identify_column(event.x)

        if item and column:
            column = column.split("#")[-1]  # Get the column index
            item_text = tree.item(item, "values")[int(column) - 1]
            self.copy_to_clipboard(item_text)
            # item_text = tree.item(item, "values")[int(column)+2]
            # if item_text == '-':

            #     self.copy_to_clipboard(tree.item(item, "values")[int(column)+1])
            # else:
            #     self.copy_to_clipboard(item_text)

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

    def on_cell_edit(self, event, tree):
        item = tree.selection()[0]
        column = tree.identify_column(event.x)

        if column != "#0":  # Exclude the first (checkbox) column
            column_index = int(column.replace("#", ""))

            column_name = tree.heading(column, "text")
            current_value = tree.item(item, "values")[column_index - 1]

            new_value = askstring(f"Edit {column_name}", f"Enter new {column_name}:", initialvalue=current_value)

            if new_value is not None:
                values = list(tree.item(item, "values"))
                values[column_index - 1] = new_value
                tree.item(item, values=values)

    def parse_treeview_data(self, list_tr, main_name):
        # Инициализируем переменную для хранения прочитанного содержимого шаблона
        template_content = ""

        # Читаем содержимое файла Test3.tex
        try:
            with open("tamplete/Test3.tex", "r", encoding="utf-8") as template_file:
                template_content = template_file.read()
        except Exception as e:
            print(f"Не удалось прочитать файл шаблона: {e}")

        # Инициализируем переменную для хранения основных данных
        parsed_data = ""

        # Обрабатываем дерево
        for tree in list_tr:
            for item in tree.get_children():
                values = tree.item(item, "values")
                test, status, value, dop, string = values
                parsed_data += f"{test}   {status}   {value}   {dop}   {string}\n"

        # Записываем все данные в файл
        try:
            with open(f"{main_name}.tex", "w", encoding="utf-8") as tex_file:
                # Записываем содержимое шаблона в начало файла
                tex_file.write(template_content)
                # Записываем основные данные
                tex_file.write(parsed_data)
        except Exception as e:
            print(f"Не удалось записать в файл: {e}")

    def update_frame(self, idx):
        print(idx)

        if self.current_frame:
            self.current_frame.pack_forget()

        selected_frame = self.dict_of_frame[idx]
        if selected_frame:
            selected_frame.pack(fill='both', expand=True)
            # label = tk.Label(selected_frame, text=f'{idx}')
            # label.pack()
            self.current_frame = selected_frame

    def generate_tex_file(self, idx):
        try:
            # Чтение шаблонного файла
            with open("tamplete/Test3.tex", "r") as template_file:
                template_content = template_file.read()
                print(
                    f"Successfully read the template file. Content: {template_content[:50]}...")  # Выводим первые 50 символов
        except Exception as e:
            print(f"Error reading the template file: {e}")
            template_content = ""

        # Создание имени файла на основе индекса (хотя это значение не используется в оригинальной версии)
        file_name = self.text_str_db[idx].split()

        try:
            # Запись в целевой файл
            with open(f"{idx}.tex", "w") as tex_file:
                # Запись содержимого шаблонного файла
                tex_file.write(template_content)
                # Запись основного содержимого
                tex_file.write(self.text_str_db[idx])
                print(f"Successfully wrote to {idx}.tex")  # Уведомление об успешной записи
        except Exception as e:
            print(f"Error writing to the target file: {e}")

    def clear_result_tabs(self):
        for tab in self.result_tabs:
            self.results_notebook.forget(tab)

        self.result_tabs.clear()

    def clear_select_tab(self):
        self.file_treeview.delete(*self.file_treeview.get_children())

    def clear_notebook(self):
        for index in range(len(self.notebook.tabs()) - 1, 0, -1):
            self.notebook.forget(index)

    def clear_all(self):
        self.clear_result_tabs()
        self.clear_select_tab()
        self.clear_notebook()

    def reset_default_path(self):
        self.default_folder_path.set("")

    def refresh(self):
        self.clear_all()
        self.update_folder()


if __name__ == "__main__":
    app = Application()
    app.mainloop()