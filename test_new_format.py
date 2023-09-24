import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk

class StartFrame(ttk.Frame):
    def __init__(self, container, controller, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.controller = controller

        # Добавление логотипа
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'photo.jpg')
        img = Image.open(img_path)  # Загрузка изображения с помощью Pillow
        self.logo = ImageTk.PhotoImage(img)
        ttk.Label(self, image=self.logo).pack(side="right", padx=10)

        self.use_custom_dir = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text="Choose directory", variable=self.use_custom_dir,
                        command=self.toggle_dir_choice).pack(anchor=tk.W, pady=5)

        self.dir_entry = ttk.Entry(self, state='disabled')
        self.dir_entry.pack(fill=tk.X, padx=5, pady=5)
        self.dir_button = ttk.Button(self, text="Choose Directory", command=self.choose_directory, state='disabled')
        self.dir_button.pack(pady=5)

        self.file_listbox = tk.Listbox(self)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Button(self, text="Start", command=self.start).pack(pady=5)

        self.populate_file_list(os.path.dirname(os.path.abspath(__file__)))

    def toggle_dir_choice(self):
        if self.use_custom_dir.get():
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
            print("No file selected.")
            return

        if not directory:
            directory = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(directory, selected_file)
        print(f"Selected file: {file_path}")

        self.controller.start_analysis(file_path)


class XMLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XML Viewer")
        self.root.geometry("800x600")  # Установите размер окна
        self.root.resizable(False, False)  # Запретить изменение размера окна
        self.init_ui()

    def init_ui(self):
        self.start_frame = StartFrame(self.root, self)
        self.start_frame.pack(expand=tk.YES, fill=tk.BOTH)

        self.tab_control = ttk.Notebook(self.root)
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.load_xml)

    def start_analysis(self, file_path):
        result_window = tk.Toplevel(self.root)
        result_window.title("Result")
        tab_control = ttk.Notebook(result_window)
        tab_control.pack(expand=tk.YES, fill=tk.BOTH)
        self.load_xml(file_path, tab_control)

    def load_xml(self, file_path, tab_control):
        namespaces = {
            'trc': 'urn:IEEE-1636.1:2011:01:TestResultsCollection',
            'tr': 'urn:IEEE-1636.1:2011:01:TestResults',
            'c': 'urn:IEEE-1671:2010:Common',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'ts': 'www.ni.com/TestStand/ATMLTestResults/2.0'
        }
        if not file_path:
            file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
            if not file_path:
                print("No file selected.")
                return
            print(f"Selected file: {file_path}")

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except Exception as e:
            print(f"Failed to parse XML: {e}")
            return

        for elem in root.findall(".//tr:ResultSet", namespaces=namespaces):
            self.add_tab(elem, "Result", 1, tab_control)  # Здесь создается новая вкладка с именем "Result"

    def add_tab(self, elem, name, level, tab_control):
        frame = ttk.Frame(tab_control)
        tab_control.add(frame, text=name)

        tree = ttk.Treeview(frame)
        tree["columns"] = ("Value",)
        tree.column("#0", width=150)
        tree.column("Value", width=100)
        tree.heading("#0", text="Name")
        tree.heading("Value", text="Value")

        self.populate_tree(tree, elem)

        tree.pack(expand=tk.YES, fill=tk.BOTH)

    def populate_tree(self, tree, elem, parent="", level=1):
        for child in elem:
            name = child.attrib.get('callerName', child.attrib.get('name', 'Unknown'))
            value = child.text if child.text else "N/A"

            if name == "Unknown":
                continue

            id = tree.insert(parent, tk.END, text=name, values=(value,))
            self.populate_tree(tree, child, id, level + 1)


def main():
    root = tk.Tk()
    app = XMLApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()  # Теперь main() вызывается только при прямом запуске файла