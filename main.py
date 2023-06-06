import sys
import threading
import subprocess
import time
import socket
from pathlib import Path
import tkinter as tk
from tkinter import (Tk, Canvas, Text, Button,PhotoImage, Entry, StringVar, ttk,)
from tkinter.filedialog import askopenfilename
from py.start import start_process
from box import open_popup
from bulk import BulkPopup
from py.report import generate_task_csv, generate_project_csv, log_task, log_project

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r".\assets")

wide = False
client_list = {}
client = []
tasks = {}
task_list = {}
project = []
botoes = True
task_frame = ""
projects = []

# Send the cmd lines to the log area
def redirect_stdout(widget):
    class StdoutRedirector:
        def __init__(self, widget):
            self.widget = widget

        def write(self, text):
            self.widget.insert("1.0", text)

        def flush(self):
            pass

    sys.stdout = StdoutRedirector(widget)

# Checks if runrun.it is reachable
def ping_runrun():
    global botoes

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            resultado = sock.connect_ex(('35.190.30.45', 80))
            sock.close()

            if resultado == 0:
                conexao_ruim = False
            else:
                conexao_ruim = True

            if conexao_ruim:
                canvas.itemconfig(ping_sensor, fill='red')
                if botoes:
                    disable_elements()
            else:
                canvas.itemconfig(ping_sensor, fill='green')
                if not botoes:
                    enable_elements()

        except subprocess.CalledProcessError:
            canvas.itemconfig(ping_sensor, fill='red')
            if botoes:
                disable_elements()
        time.sleep(2)

# Disabling and enabling the buttons and selection boxes
def disable_elements():
    global botoes
    combo_client.config(state='disabled')
    combo_project.config(state='disabled')
    btn_ref_client.config(state='disabled')
    btn_bulk_project.config(state='disabled')
    btn_close_tasks.config(state='disabled')
    btn_create_projects.config(state='disabled')
    btn_report_client.config(state='disabled')
    btn_report_project.config(state='disabled')
    botoes = False

def enable_elements():
    global botoes
    combo_client.config(state='readonly')
    combo_project.config(state='readonly')
    btn_ref_client.config(state='normal')
    btn_bulk_project.config(state='normal')
    btn_close_tasks.config(state='normal')
    btn_create_projects.config(state='normal')
    btn_report_client.config(state='normal')
    btn_report_project.config(state='normal')
    botoes = True

# Get the absolute path to the assets
def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# Change the window size
def change_window_size():
    global wide
    if wide:
        window.geometry("520x600")
        btn_expand.config(image=btn_expand_img)
        wide = False
    else:
        window.geometry("1048x600")
        btn_expand.config(image=btn_expand_img_alt)
        wide = True

# Open the Excel file selection
def open_excel_selection():
    file_path = askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    entry_file.delete(0, "end")
    entry_file.insert(0, file_path)

# Get the current selected client
def get_client_info():
    selected_name = combo_client.get()
    if not selected_name:
        print("Select a client")
        return None

    for client_id, (name, projects_count) in client_list.items():
        if name == selected_name:
            return {client_id: projects_count}

    return None

# Get the current selected project
def get_project_info(lst=None):
    if lst is not None:
        project_info = {}
        for item in lst:
            for project_id, (name, tasks_count) in task_list.items():
                if name == item:
                    project_info[project_id] = tasks_count
        return project_info

    selected_name = combo_project.get()
    if not selected_name:
        print("Select a project")
        return

    for project_id, (name, tasks_count) in task_list.items():
        if name == selected_name:
            return {project_id: tasks_count}

    return None

# Refresh the selectable clients in the combobox
def refresh_client():
    global client
    global client_list

    client_list = start_process(2)
    client = [name for name, _ in client_list.values()]
    combo_client["values"] = client

# Refresh the selectable projects in the combobox
def refresh_project():
    global project
    global task_list

    client_info = get_client_info()
    if not client_info:
        return

    client_id, projects_count = list(client_info.items())[0]

    if not projects_count:
        print("There are no projects under the client with ID {}.".format(client_id))
        return

    task_list = start_process(3, client_id, projects_count)
    project = [name for name, _ in task_list.values()]
    combo_project["values"] = project

