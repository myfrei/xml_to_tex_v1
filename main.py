import os
import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk, simpledialog
from tkinter.scrolledtext import ScrolledText
from typing import Tuple
from ttkthemes import ThemedTk
from ScrollableNotebook import ScrollableNotebook
from Switch import Switch
from PIL import Image, ImageTk


def lookahead(iterable):
    # Get an iterator and pull the first value.
    it = iter(iterable)
    try:
        last = next(it)
    except StopIteration:
        return
    # Run the iterator to exhaustion (starting from the second value).
    for val in it:
        # Report the *previous* value (more to come).
        yield last, False
        last = val
    # Report the last value.
    yield last, True


class MyTreeview(ttk.Treeview):
    def get_line(self, rowid):
        return '\t'.join((
            self.item(rowid, 'text'),
            *self.item(rowid, 'values')
        ))

    def write(self, f, parent='', is_latest_parent=False, level=0):
        for child, is_latest in lookahead(self.get_children(parent)):
            prefix = ' '.join((
                *('│' * (level - is_latest_parent)),
                '  ' * is_latest_parent + '└─' if is_latest else '├─'
            ))

            line = prefix + self.get_line(child).rstrip() + '\n'
            f.write(line)
            self.write(f, child, is_latest, level + 1)


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

        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'photo.jpg')
        img = Image.open(img_path)
        img = img.resize((300, 300))
        self.logo = ImageTk.PhotoImage(img)
        ttk.Label(self, image=self.logo).grid(row=0, column=1, rowspan=4, padx=5, pady=5, sticky='ne')

        self.apply_button = ttk.Button(self, text="F.A.Q.", command=self.show_faq)
        self.apply_button.grid(row=4, column=1, padx=5, pady=5, sticky='sw')

        self.theme_combobox = ttk.Combobox(self, values=self.controller.available_themes, width=8)
        if self.controller.available_themes:
            self.theme_combobox.set(self.controller.available_themes[0])
        self.theme_combobox.grid(row=4, column=1, padx=5, pady=10, ipadx=5, ipady=1, sticky='s')

        self.apply_button = ttk.Button(self, text="Применить", command=self.apply_theme)
        self.apply_button.grid(row=4, column=1, padx=5, pady=5, sticky='se')

        self.populate_file_list(os.path.dirname(os.path.abspath(__file__)))

        # Конфигурация grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

    def apply_theme(self):
        selected_theme = self.theme_combobox.get()  # Получаем выбранную тему
        if selected_theme:
            self.controller.root.set_theme(selected_theme)  # Применяем выбранную тему

    def show_faq(self):
        # Создайте новое окно для отображения информации из текстового файла
        faq_window = tk.Toplevel(self)
        faq_window.title("F.A.Q.")

        # Загрузите информацию из текстового файла с явно указанной кодировкой UTF-8
        try:
            with open("faq.txt", "r", encoding="utf-8") as file:
                faq_text = file.read()
                text_widget = ScrolledText(faq_window, wrap=tk.WORD, width=50, height=20)
                text_widget.insert(tk.END, faq_text)
                text_widget.pack(fill=tk.BOTH, expand=True)
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл FAQ.txt не найден.")

        # Создайте рамку для размещения виджетов для отправки писем
        email_frame = tk.Frame(faq_window)
        email_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Добавьте виджеты для отправки писем внутри рамки
        tk.Label(email_frame, text="email для обратной связи: epbazh@spels.ru").pack()

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


def generate_file(*trees: Tuple[str, MyTreeview]):
    filetypes = [("TeX", "*.tex"), ("Text", "*.txt")]
    file_path = filedialog.asksaveasfilename(defaultextension=".tex", filetypes=filetypes)
    if not file_path:
        return

    with open(file_path, 'w', encoding='utf-8') as file:
        for tree_title, tree in trees:
            file.write(f"{tree_title}\n")
            tree.write(file)


