import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import xml.etree.ElementTree as ET
import os
from bs4 import BeautifulSoup

class Application(tk.Tk):
    """
    Главный класс приложения для конвертации XML в TEX формат
    """

    def __init__(self):
        super().__init__()

        self.title("XML to TEX converter")
        self.geometry("740x680")
        self.resizable(True, True)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Создание главной закладки
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Закладка для выбора файла
        self.select_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.select_tab, text="Select File")

        # Переключатель для выбора пути к файлу
        self.use_default_path = tk.BooleanVar(value=True)
        self.default_path_checkbox = ttk.Checkbutton(self.select_tab, text="Выбрать другой путь для XML",
                                                     variable=self.use_default_path, command=self.toggle_default_path)
        self.default_path_checkbox.pack(pady=10)

        # Поле и кнопка выбора папки
        self.default_path_label = ttk.Label(self.select_tab, text="Выбранный путь для XML:")
        self.default_path_label.pack()
        self.default_folder_path = tk.StringVar()
        self.default_folder_path_entry = ttk.Entry(self.select_tab, textvariable=self.default_folder_path,
                                                   state="disabled")
        self.default_folder_path_entry.pack()
        self.default_folder_button = ttk.Button(self.select_tab, text="Выбрать папку",
                                                command=self.select_default_folder, state="disabled")
        self.default_folder_button.pack()

        # Вывод списка XML-файлов в папке
        self.file_label = ttk.Label(self.select_tab, text="XML-файлы в выбранной папке:")
        self.file_label.pack()
        self.file_treeview = ttk.Treeview(self.select_tab)
        self.file_treeview.pack(fill=tk.BOTH, expand=True)

        # Кнопка старта обработки файлов
        self.start_button = ttk.Button(self.select_tab, text="Старт", command=self.process_file, state="disabled")
        self.start_button.pack(pady=10)

        # Инициализация переменных для результатов и текстовых данных
        self.result_tabs = []
        self.text_str_db = {}

        self.update_folder()

    def toggle_default_path(self):
        """
        Переключение режима выбора пути к файлу
        """
        if self.use_default_path.get():
            self.default_folder_path_entry.config(state="disabled")
            self.default_folder_button.config(state="disabled")
        else:
            self.default_folder_path_entry.config(state="enabled")
            self.default_folder_button.config(state="enabled")

    def select_default_folder(self):
        """
        Открытие диалогового окна для выбора папки
        """
        folder_path = filedialog.askdirectory()
        self.default_folder_path.set(folder_path)
        self.update_folder()

    def update_folder(self):
        """
        Обновление списка файлов в выбранной папке
        """
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
        """
        Обработка выбранного XML-файла
        """
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
        """
        Создание вкладок с результатами обработки файла
        :param file_path: Путь к XML-файлу (строка)
        """
        fd = open(file_path, 'r')
        xml_file = fd.read()
        soup = BeautifulSoup(xml_file, 'lxml')
        result_set = soup.find('tr:resultset')

        results_tab = ttk.Frame(self.notebook)
        self.notebook.add(results_tab, text="Results")

        self.results_notebook = ttk.Notebook(results_tab)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)

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
                    tex_str = ''
                    test_group_tab = ttk.Frame(self.results_notebook)
                    self.results_notebook.add(test_group_tab, text=callername)
                    tex_str += callername + '\n\n'
                    self.result_tabs.append(test_group_tab)

                    treeview = ttk.Treeview(test_group_tab, show="headings")
                    treeview.pack(fill=tk.BOTH, expand=True)

                    treeview["columns"] = ("Name", "Status", "Value")
                    treeview.heading("Name", text="Test")
                    treeview.heading("Status", text="Status")
                    treeview.heading("Value", text="Value")

                    if not isinstance(i, str):
                        for child in i.children:
                            if child.name == 'tr:test' or child.name == 'tr:testgroup':
                                if child.name == 'tr:testgroup':
                                    try:
                                        name2 = child.attrs['callername']
                                        treeview.insert("", "end",
                                                        values=(name2, child.find('tr:outcome')['qualifier'], 'None'))
                                        tex_str += f"{name2}  {child.find('tr:outcome')['qualifier']}  None\n"
                                    except:
                                        name2 = child.attrs['callername']
                                        treeview.insert("", "end",
                                                        values=(name2, child.find('tr:outcome')['value'], 'None'))
                                        tex_str += f"{name2}  {child.find('tr:outcome')['value']}  None\n"

                                try:
                                    if child.find('c:datum'):
                                        if child.find('c:datum').find('value'):
                                            try:
                                                name2 = child.attrs['callername']
                                            except:
                                                name2 = child.attrs['name']
                                            treeview.insert("", "end", values=(
                                                name2, child.find('tr:outcome')['qualifier'],
                                                child.find('c:datum').find('value')))
                                            tex_str += f"{name2}  {child.find('tr:outcome')['qualifier']}  {child.find('c:datum').find('value')}\n"
                                        # print('\n    ',child.attrs['name'], ' - ',child.attrs['id'] ,' - ',child.find('tr:outcome')['qualifier'], ' - ', child.find('c:datum').find('value')  ,'\n')
                                    else:
                                        try:
                                            name2 = child.attrs['callername']
                                        except:
                                            name2 = child.attrs['name']
                                        treeview.insert("", "end",
                                                        values=(name2, child.find('tr:outcome')['qualifier'], 'None'))
                                        tex_str += f"{name2}  {child.find('tr:outcome')['qualifier']}  None\n"
                                    #  print('\n    ',child.attrs['name'], ' - ',child.attrs['id'] ,' - ',child.find('tr:outcome')['qualifier'],' - ','None','\n')
                                except:
                                    if child.find('c:datum'):
                                        if child.find('c:datum').find('value'):
                                            # ' - ', child.find('c:datum').find('value')  ,
                                            try:
                                                name2 = child.attrs['callername']
                                            except:
                                                name2 = child.attrs['name']
                                            treeview.insert("", "end", values=(name2, child.find('tr:outcome')['value'],
                                                                               child.find('c:datum').find('value')))
                                            tex_str += f"{name2}  {child.find('tr:outcome')['value']}  {child.find('c:datum').find('value')}\n"
                                        # print('\n    ',child.attrs['name'], ' - ', child.attrs['id'] ,' - ', child.find('tr:outcome')['value'],' - ', child.find('c:datum').find('value')  ,'\n')
                                    else:
                                        try:
                                            name2 = child.attrs['callername']
                                        except:
                                            name2 = child.attrs['name']
                                        treeview.insert("", "end",
                                                        values=(name2, child.find('tr:outcome')['value'], 'None'))
                                        tex_str += f"{name2}  {child.find('tr:outcome')['value']}  None\n"
                                        # print('\n    ',child.attrs['name'], ' - ', child.attrs['id'] ,' - ', child.find('tr:outcome')['value'],' - ','None','\n')

                            if not isinstance(child, str):
                                for child2 in child.children:
                                    if child2.name == 'tr:test' or child2.name == 'tr:testgroup':
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

                                            treeview.insert("", "end", values=(f"            {child2.attrs['name']}",
                                                                               child.find('tr:outcome')['qualifier'],
                                                                               f'{GE} < {val} < {LE}'))
                                            tex_str += f"            {child2.attrs['name']}  {child.find('tr:outcome')['qualifier']}  {GE} < {val} < {LE}\n"
                                            # print('\n        ',child2.attrs['name'], ' - ', child2.find('tr:outcome')['qualifier'], f'  GE = {GE}  val = {val}  LE = {LE}' ,'\n')
                                        except:
                                            if GE and LE:
                                                treeview.insert("", "end", values=(
                                                    f"            {child2.attrs['name']}",
                                                    child.find('tr:outcome')['value'], f'{GE} < {val} < {LE}'))
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
                                                treeview.insert("", "end", values=(
                                                    f"            {child2.attrs['name']}",
                                                    child.find('tr:outcome')['value'], val))
                                                tex_str += f"            {child2.attrs['name']}  {child.find('tr:outcome')['value']}  {val}\n"
                                                # print('\n        ',child2.attrs['name'], ' - ', child2.find('tr:outcome')['value'], f'  {val}' ,'\n')

                    generate_button = ttk.Button(test_group_tab, text="Generate",
                                                 command=lambda idx=callername: self.generate_tex_file(idx))
                    generate_button.pack(pady=10)

                    copy_to_buffer_button = ttk.Button(test_group_tab, text="CopyOnBuffer",
                                                       command=lambda idx=callername: self.copy_to_buffer(idx))
                    copy_to_buffer_button.pack(pady=10)

                    self.text_str_db[callername] = tex_str

        self.notebook.select(results_tab)
        print(self.text_str_db)

    def generate_tex_file(self, idx):
        """
        Генерация TEX файла на основе данных в текстовой переменной
        :param idx: Имя файла (строка)
        """
        file_name = self.text_str_db[idx].split()
        with open(f"{idx}.tex", "w") as tex_file:
            tex_file.write(self.text_str_db[idx])

    def copy_to_buffer(self, idx):
        """
        Копирование данных в буфер обмена
        :param idx: Индекс данных (строка)
        """
        tab_id = self.results_notebook.select()
        tab_text = self.results_notebook.tab(tab_id, "text")
        tex_str = self.text_str_db.get(tab_text, "")
        if tex_str:
            self.clipboard_clear()
            self.clipboard_append(tex_str)
            self.update()

    def clear_result_tabs(self):
        """
        Очистка вкладок с результатами
        """
        for tab in self.result_tabs:
            self.results_notebook.forget(tab)
        self.result_tabs.clear()

    def clear_select_tab(self):
        """
        Очистка закладки для выбора файла
        """
        self.file_treeview.delete(*self.file_treeview.get_children())

    def clear_notebook(self):
        """
        Очистка основной закладки
        """
        for index in range(len(self.notebook.tabs()) - 1, 0, -1):
            self.notebook.forget(index)

    def clear_all(self):
        """
        Очистка всех данных и вкладок
        """
        self.clear_result_tabs()
        self.clear_select_tab()
        self.clear_notebook()

    def reset_default_path(self):
        """
        Сброс пути к файлу по умолчанию
        """
        self.default_folder_path.set("")

    def refresh(self):
        """
        Обновление приложения
        """
        self.clear_all()
        self.update_folder()

if __name__ == "__main__":
    app = Application()
    app.mainloop()
