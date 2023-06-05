from tkinter import Canvas, Scrollbar, Frame, Checkbutton, IntVar, DISABLED, NORMAL, Entry, Label

def print_selected(task_name, task_entries):
    entry_progress, task_worked, task_total, _, checkbox_var = task_entries[task_name]
    entry_progress.delete(0, "end")
    
    if checkbox_var.get() == 0:
        entry_progress.insert("end", "{:.1f}".format(task_total / 3600))
    else:
        entry_progress.insert("end", "{:.1f}".format(task_worked / 3600))

def get_selected_tasks(task_entries):
    selected_task_dict = {}
    for task_name, (entry_progress, task_worked, _, task_ids, checkbox_var) in task_entries.items():
        task_worked = entry_progress.get()
        try:
            task_worked = float(task_worked)
        except ValueError:
            task_worked = 0.0
        if checkbox_var.get() != 0:
            selected_task_dict[task_name] = (task_worked * 3600, task_ids)
    return selected_task_dict

def open_popup(root, task_list):
    frame = Frame(root)
    frame.pack(fill="both", expand=True)

    canvas = Canvas(frame)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    inner_frame = Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    task_entries = {}

    for task_name, (task_total, task_worked, task_state, task_ids) in task_list.items():
        checkbox_state = DISABLED if task_state == "closed" else NORMAL

        task_frame = Frame(inner_frame)
        task_frame.pack(anchor="w", fill="x")

        checkbox_var = IntVar(value=0)

        checkbox = Checkbutton(task_frame, variable=checkbox_var, state=checkbox_state, onvalue=1, offvalue=0)
        checkbox.pack(side="left")

        checkbox.bind("<Button-1>", lambda event, task_name=task_name: print_selected(task_name, task_entries))

        label_name = Label(task_frame, text=task_name)
        label_name.pack(side="top", anchor="w")

        entry_frame = Frame(task_frame)
        entry_frame.pack(side="left", padx=(0, 5))

        entry_progress = Entry(entry_frame)
        entry_progress.insert("end", "{:.1f}".format(task_worked / 3600))
        entry_progress.config(width=4)
        entry_progress.pack(side="left")

        label_total = Label(entry_frame, text=f"/ {task_total / 3600}")
        label_total.pack(side="left")

        task_frame.pack()

        task_entries[task_name] = (entry_progress, task_worked, task_total, task_ids, checkbox_var)

    def update_canvas_size(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    inner_frame.bind("<Configure>", update_canvas_size)

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    return frame, lambda: get_selected_tasks(task_entries)
