import tkinter as tk
from cryptography.fernet import Fernet
from py.create_project import create_project
from py.change_status import *

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
        create_project(extra, headers, secret_info)
        print("End of process.")
    elif (command == 2):
        data = get_client(headers)
    elif (command == 3):
        data = get_project(headers, extra, count)
    elif (command == 4):
        data = get_tasks(headers, extra, count)
    elif (command == 5):
        for task_id in extra:
            max_hours(headers, task_id)
        print("End of process.")

    if button:
        window.after(0, lambda: button.config(state=tk.NORMAL))

    return data

def read_file(filename):
    try:
        with open(filename, "rb") as file:
            return file.read()
    except FileNotFoundError:
        print(f"File '{filename}' not found. Try generating again.")
        return b''

def get_keys():
    ciphertext = read_file("😨")
    encryption_key = read_file("./assets/data")

    cipher = Fernet(encryption_key)
    plaintext = cipher.decrypt(ciphertext).decode()

    values = [{"tag": tag, "value": value} for line in plaintext.split("\n") if line for tag, value in [line.split("=")]]

    return values