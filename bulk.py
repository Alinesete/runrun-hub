import tkinter as tk
from tkinter import ttk

class bulk_popup:
    def __init__(self, parent, options):
        self.parent = parent
        self.options = options
        self.popup_window = tk.Toplevel(parent)
        self.selected_options = []

        self.create_widgets()

    def create_widgets(self):
        self.popup_window.geometry("400x300")

        frame = ttk.Frame(self.popup_window)
        frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)

        for item in self.options:
            selected = tk.BooleanVar(value=False)
            option_button = ttk.Checkbutton(inner_frame, text=item, variable=selected,
                                            onvalue=True, offvalue=False,
                                            command=lambda item=item, selected=selected: self.toggle_option(item, selected))
            option_button.pack(anchor='w')

            self.selected_options.append((item, selected))

        process_button = ttk.Button(inner_frame, text="Selecionar", command=self.get_selected_options)
        process_button.pack()
        inner_frame.bind("<Configure>", lambda event: self.update_scroll_region(canvas, inner_frame))
        canvas.bind("<MouseWheel>", self.on_mousewheel)

    def update_scroll_region(self, canvas, inner_frame):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def toggle_option(self, option, selected):
        pass

    def get_selected_options(self):
        selected_options = []
        for item, selected in self.selected_options:
            if selected.get():
                selected_options.append(item)
        self.popup_window.destroy()
        return selected_options

    def on_mousewheel(self, event):
        canvas = event.widget
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
