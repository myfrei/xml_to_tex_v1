import os
import tkinter as tk
from tkinter import ttk, YES, BOTH
from tkinter import filedialog
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk
from ttkthemes import ThemedTk
from tkinter import messagebox

class StartFrame(ttk.Frame):
    def __init__(self, container, controller, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.controller = controller

        # Левая часть
        self.switch_frame = ttk.Frame(self)
        self.switch_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nw')

        self.switch = Switch(self.switch_frame)
        self.switch.grid(row=0, column=0, padx=5, pady=5)

        self.switch_label = ttk.Label(self.switch_frame, text="Выбрать другую директорию")
        self.switch_label.grid(row=0, column=1, padx=5, pady=5)
        self.switch.bind('<<SwitchToggled>>', lambda e: self.toggle_dir_choice())

        self.dir_entry = ttk.Entry(self, state='disabled')
        self.dir_entry.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        self.dir_button = ttk.Button(self, text="Выбрать папку", command=self.choose_directory, state='disabled')
        self.dir_button.grid(row=2, column=0, padx=5, pady=5)

        self.file_listbox = tk.Listbox(self, width=25)
        self.file_listbox.grid(row=3, column=0, padx=5, pady=5, sticky='nsew')

        ttk.Button(self, text="Start", command=self.start).grid(row=4, column=0, padx=5, pady=5)

        # Правая часть
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'photo.jpg')
        img = Image.open(img_path)
        img = img.resize((300, 300))
        self.logo = ImageTk.PhotoImage(img)
        ttk.Label(self, image=self.logo).grid(row=0, column=1, rowspan=4, padx=5, pady=5, sticky='ne')

        self.theme_combobox = ttk.Combobox(self, values=self.controller.available_themes)
        if self.controller.available_themes:
            self.theme_combobox.set(self.controller.available_themes[0])
        self.theme_combobox.grid(row=4, column=1, padx=65, pady=5, ipady=2, rowspan=4, sticky='w')

        self.apply_button = ttk.Button(self, text="Применить", command=self.apply_theme)
        self.apply_button.grid(row=4, column=1, padx=5, pady=5, sticky='e')

        self.populate_file_list(os.path.dirname(os.path.abspath(__file__)))

        # Конфигурация grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

    def apply_theme(self):
        selected_theme = self.theme_combobox.get()  # Получаем выбранную тему
        if selected_theme:
            self.controller.root.set_theme(selected_theme)  # Применяем выбранную тему

    def toggle_dir_choice(self):
        if self.switch.is_on:  # Используйте свойство is_on нового виджета Switch
            self.dir_entry.config(state='normal')
            self.dir_button.config(state='normal')
        else:
            self.dir_entry.config(state='disabled')
            self.dir_button.config(state='disabled')
            self.populate_file_list(os.path.dirname(os.path.abspath(__file__)))

    def choose_directory(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, folder_selected)
            self.populate_file_list(folder_selected)

    def populate_file_list(self, directory):
        self.file_listbox.delete(0, tk.END)
        for file in os.listdir(directory):
            if file.endswith(".xml"):
                self.file_listbox.insert(tk.END, file)

    def start(self):
        selected_file = self.file_listbox.get(tk.ACTIVE)
        directory = self.dir_entry.get()

        if not selected_file:
            messagebox.showerror("Ошибка", "Файл не выбран.")
            return

        if not directory:
            directory = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(directory, selected_file)

        self.controller.start_analysis(file_path)


