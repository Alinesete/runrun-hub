import os
import tkinter as tk
from cryptography.fernet import Fernet
from py.create import create_project
from py.get import get_client_dict, get_project_dict, get_tasks_dict
from py.deliver import deliver_task

def start_process(command, extra=None, count=None, window=None, button=None):

    if button:
        button.config(state=tk.DISABLED)

    data = None
    values = get_keys()

    if not values:
        return

    secret_info = {}
    for item in values:
        tag = item["tag"]
        value = item["value"]
        secret_info[tag] = value

    headers = {
        "App-Key": secret_info["App-Token"],
        "User-Token": secret_info["User-Token"],
        "Content-Type": "application/json",
    }

    if (command == 1):
        data = create_project(extra, headers, secret_info)
        print("End of process.")
    elif (command == 2):
        data = get_client_dict(headers)
    elif (command == 3):
        data = get_project_dict(headers, extra, count)

    elif command == 4:
        tasks = {}
        title_tasks = {}

        for id, count in extra.items():
            tasks[id] = get_tasks_dict(headers, id, count)
            for task_id, (title, state, current_estimate_seconds, time_worked) in tasks[id].items():
                if title in title_tasks:
                    title_tasks[title][3].append((task_id, id))
                else:
                    title_tasks[title] = (current_estimate_seconds, time_worked, state, [(task_id, id)])

        common_title_tasks = {}
        for title, (estimate, time_worked, state, task_ids) in title_tasks.items():
            if len(task_ids) == len(extra):
                unique_project_ids = set([project_id for _, project_id in task_ids])
                if len(unique_project_ids) > 1:
                    time_worked = 0
                    state = ""
                common_title_tasks[title] = (estimate, time_worked, state, [task_id for task_id, _ in task_ids])


        return common_title_tasks

    elif (command == 5):
        deliver_task(headers, extra)
        id_list = [str(id) for _, (_, ids) in extra.items() for id in ids]
        id_string = ', '.join(id_list)
        print("IDs changed:", id_string)

    elif (command == 6):
        return headers

    if button:
        window.after(0, lambda: button.config(state=tk.NORMAL))

    if data:
        return data

def read_file(filename):
    try:
        with open(filename, "rb") as file:
            return file.read()
    except FileNotFoundError:
        print(f"File '{filename}' not found. Try generating again.")
        return b''

# Read the headers
def get_keys():
    cache_folder = os.path.expanduser("~/runhub")

    cache_file = os.path.join(cache_folder, "encrypted_data")
    with open(cache_file, "rb") as file:
        ciphertext = file.read()

    key_file = os.path.join(cache_folder, "encryption_key")
    with open(key_file, "rb") as file:
        encryption_key = file.read()

    cipher = Fernet(encryption_key)
    plaintext = cipher.decrypt(ciphertext).decode()

    values = [{"tag": tag, "value": value} for line in plaintext.split("\n") if line for tag, value in [line.split("=")]]

    return values