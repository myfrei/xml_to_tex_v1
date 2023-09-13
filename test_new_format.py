import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import xml.etree.ElementTree as ET


def load_xml():
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
        add_tab(elem, "Result", 1)


def add_tab(elem, name, level):
    frame = ttk.Frame(tab_control)
    tab_control.add(frame, text=name)

    tree = ttk.Treeview(frame)
    tree["columns"] = ("Value",)
    tree.column("#0", width=150)
    tree.column("Value", width=100)
    tree.heading("#0", text="Name")
    tree.heading("Value", text="Value")

    populate_tree(tree, elem, "", level)

    tree.pack(expand=tk.YES, fill=tk.BOTH)


def populate_tree(tree, elem, parent="", level=1):
    for child in elem:
        name = child.attrib.get('callerName', child.attrib.get('name', 'Unknown'))
        value = child.text if child.text else "N/A"

        if name != "Unknown":  # Проверка на "Unknown"
            id = tree.insert(parent, tk.END, text=name, values=(value,))
            print(f"Added tree item: {name} with value: {value}")
            populate_tree(tree, child, id)

        if level == 1 and (
                child.tag == "tr:TestGroup" or child.tag == "tr:Test"):
            add_tab(child, name, level + 1)
        else:
            id = tree.insert(parent, tk.END, text=name, values=(value,))
            print(f"Added tree item: {name} with value: {value}")

            if level == 2 and (
                    child.tag == "tr:TestGroup" or child.tag == "tr:Test" or child.tag == "tr:SessionAction"):
                populate_tree(tree, child, id, level + 1)


root = tk.Tk()
root.title("XML Viewer")

tab_control = ttk.Notebook(root)
tab_control.pack(expand=tk.YES, fill=tk.BOTH)

menu = tk.Menu(root)
root.config(menu=menu)
file_menu = tk.Menu(menu)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=load_xml)

namespaces = {
    'trc': 'urn:IEEE-1636.1:2011:01:TestResultsCollection',
    'tr': 'urn:IEEE-1636.1:2011:01:TestResults',
    'c': 'urn:IEEE-1671:2010:Common',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'ts': 'www.ni.com/TestStand/ATMLTestResults/2.0'
}
  # Replace with your actual namespace

root.mainloop()