class XMLApp:
    def __init__(self, root):
        self.tab_control = None
        self.menu = None
        self.root = root
        self.available_themes = self.root.get_themes()
        self.root.set_theme('blue')
        self.root.title("XML Viewer")
        self.root.geometry("700x330+100+100")
        self.root.resizable(False, False)
        self.init_ui()  # Вызов метода init_ui
        self.start_frame = StartFrame(self.root, self)  # Обратите внимание, что мы передаем self как controller
        self.start_frame.pack(expand=tk.YES, fill=tk.BOTH)

    def init_ui(self):
        # Инициализация пользовательского интерфейса
        self.tab_control = ttk.Notebook(self.root)
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.file_menu = tk.Menu(self.menu)
        #self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.load_xml)

    # Метод для загрузки и анализа XML файла
    def load_xml(self, root, tab_control):
        namespaces = {
            'tr': 'urn:IEEE-1636.1:2011:01:TestResults'
        }

        for elem in root.findall(".//tr:ResultSet", namespaces=namespaces):
            for child in elem.findall("./tr:TestGroup | ./tr:Test", namespaces=namespaces):
                tab_name = child.get('callerName', child.get('name', 'Unknown'))
                self.add_tab(child, tab_name, tab_control)

    # Метод для добавления новой вкладки в Notebook
    def add_tab(self, elem, name, tab_control):
        tab = ttk.Frame(tab_control)
        tab_control.add(tab, text=name)

        tree = ttk.Treeview(tab, columns=("Value",), show="tree headings")
        tree.column("#0", width=200)
        tree.column("Status", width=200)
        tree.heading("Status", text="Status")
        tree.pack(fill='both', expand=True)

        self.populate_tree(tree, elem)

    # Метод для добавления элементов в дерево
    def populate_tree(self, tree, elem, parent="", level=1):
        namespaces = {
            "tr": "urn:IEEE-1636.1:2011:01:TestResults",
            "c": "urn:IEEE-1671:2010:Common"
        }

        for child in elem:
            name = child.attrib.get('callerName', child.attrib.get('name', 'Unknown'))

            # Извлечение значения атрибута 'value' из тега 'tr:Outcome'
            outcome = child.find('./tr:Outcome', namespaces=namespaces)
            status = outcome.get('value') if outcome is not None else 'N/A'

            # Извлечение данных из тега 'tr:Data'
            data_elems = child.findall('./tr:Data/c:Collection/c:Item/c:Datum', namespaces=namespaces)
            data_values = [datum.get('value') for datum in data_elems] if data_elems else ['N/A']
            data_str = ', '.join(data_values)  # Преобразование списка значений в строку, разделенную запятыми

            # Извлечение данных из тега 'tr:TestResult'
            test_result_elems = child.findall('.//tr:TestResult', namespaces=namespaces)
            for test_result in test_result_elems:
                value_elem = test_result.find("./tr:TestData/c:Datum", namespaces=namespaces)
                value = value_elem.get("value") if value_elem is not None else 'N/A'

                low_limit_elem = test_result.find(
                    "./tr:TestLimits/tr:Limits/c:LimitPair/c:Limit[@comparator='GE']/c:Datum", namespaces=namespaces)
                low_limit = low_limit_elem.get("value") if low_limit_elem is not None else ' '

                high_limit_elem = test_result.find(
                    "./tr:TestLimits/tr:Limits/c:LimitPair/c:Limit[@comparator='LE']/c:Datum", namespaces=namespaces)
                high_limit = high_limit_elem.get("value") if high_limit_elem is not None else ' '

                valid_values_str = f"{low_limit} < > {high_limit}"

                if name == "Unknown":
                    continue

                id = tree.insert(parent, tk.END, text=name, values=(
                status, value, valid_values_str))  # Добавление статуса, значения и допустимых значений в дерево
                self.populate_tree(tree, child, id, level + 1)

    # Метод для анализа выбранного файла и отображения результатов в новом окне
    def start_analysis(self, file_path):
        result_window = tk.Toplevel(self.root)
        result_window.title("Result")

        # Создаем Canvas и Scrollbar для горизонтальной прокрутки
        canvas = tk.Canvas(result_window)
        scrollbar = ttk.Scrollbar(result_window, orient="horizontal", command=canvas.xview)
        frame = ttk.Frame(canvas)

        canvas.config(xscrollcommand=scrollbar.set)
        scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Создаем Notebook внутри Frame
        tab_control = ttk.Notebook(frame)
        tab_control.pack(expand=tk.YES, fill=tk.BOTH)

        frame.bind("<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all")))

        if not file_path:
            print("No file selected.")
            return

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except Exception as e:
            print(f"Failed to parse XML: {e}")
            return

        # self.add_tree_tab(root, "Full Tree", tab_control)  # Здесь создается вкладка с полным деревом
        self.add_tabs_from_xml(root, tab_control)

    def add_tabs_from_xml(self, xml_root, tab_control):
        namespaces = {'tr': 'urn:IEEE-1636.1:2011:01:TestResults'}

        for elem in xml_root.findall('.//tr:ResultSet', namespaces=namespaces):
            for child in elem.findall('./*', namespaces=namespaces):
                tag = child.tag.split('}')[-1]
                if tag in ['TestGroup', 'Test']:
                    name = child.get('callerName', child.get('name', 'Unknown'))
                    if name == "Unknown":
                        continue
                    # Вместо добавления вкладки дерева добавляем вкладку Notebook
                    self.add_notebook_tab(child, name, tab_control)

    def add_notebook_tab(self, xml_element, tab_name, tab_control):
        # Создаем новый ttk.Notebook для каждой вкладки
        sub_tab_control = ttk.Notebook(tab_control)
        tab_control.add(sub_tab_control, text=tab_name)

        # Теперь для каждого дочернего элемента xml_element добавим вкладку в sub_tab_control
        for sub_elem in xml_element:
            sub_name = sub_elem.get('callerName', sub_elem.get('name', 'Unknown'))
            if sub_name != "Unknown":
                self.add_tree_tab(sub_elem, sub_name, sub_tab_control)

    def add_tree_tab(self, xml_element, tab_name, tab_control):
        # Создаем Frame для каждой вкладки
        frame = ttk.Frame(tab_control)
        tab_control.add(frame, text=tab_name)

        tree = ttk.Treeview(frame, columns=("status", "value", "valid_values"))
        tree.pack(expand=tk.YES, fill=tk.BOTH)

        tree.column("#0", width=270, minwidth=270)
        tree.column("status", width=150, minwidth=150)
        tree.column("value", width=150, minwidth=150)
        tree.column("valid_values", width=150, minwidth=150)

        tree.heading("#0", text="Treeview")
        tree.heading("status", text="Status")
        tree.heading("value", text="Value")
        tree.heading("valid_values", text="Valid Values")

        self.populate_tree(tree, xml_element)


    def populate_full_tree(self, tree, elem, parent="", level=1):
        name = elem.tag
        value = elem.text.strip() if elem.text else "N/A"
        namespaces = {'tr': 'urn:IEEE-1636.1:2011:01:TestResults'}

        # Если элемент является tr:TestGroup или tr:Test, или является их потомком
        if 'TestGroup' in name or 'Test' in name or parent:
            # Добавляем текущий элемент как узел в дерево
            id = tree.insert(parent, tk.END, text=name, values=(value,))

            # Рекурсивно обходим дочерние элементы
            for child in elem.findall(".//*", namespaces=namespaces):
                self.populate_full_tree(tree, child, id, level + 1)


