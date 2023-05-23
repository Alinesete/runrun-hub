# This file was generated by the Tkinter Designer by Parth Jadhav
# https://github.com/ParthJadhav/Tkinter-Designer
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import (
Tk,
Canvas,
Text,
Button,
PhotoImage,
Entry,
StringVar,
font,
DISABLED,
NORMAL,
ttk,
)
from tkinter.filedialog import askopenfilename
from py.start_process import start_process
from box import open_popup

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r".\assets")

wide = False
client_list = {}
client = []
task_list = {}
project = []
task_list = {}
tasks = []

# -------------------------------------------

def redirect_stdout(widget):
    class StdoutRedirector:
        def __init__(self, widget):
            self.widget = widget

        def write(self, text):
            self.widget.insert("1.0", text)

        def flush(self):
            pass

    sys.stdout = StdoutRedirector(widget)

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def change_geometry():
    global wide
    if wide:
        window.geometry("520x600")
        btn_expand.config(image=btn_expand_img)
        wide = False
    else:
        window.geometry("1048x600")
        btn_expand.config(image=btn_expand_img_alt)
        wide = True

def open_file_dialog():
    file_path = askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    entry_file.delete(0, "end")
    entry_file.insert(0, file_path)

def get_client_id():
    selected_name = combo_client.get()
    if not selected_name:
        print("Select a client")
        return
    for client_id, (name, projects_count) in client_list.items():
        if name == selected_name:
            return client_id
    return None

def get_project_id():
    selected_name = combo_project.get()
    if not selected_name:
        print("Select a project")
        return
    for project_id, (name, tasks_count) in task_list.items():
        if name == selected_name:
            return project_id
    return None

def get_client_count():
    selected_name = combo_client.get()
    for client_id, (name, projects_count) in client_list.items():
        if name == selected_name:
            return projects_count
    return None

def get_project_count():
    selected_name = combo_project.get()
    for project_id, (name, tasks_count) in task_list.items():
        if name == selected_name:
            return tasks_count
    return None

# -------------------------------------------

def refresh_client():
    global client
    global client_list
    client_list = start_process(2)
    client = [name for name, _ in client_list.values()]
    combo_client["values"] = client


def refresh_project():
    entry_log.delete("1.0", tk.END)
    global project
    global task_list
    client_name = get_client_id()
    client_count = get_client_count()

    if not client_count:
        print("There are no projects under the client {}.".format(client_name))
        return

    task_list = start_process(3, client_name, client_count)
    project = [name for name, _ in task_list.values()]
    combo_project["values"] = project

def refresh_project_drop(event):
    refresh_project()

def refresh_task():
    entry_log.delete("1.0", tk.END)
    global tasks
    global task_list
    selected_project = get_project_id()
    selected_count = get_project_count()
    task_list = start_process(4, selected_project, selected_count)
    open_popup(window, task_list, btn_att)
    refresh_project()

def start_project_creation():
    entry_log.delete("1.0", tk.END)
    file_path = entry_file.get()

    if file_path.endswith(".xlsx"):
        thread = threading.Thread(target=start_process, kwargs={"command": 1, "extra": file_path, "window":window, "button":btn_start_project_creation})
        thread.start()
        
    else:
        print("File must be XLSX.")

# -------------------------------------------

window = Tk()
window.iconbitmap("./assets/icon.ico")
window.title("RunRun Hub")
window.geometry("520x600")
window.configure(bg="#1A253B")
selected_name = StringVar(window)

canvas = Canvas(
    window,
    bg="#1A253B",
    height=600,
    width=1048,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)

canvas.place(x=0, y=0)
canvas.create_rectangle(
    543.0,
    39.0,
    1019.0,
    572.0,
    fill="#FFFFFF",
    outline="")

canvas.create_text(
    563.0,
    59.0,
    anchor="nw",
    text="Client:",
    fill="#1A253B",
    font=("Inter", 12 * -1)
)

combo_client = ttk.Combobox(
    window,
    values=client,
    state="readonly"
)
combo_client.place(
    x=563.0,
    y=80.0,
    width=402.0,
    height=20.0
)

combo_client.bind("<<ComboboxSelected>>", refresh_project_drop)