# Refresh project event for combobox selection, destroy the task list if it's already generated
def refresh_project_drop(event):
    global task_frame
    refresh_project()
    combo_project.set('')

    if task_frame:
        task_frame.unbind_all("<MouseWheel>")
        task_frame.destroy()

# Refresh task event for combobox
def refresh_task_drop(event):
    refresh_task()

# Refresh task function, create the task_frame inside the rect
def refresh_task(bulk=None):
    global tasks
    global task_list
    global task_frame

    if task_frame:
        task_frame.unbind_all("<MouseWheel>")
        task_frame.destroy()

    extra = get_project_info(bulk)
    task_list = start_process(4, extra)
    task_frame, tasks = open_popup(window, task_list)
    # Placing in the rect
    x1, y1, x2, y2 = 564, 173, 998, 487
    rect_width = x2 - x1
    rect_height = y2 - y1
    task_frame.place(x=x1, y=y1, width=rect_width, height=rect_height)
    refresh_project()

# Open popup to select more than one project
def bulk_project():
    popup = BulkPopup(window, project)
    window.wait_window(popup.popup_window)
    selected_options = popup.get_selected_options()
    if not selected_options:
        print("No projects selected.")
        return
    refresh_task(selected_options)

# Create new project inside the saved client and board in the headers file
def start_project_creation():
    file_path = entry_file.get()

    if file_path.endswith(".xlsx"):
        data = None

        def target():
            nonlocal data
            data = start_process(command=1, extra=file_path,
                                 window=window, button=btn_create_projects)

        thread = threading.Thread(target=target)
        thread.start()
        thread.join()

        log_project(2, data)

    else:
        print("File must be XLSX.")

# Deliver selected tasks, with the number written in their entries
def close_task():
    global tasks, task_frame
    task_list = tasks()
    try:
        start_process(5, task_list)
        log_task(1, task_list)
    except Exception as e:
        print("An error occurred while creating the projects:", str(e))
    task_frame.unbind_all("<MouseWheel>")
    task_frame.destroy()

# Ask start.py for the list under the selected client/project and generate the log
def report(command, button, bulk=None):
    button.config(state='disabled')
    if command == 1:
        main = get_project_info(bulk)
        if not main:
            return
        id, count = list(main.items())[0]
        if not count:
            print("There are no tasks under the project with ID {}.".format(id))
            return
        extra = start_process(4, extra=main)

        if not bulk:
            name = combo_project.get()

        try:
            generate_task_csv(extra, name)
        except Exception as e:
            print("An error occurred while writing to the CSV file:", str(e))

    elif command == 2:
        main = get_client_info()
        if not main:
            return
        id, count = list(main.items())[0]
        if not count:
            print("There are no projects under the client with ID {}.".format(id))
            return
        extra = start_process(3, extra=main, count=count)

        if not bulk:
            name = combo_client.get()

        try:
            generate_project_csv(extra, combo_client.get())
        except Exception as e:
            print("An error occurred while writing to the CSV file:", str(e))

    else:
        print("Selected does not exist or you don't have permissions.")
    button.config(state='normal')
    return

# Threading for report()
def start_report(command, button, bulk=None):
    thread = threading.Thread(target=report, args=(command, button, bulk))
    thread.start()

# WINDOW CREATION ########################################
# This file was generated by the Tkinter Designer by Parth Jadhav
# https://github.com/ParthJadhav/Tkinter-Designer

window = Tk()
window.iconbitmap("./assets/icon.ico")
window.title("RunRun Hub")
window.geometry("520x600")
window.configure(bg="#1A253B")
selected_name = StringVar(window)

# Images
btn_expand_img = PhotoImage(file=relative_to_assets("button_expand.png"))
btn_expand_img_alt = PhotoImage(
    file=relative_to_assets("button_expand_alt.png"))
