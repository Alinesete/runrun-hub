from tkinter import Toplevel, Canvas, Scrollbar, Frame, Checkbutton, IntVar, DISABLED, NORMAL, Button
from py.start_process import start_process
import threading

selected_tasks = []

def print_selected(task_id, task_name):
    if task_id in selected_tasks:
        selected_tasks.remove(task_id)
    else:
        selected_tasks.append(task_id)

def open_popup(root, task_list, button):
    popup = Toplevel(root)
    popup.title("Popup")

    frame = Frame(popup)
    frame.pack(fill="both", expand=True)

    canvas = Canvas(frame)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    inner_frame = Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    for task_id, task_data in task_list.items():
        task_name, task_state = task_data
        checkbox_state = DISABLED if task_state == "closed" else NORMAL
        checkbox_var = IntVar()
        checkbox = Checkbutton(inner_frame, text=task_name, variable=checkbox_var, state=checkbox_state, onvalue=1, offvalue=0)
        checkbox.pack(anchor="w")
        checkbox.config(command=lambda task_id=task_id, task_name=task_name: print_selected(task_id, task_name))

    def update_canvas_size(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    inner_frame.bind("<Configure>", update_canvas_size)

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    def start_selected():
        selected_ids = [task_id for task_id in selected_tasks]
        thread = threading.Thread(target=start_process, kwargs={"command": 5, "extra": selected_ids, "window": root, "button": button})
        thread.start()
        popup.destroy()

    show_button = Button(popup, text="Mark as completed", command=start_selected)
    show_button.pack(pady=10)
