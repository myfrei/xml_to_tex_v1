import math
import os
import sys
import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import filedialog, scrolledtext
from tkinter import messagebox
from tkinter import ttk, simpledialog
from typing import Tuple

from PIL import Image, ImageTk
from pkg_resources import resource_string
from ttkthemes import ThemedTk

from ScrollableNotebook import ScrollableNotebook
from Switch import Switch


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
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.checkboxes = {}  # Словарь для отслеживания состояния чекбоксов
        self.bind('<ButtonRelease-1>', self.on_click)  # Обработчик кликов
        self["columns"] = ("checkbox", "status", "value", "valid_values")

        self.column("#0", width=0, stretch=tk.NO)  # Скрываем первый столбец
        self.column("checkbox", width=20, anchor='center')
        self.heading("checkbox", text='')

        # Настройка остальных столбцов
        self.column("status", width=150)
        self.column("value", width=150)
        self.column("valid_values", width=150)

        self.heading("status", text="Status")
        self.heading("value", text="Value")
        self.heading("valid_values", text="Valid Values")

    def get_line(self, rowid):
        # Извлекаем текст и значения, связанные с узлом
        return '\t'.join([self.item(rowid, 'text')] + list(self.item(rowid, 'values')))

    def add_item_with_checkbox(self, parent, text, values):
        checkbox_state = tk.BooleanVar(value=True)  # Включен по умолчанию
        rowid = self.insert(parent, tk.END, text=text, values=('', *values))
        self.checkboxes[rowid] = checkbox_state
        self.update_checkbox(rowid)
        return rowid

    def update_checkbox(self, rowid):
        checkbox_symbol = "☑" if self.checkboxes[rowid].get() else "☐"
        self.set(rowid, "checkbox", checkbox_symbol)  # Обновление символа чекбокса

    def on_click(self, event):
        region = self.identify("region", event.x, event.y)
        if region == "cell":
            col = self.identify_column(event.x)
            if col == "#1":  # Проверяем, что клик был в колонке чекбоксов
                rowid = self.identify_row(event.y)
                if rowid in self.checkboxes:
                    self.toggle_checkbox_and_parents(rowid)

    def toggle_checkbox_and_parents(self, rowid):
        current_value = self.checkboxes[rowid].get()
        self.checkboxes[rowid].set(not current_value)
        self.update_checkbox(rowid)

        # Рекурсивно обновляем чекбоксы родителей
        self.update_parent_checkboxes(self.parent(rowid))

    def update_parent_checkboxes(self, parentid):
        if parentid:
            self.checkboxes[parentid].set(True)
            self.update_checkbox(parentid)
            self.update_parent_checkboxes(self.parent(parentid))

    def write(self, f, parent='', is_latest_parent=False, level=0):
        for child, is_latest in lookahead(self.get_children(parent)):
            if self.checkboxes.get(child) and not self.checkboxes[child].get():
                continue

            # Получаем данные строки
            line = self.get_line(child).rstrip() + '\n'
            f.write(line)

            # Рекурсивно обрабатываем дочерние элементы
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
        self.dir_button.grid(row=0, column=0, padx=5, pady=5, sticky='se')

        self.file_listbox = tk.Listbox(self, width=25)
        self.file_listbox.grid(row=3, column=0, padx=5, pady=5, sticky='nsew')

        self.skip_user_defined_var = tk.BooleanVar()
        self.skip_user_defined_checkbox = ttk.Checkbutton(self, text="Skip UserDefined",
                                                          variable=self.skip_user_defined_var)
        self.skip_user_defined_checkbox.grid(row=4, column=0, padx=5, pady=(0, 30), sticky='sw')

        self.rounding_var = tk.StringVar(value="no rounding")
        self.rounding_combobox = ttk.Combobox(self, textvariable=self.rounding_var, values=[
            "no rounding",
            "up to 2 characters upward",
            "up to 2 decimal places",
            "up to 3 characters upward",
            "up to 3 decimal places"
        ])
        self.rounding_combobox.set("no rounding")
        self.rounding_combobox.grid(row=4, column=0, padx=5, pady=(0, 5), sticky='sw')

        ttk.Button(self, text="Start", command=self.start).grid(row=4, column=0, padx=5, pady=5, sticky='se')

        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'photo.jpg')
        img = Image.open(img_path)
        img = img.resize((300, 300))
        self.logo = ImageTk.PhotoImage(img)
        ttk.Label(self, image=self.logo).grid(row=0, column=1, rowspan=4, padx=5, pady=5, sticky='ne')

        self.apply_button = ttk.Button(self, text="Инструкция", command=self.show_faq)
        self.apply_button.grid(row=4, column=1, padx=5, pady=5, sticky='sw')

        self.theme_combobox = ttk.Combobox(self, values=self.controller.available_themes, width=8)
        if self.controller.available_themes:
            self.theme_combobox.set(self.controller.available_themes[0])
        self.theme_combobox.grid(row=4, column=1, padx=5, pady=(5, 10), sticky='s')

        self.apply_button = ttk.Button(self, text="Применить", command=self.apply_theme)
        self.apply_button.grid(row=4, column=1, padx=5, pady=5, sticky='se')

        # Определите путь к корневой директории в зависимости от способа запуска
        if getattr(sys, 'frozen', False):
            # Запуск из exe
            self.root_dir = os.path.dirname(sys.executable)
        else:
            # Запуск из скрипта Python
            self.root_dir = os.path.dirname(os.path.abspath(__file__))

        #log_file_path = os.path.join(self.root_dir, 'app.log')
        #logging.basicConfig(filename=log_file_path, level=logging.DEBUG,
        #                    format='%(asctime)s - %(levelname)s - %(message)s')
        #logging.debug(self.root_dir)

        self.populate_file_list(self.root_dir)

        # Конфигурация grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

    def apply_theme(self):
        selected_theme = self.theme_combobox.get()  # Получаем выбранную тему
        if selected_theme:
            self.controller.root.set_theme(selected_theme)  # Применяем выбранную тему

    def show_faq(self):
        faq_window = tk.Toplevel(self)
        faq_window.title("Инструкция")

        try:
            if getattr(sys, 'frozen', False):
                # Если приложение запущено как исполняемый файл
                faq_text = resource_string(__name__, "tamplete/FAQ.txt").decode('utf-8')
            else:
                # Если приложение запущено как скрипт
                with open("tamplete/FAQ.txt", "r", encoding="utf-8") as file:
                    faq_text = file.read()

            text_widget = scrolledtext.ScrolledText(faq_window, wrap=tk.WORD, width=55, height=30)
            text_widget.insert(tk.END, faq_text)
            text_widget.pack(fill=tk.BOTH, expand=True)
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл FAQ.txt не найден.")

        email_frame = tk.Frame(faq_window)
        email_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        email_label = tk.Label(email_frame, text="email для обратной связи: epbazh@spels.ru", fg="blue", cursor="hand2")
        email_label.pack()
        email_label.bind("<Button-1>", self.copy_email_to_clipboard)

    def copy_email_to_clipboard(self, event):
        email = "epbazh@spels.ru"
        self.clipboard_clear()
        self.clipboard_append(email)
        messagebox.showinfo("Копирование", f"Адрес {email} скопирован в буфер обмена.")

    def toggle_dir_choice(self):
        if self.switch.is_on:  # Используйте свойство is_on нового виджета Switch
            self.dir_entry.config(state='normal')
            self.dir_button.config(state='normal')
        else:
            self.dir_entry.config(state='disabled')
            self.dir_button.config(state='disabled')
            self.populate_file_list(self.root_dir)

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
        directory = self.dir_entry.get() if self.switch.is_on else self.root_dir
        if not selected_file:
            messagebox.showerror("Ошибка", "Файл не выбран.")
            return

        if not directory:
            directory = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(directory, selected_file)

        # Передаем состояние чекбокса в метод start_analysis
        self.controller.start_analysis(file_path, self.skip_user_defined_var.get())


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

    def copy_cell_value(self, event):
        tree = event.widget
        rowid = tree.focus()
        col_id = tree.identify_column(event.x)
        col_num = int(col_id.split("#")[-1]) - 1
        if col_num >= 0:  # Убедитесь, что номер столбца валиден
            value = tree.item(rowid, 'values')[col_num]
            self.root.clipboard_clear()
            self.root.clipboard_append(value)
            self.root.update()

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
        tree = event.widget
        rowid = tree.focus()
        col_id = tree.identify_column(event.x)
        col_num = int(col_id.split("#")[-1]) - 1

        if col_num >= 0:  # Убедитесь, что номер столбца валиден
            old_value = tree.item(rowid, 'values')[col_num]
            column_name = tree.heading(col_id, 'text')

            new_value = simpledialog.askstring(f"Edit {column_name}", f"Enter new value:", initialvalue=old_value)
            if new_value is not None:
                line = [tree.item(rowid, 'text'), *tree.item(rowid, 'values')]
                line[col_num + 1] = new_value  # +1 потому что первый элемент в line - это текст, а не значение
                tree.item(rowid, text=line[0], values=line[1:])

    def start_analysis(self, file_path, skip_user_defined):
        result_window = tk.Toplevel(self.root)
        file_name = os.path.basename(file_path)  # Получаем имя файла с расширением
        file_name_without_extension = os.path.splitext(file_name)[0]  # Убираем расширение файла
        result_window.title(f"Result_{file_name_without_extension}")
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

        self.populate_root_notebook(root, root_note, skip_user_defined)

    def populate_root_notebook(self, xml_root, tab_control, skip_user_defined):
        namespaces = {'tr': 'urn:IEEE-1636.1:2011:01:TestResults'}

        for elem in xml_root.findall('.//tr:ResultSet', namespaces=namespaces):
            for child in elem.findall('./*', namespaces=namespaces):
                tag = child.tag.split('}')[-1]
                name = child.get('callerName', child.get('name'))
                if tag == 'Test':
                    # Проверяем статус и пропускаем элемент, если необходимо
                    status = child.find('./tr:Outcome', namespaces=namespaces)
                    if skip_user_defined and status is not None and status.get('value') == 'UserDefined':
                        continue
                    self.add_treeview_tab(child, name, tab_control, skip_user_defined)
                elif tag == 'TestGroup':
                    if name != "Unknown":
                        self.add_root_tab(child, name, tab_control, skip_user_defined)

    def add_root_tab(self, xml_element, tab_name: str, notebook: ttk.Notebook, skip_user_defined):
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
                    (child_name, self.add_treeview_tab(child, child_name, sub_notebook, skip_user_defined))
                )

    def add_treeview_tab(self, xml_element, tab_name, notebook, skip_user_defined):
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
        tree.bind("<Control-w>", self.copy_cell_value)

        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(expand=False, anchor='sw', side='bottom', fill='x')

        export_button = ttk.Button(tree, text='Export This',
                                   command=lambda: generate_file((tab_name, tree)))
        export_button.pack(expand=False, anchor='se', side='right')
        export_all_button = ttk.Button(tree, text="Export All",
                                       width=export_button['width'],
                                       command=lambda: generate_file(*self.treeviews))
        export_all_button.pack(expand=False, anchor='se', side='bottom')

        toggle_checkboxes_button = ttk.Button(buttons_frame, text="Вкл/Выкл все чекбоксы",
                                              command=lambda: self.toggle_all_checkboxes(tree))
        toggle_checkboxes_button.pack(expand=False, anchor='sw', side='left')

        self.populate_tree(tree, xml_element, skip_user_defined=skip_user_defined)
        return tree

    def toggle_all_checkboxes(self, tree):
        new_state = not any(tree.checkboxes[child].get() for child in tree.checkboxes)
        for child in tree.checkboxes:
            tree.checkboxes[child].set(new_state)
            tree.update_checkbox(child)

    def round_value(self, value):
        rounding_option = self.start_frame.rounding_var.get()
        try:
            num = float(value)
        except ValueError:
            return value  # Возвращаем исходное значение, если оно не является числом

        if rounding_option == "up to 2 characters upward":
            return f"{round(num, 2):.2f}"
        elif rounding_option == "up to 2 decimal places":
            return f"{math.floor(num * 100) / 100:.2f}"
        elif rounding_option == "up to 3 characters upward":
            return f"{round(num, 3):.3f}"
        elif rounding_option == "up to 3 decimal places":
            return f"{math.floor(num * 1000) / 1000:.3f}"
        else:  # "no rounding" или любой другой вариант
            return value

    # Метод для добавления элементов в дерево
    def populate_tree(self, tree, elem, parent="", skip_user_defined=False):
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

            if skip_user_defined and status == "UserDefined":
                pass
            else:
                values = []
                if elem.tag.endswith("SessionAction"):
                    values = (status, '', '')
                elif elem.tag.endswith("Test"):
                    value_elem = elem.find('./tr:Data/c:Collection/c:Item/c:Datum', namespaces=namespaces)
                    value = value_elem.get('value', 'N/A') if value_elem is not None else 'N/A'
                    values = (status, value, '')
                elif elem.tag.endswith("TestResult"):
                    value_elem = elem.find("./tr:TestData/c:Datum", namespaces=namespaces)
                    value = value_elem.get("value") if value_elem is not None else 'N/A'
                    value = self.round_value(value)

                    low_limit_elem = elem.find(
                        "./tr:TestLimits/tr:Limits/c:LimitPair/c:Limit[@comparator='GE']/c:Datum",
                        namespaces=namespaces)
                    low_limit = low_limit_elem.get("value") if low_limit_elem is not None else None

                    high_limit_elem = elem.find(
                        "./tr:TestLimits/tr:Limits/c:LimitPair/c:Limit[@comparator='LE']/c:Datum",
                        namespaces=namespaces)
                    high_limit = high_limit_elem.get("value") if high_limit_elem is not None else None

                    if low_limit is not None and high_limit is not None:
                        valid_values_str = f"{low_limit} ÷ {high_limit}"
                    elif low_limit is not None:
                        valid_values_str = f"> {low_limit}"
                    elif high_limit is not None:
                        valid_values_str = f"< {high_limit}"
                    else:
                        valid_values_str = "Не определено"

                    values = (status, value, valid_values_str)

                parent_id = tree.add_item_with_checkbox(parent, name, values)

                # Проверяем статус и применяем красный цвет фона для элементов с FAIL
                if "Failed" in values:
                    tree.item(parent_id, tags=('failed',))
                    tree.tag_configure('failed', background='red')

                # Рекурсивно обрабатываем дочерние элементы
                for child in elem:
                    self.populate_tree(tree, child, parent_id, skip_user_defined)


def main():
    root = ThemedTk()  # Используем ThemedTk вместо стандартного Tk для задания темы
    XMLApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