class Switch(tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, width=40, height=20, *args, **kwargs)
        self.value = False  # Переключатель выключен по умолчанию
        self.configure(borderwidth=0, highlightthickness=0)  # Убираем рамку

        # Сам переключатель
        self.rect = self.create_rectangle(1, 1, 40, 20, outline='black', fill='red', width=1, tags='rect')

        # Белый кругляш
        self.oval = self.create_oval(2, 2, 18, 18, outline='black', fill='white', tags='oval')

        self.tag_bind('oval', '<1>', self.toggle)
        self.tag_bind('rect', '<1>', self.toggle)

    # Метод для переключения состояния Switch
    def toggle(self, event=None):
        self.value = not self.value
        fill_color = 'green' if self.value else 'red'
        oval_x0, oval_y0, oval_x1, oval_y1 = (22, 2, 38, 18) if self.value else (2, 2, 18, 18)
        self.coords(self.oval, oval_x0, oval_y0, oval_x1, oval_y1)
        self.itemconfig(self.rect, fill=fill_color)
        self.event_generate('<<SwitchToggled>>')  # Генерируем событие при переключении

    @property
    def is_on(self):
        return self.value


class ScrollableNotebook(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.notebook = ttk.Notebook(self.canvas)

        self.notebook.bind("<Configure>", self.on_configure)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="top", fill="both", expand=True)
        self.scrollbar.pack(side="bottom", fill="x")
        self.canvas.create_window((0, 0), window=self.notebook, anchor="nw")

    # Метод для обновления области прокрутки при изменении размера Notebook
    def on_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # Метод для добавления новой вкладки в ScrollableNotebook
    def add(self, tab, text):
        self.notebook.add(tab, text=text)

    def pack(self, *args, **kwargs):
        super().pack(*args, **kwargs)

class VerticalScrollableNotebook(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.notebook = ttk.Notebook(self.canvas)

        self.notebook.bind("<Configure>", self.on_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.create_window((0, 0), window=self.notebook, anchor="nw")

    def on_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def add(self, tab, text):
        self.notebook.add(tab, text=text)

    def pack(self, *args, **kwargs):
        super().pack(*args, **kwargs)


def main():
    root = ThemedTk()  # Используем ThemedTk вместо стандартного Tk
    app = XMLApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()  # Теперь main() вызывается только при прямом запуске файла