btn_ref_img = PhotoImage(file=relative_to_assets("button_refresh.png"))
btn_report = PhotoImage(file=relative_to_assets("button_report.png"))
bnt_bulk_project_img = PhotoImage(file=relative_to_assets("button_bulk.png"))
banner_img = PhotoImage(file=relative_to_assets("banner.png"))
btn_create_projects_image = PhotoImage(
    file=relative_to_assets("button_start.png"))
btn_close_tasks_img = PhotoImage(
    file=relative_to_assets("button_close_tasks.png"))
entry_file_image = PhotoImage(file=relative_to_assets("entry_file.png"))
btn_get_file_image = PhotoImage(file=relative_to_assets("button_file.png"))

canvas = Canvas(
    window,
    bg="#5fad9e",
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

######################################## Intro Panel ########################################
# Place the banner
banner = canvas.create_image(
    257.0,
    123.0,
    image=banner_img
)

# Expand window button
btn_expand = tk.Button(
    image=btn_expand_img,
    borderwidth=0,
    highlightthickness=0,
    command=change_window_size,
    relief="flat"
)
btn_expand.place(x=500.0, y=0.0, width=20.0, height=600.0)

# Ping sensor. If runrun.it cannot be pinged, it will turn red and disable all buttons.
ping_sensor = canvas.create_oval(16, 19, 16 + 13, 19 + 13, fill='yellow')
thread_ms = threading.Thread(target=ping_runrun)
thread_ms.daemon = True
thread_ms.start()

######################################## First Panel ########################################
# Excel Area 
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

btn_get_file = Button(
    image=btn_get_file_image,
    borderwidth=0,
    highlightthickness=0,
    command=open_excel_selection,
    relief="flat"
)
btn_get_file.place(
    x=438.0,
    y=256.0,
    width=28.0,
    height=28.0
)

# Button to create project
btn_create_projects = Button(
    image=btn_create_projects_image,
    borderwidth=0,
    highlightthickness=0,
    command=start_project_creation,
    relief="flat"
)
btn_create_projects.place(
    x=145.0,
    y=310.0,
    width=225.0,
    height=61.0
)

# Log area
entry_log = Text(
    bd=0,
    bg="#daede9",
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

######################################## Second Panel ########################################
######################################## Client Area ########################################
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
    width=372.0,
    height=20.0
)

combo_client.bind("<<ComboboxSelected>>", refresh_project_drop)

btn_ref_client = Button(
    image=btn_ref_img,
    borderwidth=0,
    highlightthickness=0,
    command=refresh_client,
    relief="flat"
)
btn_ref_client.place(
    x=942.0,
    y=80.0,
    width=23.0,
    height=20.0
)

btn_report_client = Button(
    image=btn_report,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: start_report(1, btn_report_client),
    relief="flat"
)
btn_report_client.place(
    x=973.0,
    y=134.0,
    width=22.0,
    height=20.0
)

######################################## Project area ########################################
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
    values=project,
    state="readonly",
    justify="left",
    height=5,
    width=30,
)
combo_project.place(
    x=563.0,
    y=134.0,
    width=372.0,
    height=20.0
)

combo_project.bind("<<ComboboxSelected>>", refresh_task_drop)

btn_bulk_project = Button(
    image=bnt_bulk_project_img,
    borderwidth=0,
    highlightthickness=0,
    command=bulk_project,
    relief="flat"
)
btn_bulk_project.place(
    x=942.0,
    y=134.0,
    width=23.0,
    height=20.0
)

btn_report_project = Button(
    image=btn_report,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: start_report(2, btn_report_project),
    relief="flat"
)
btn_report_project.place(
    x=973.0,
    y=80.0,
    width=22.0,
    height=20.0
)

######################################## Task area ########################################
btn_close_tasks = Button(
    image=btn_close_tasks_img,
    borderwidth=0,
    highlightthickness=0,
    command=close_task,
    relief="flat"
)
btn_close_tasks.place(
    x=733.0,
    y=511.0,
    width=108.0,
    height=36.0
)

canvas.create_rectangle(563.0, 172.0, 998.0, 487.0, fill="#D9D9D9")

window.resizable(False, False)
redirect_stdout(entry_log)
window.mainloop()