class XMLApp:
    def __init__(self, root):
        self.root = root
        self.treeviews = []
        self.available_themes = self.root.get_themes()
        self.root.set_theme('blue')
        self.root.title("XML Viewer")
        self.root.geometry("700x350+100+100")
        self.root.resizable(False, False)
        self.start_frame = StartFrame(root, self)  # Обратите внимание, что мы передаем self как controller
        self.start_frame.pack(expand=tk.YES, fill=tk.BOTH)

    def copy_line(self, event):
        rowid = event.widget.focus()
        line = event.widget.get_line(rowid)
        if line:
            self.root.clipboard_clear()
            self.root.clipboard_append(line)
            self.root.update()

    def copy_group(self, event):
        tree = event.widget
        rowid = tree.focus()

        children = tree.get_children(rowid)
        self.root.clipboard_clear()
        self.root.clipboard_append('\n'.join(  # all lines
            tree.get_line(child) for child in children
        ))
        self.root.update()

    @staticmethod
    def edit_value(event):
        rowid = event.widget.focus()  # Получаем выделенный элемент
        column = event.widget.identify_column(event.x)  # Определяем, в каком столбце произошел клик
        col_num = int(column[1:])  # Получаем номер столбца

        new_value = simpledialog.askstring("Edit Value", f"Enter new value")
        if new_value is not None and new_value.strip():
            line = [event.widget.item(rowid, 'text'), *event.widget.item(rowid, 'values')]
            line[col_num] = new_value
            event.widget.item(rowid, text=line[0], values=line[1:])

    def start_analysis(self, file_path):
        result_window = tk.Toplevel(self.root)
        result_window.title("Result")
        result_window.geometry("1200x500")
        result_window.resizable(True, True)

        root_note = ScrollableNotebook(result_window, wheelscroll=True, tabmenu=True)
        root_note.pack(expand=tk.YES, fill=tk.BOTH)

        if not file_path:
            print("No file selected.")
            return

        try:
            root = ET.parse(file_path).getroot()
        except Exception as e:
            print(f"Failed to parse XML: {e}")
            return

        self.populate_root_notebook(root, root_note)

    def populate_root_notebook(self, xml_root, tab_control):
        namespaces = {'tr': 'urn:IEEE-1636.1:2011:01:TestResults'}

        for elem in xml_root.findall('.//tr:ResultSet', namespaces=namespaces):
            for child in elem.findall('./*', namespaces=namespaces):
                tag = child.tag.split('}')[-1]
                name = child.get('callerName', child.get('name'))
                if tag == 'Test':
                    self.add_treeview_tab(child, name, tab_control)
                elif tag == 'TestGroup':
                    if name != "Unknown":
                        self.add_root_tab(child, name, tab_control)

    def add_root_tab(self, xml_element, tab_name: str, notebook: ttk.Notebook):
        # Создаем новый Frame для каждой вкладки
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=tab_name)

        # Создаем новый Notebook внутри frame
        sub_notebook = ScrollableNotebook(frame, wheelscroll=True, tabmenu=True)
        sub_notebook.pack(expand=True, fill='both')  # Используем pack для размещения Notebook внутри Frame

        # Теперь для каждого дочернего элемента xml_element добавим вкладку в sub_notebook
        for child in xml_element:
            child_name = child.get('callerName', child.get('name'))
            if child_name is not None:
                self.treeviews.append(
                    (child_name, self.add_treeview_tab(child, child_name, sub_notebook))
                )

    def add_treeview_tab(self, xml_element, tab_name, notebook):
        # Создаем Frame для каждой вкладки
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=tab_name)

        tree = MyTreeview(frame, columns=("status", "value", "valid_values"), selectmode='browse')
        scroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(expand=False, fill='y', side='right')
        tree.pack(expand=True, fill=tk.BOTH)

        tree.column("#0", width=270, minwidth=270)
        tree.column("status", width=150, minwidth=150)
        tree.column("value", width=150, minwidth=150)
        tree.column("valid_values", width=150, minwidth=150)

        tree.heading("#0", text="TreeView")
        tree.heading("status", text="Status")
        tree.heading("value", text="Value")
        tree.heading("valid_values", text="Valid Values")

        tree.bind("<Button-3>", self.copy_line)
        tree.bind("<Control-c>", self.copy_line)
        tree.bind("<Double-1>", self.edit_value)
        tree.bind("<Control-e>", self.edit_value)
        tree.bind("<Control-r>", self.copy_group)

        export_button = ttk.Button(tree, text='Export This',
                                   command=lambda: generate_file((tab_name, tree)))
        export_all_button = ttk.Button(tree, text="Export All",
                                       width=export_button['width'],
                                       command=lambda: generate_file(*self.treeviews))
        export_all_button.pack(expand=False, anchor='se', side='bottom')
        export_button.pack(expand=False, anchor='se', side='bottom')

        self.populate_tree(tree, xml_element)
        return tree

    # Метод для добавления элементов в дерево
    def populate_tree(self, tree, elem, parent=""):
        namespaces = {
            "tr": "urn:IEEE-1636.1:2011:01:TestResults",
            "c": "urn:IEEE-1671:2010:Common"
        }

        name = elem.get('callerName', elem.get('name'))
        if name is not None:
            # Извлечение значения атрибута 'value' из тега 'tr:Outcome' или 'tr:ActionOutcome'
            if (outcome := elem.find('./tr:Outcome', namespaces=namespaces)) is None:
                outcome = elem.find('./tr:ActionOutcome', namespaces=namespaces)
            status = outcome.get('value', 'N/A') if outcome is not None else 'N/A'

            if elem.tag.endswith("SessionAction"):
                parent = tree.insert(parent, tk.END, text=name, values=(status, '', ''))
            elif elem.tag.endswith("Test"):
                value_elem = elem.find('./tr:Data/c:Collection/c:Item/c:Datum', namespaces=namespaces)
                value = value_elem.get('value', 'N/A') if value_elem is not None else 'N/A'
                parent = tree.insert(parent, tk.END, text=name, values=(status, value, ''))
            elif elem.tag.endswith("TestResult"):
                value_elem = elem.find("./tr:TestData/c:Datum", namespaces=namespaces)
                value = value_elem.get("value") if value_elem is not None else 'N/A'

                low_limit_elem = elem.find(
                    "./tr:TestLimits/tr:Limits/c:LimitPair/c:Limit[@comparator='GE']/c:Datum",
                    namespaces=namespaces)
                low_limit = low_limit_elem.get("value") if low_limit_elem is not None else ' '

                high_limit_elem = elem.find(
                    "./tr:TestLimits/tr:Limits/c:LimitPair/c:Limit[@comparator='LE']/c:Datum",
                    namespaces=namespaces)
                high_limit = high_limit_elem.get("value") if high_limit_elem is not None else ' '

                valid_values_str = f"{low_limit} < > {high_limit}"
                values = (status, value, valid_values_str)

                parent = tree.insert(parent, tk.END, text=name, values=values)

        group_map = dict()
        existing = set()
        for child in elem:
            name = child.get('callerName', child.get('name'))
            if name is None:
                continue
            if name in existing and name not in group_map:
                group_map[name] = tree.insert(parent, tk.END, text=name)
            existing.add(name)
        del existing

        for child in elem:
            name = child.get('callerName', child.get('name'))
            if name is None:
                continue
            self.populate_tree(tree, child, parent=group_map.get(name, parent))


def main():
    root = ThemedTk()  # Используем ThemedTk вместо стандартного Tk для задания темы
    XMLApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