btn_ref_cliente_img = PhotoImage(
    file=relative_to_assets("button_refresh.png"))
btn_ref_cliente = Button(
    image=btn_ref_cliente_img,
    borderwidth=0,
    highlightthickness=0,
    command=refresh_client,
    relief="flat"
)
btn_ref_cliente.place(
    x=975.0,
    y=80.0,
    width=23.0,
    height=20.0
)

canvas.create_text(
    563.0,
    110.0,
    anchor="nw",
    text="Project: ",
    fill="#000000",
    font=("Inter", 12 * -1)
)

combo_project = ttk.Combobox(
    window,
    state="readonly"
)
combo_project.place(
    x=563.0,
    y=134.0,
    width=402.0,
    height=20.0
)

btn_ref_project_img = PhotoImage(
    file=relative_to_assets("button_refresh.png"))
btn_ref_project = Button(
    image=btn_ref_project_img,
    borderwidth=0,
    highlightthickness=0,
    command=refresh_project,
    relief="flat"
)
btn_ref_project.place(
    x=975.0,
    y=134.0,
    width=23.0,
    height=20.0
)

btn_att_img = PhotoImage(
    file=relative_to_assets("button_close_tasks.png"))
btn_att = Button(
    image=btn_att_img,
    borderwidth=0,
    highlightthickness=0,
    command=refresh_task,
    relief="flat"
)
btn_att.place(
    x=733.0,
    y=511.0,
    width=108.0,
    height=36.0
)

textbox = Text(canvas, bg="#D9D9D9", wrap="word")
textbox.place(x=563.0, y=172.0, width=998.0-563.0, height=487.0-172.0)
font_style = font.Font(family="Arial", size=10)
textbox.configure(font=font_style)

# -------------------------------------------

btn_expand_img = PhotoImage(file=relative_to_assets("button_expand.png"))
btn_expand_img_alt = PhotoImage(
    file=relative_to_assets("button_expand_alt.png"))

btn_expand = tk.Button(
    image=btn_expand_img,
    borderwidth=0,
    highlightthickness=0,
    command=change_geometry,
    relief="flat"
)

btn_expand.place(x=500.0, y=0.0, width=20.0, height=600.0)

banner_img = PhotoImage(
    file=relative_to_assets("banner.png"))
banner = canvas.create_image(
    257.0,
    123.0,
    image=banner_img
)

entry_file_image = PhotoImage(
    file=relative_to_assets("entry_file.png"))
entry_file_bg = canvas.create_image(
    229.5,
    270.0000009536743,
    image=entry_file_image
)
entry_file = Entry(
    bd=0,
    bg="#D9D9D9",
    fg="#808080",
    highlightthickness=0,
)
entry_file.place(
    x=33.0,
    y=256.0,
    width=393.0,
    height=26.000001907348633
)
texto = 'Excel file with "Name" column.'
entry_file.insert(0, texto)

btn_get_file_image = PhotoImage(
    file=relative_to_assets("button_file.png"))
btn_get_file = Button(
    image=btn_get_file_image,
    borderwidth=0,
    highlightthickness=0,
    command=open_file_dialog,
    relief="flat"
)
btn_get_file.place(
    x=438.0,
    y=256.0,
    width=28.0,
    height=28.0
)

btn_start_project_creation_img = PhotoImage(
    file=relative_to_assets("button_start.png"))
btn_start_project_creation = Button(
    image=btn_start_project_creation_img,
    borderwidth=0,
    highlightthickness=0,
    command=start_project_creation,
    relief="flat"
)
btn_start_project_creation.place(
    x=145.0,
    y=310.0,
    width=225.0,
    height=61.0
)

entry_log_image = PhotoImage(
    file=relative_to_assets("entry_log.png"))
entry_log_bg = canvas.create_image(
    250.5,
    471.5,
    image=entry_log_image
)
entry_log = Text(
    bd=0,
    bg="#D0DFFF",
    fg="#000716",
    highlightthickness=0,
    font=("Helvetica", 10)
)
entry_log.place(
    x=22.0,
    y=397.0,
    width=457.0,
    height=147.0
)

window.resizable(False, False)
redirect_stdout(entry_log)
window.mainloop()