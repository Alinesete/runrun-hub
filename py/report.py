import csv
from datetime import datetime
import getpass
import os
from py.get import get_list
from py.start import start_process

TIME_FORMAT = "%d/%m/%Y"
LOG_FILE_PATHS = {
    1: "tasklog.csv",
    2: "newlog.csv"
}

# Get seconds, returns hh:mm
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"'{hours:02d}:{minutes:02d}"

# Generate task report (From project)
def generate_task_csv(list, file_name):
    headers = start_process(6)

    # Preparing the file
    with open(f"{file_name}.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Client", "Project", "Task", "Overdue", "Status", "Progress",
                         "Time Worked", "Time Pending", "Responsible", "Obs"])

        # For each title in the list
        for title, (num1, num2, state, ids) in list.items():
            # For each id will request the info from the api
            for task_id in ids:
                tasks_url = f"https://runrun.it/api/v1.0/tasks/{task_id}"
                tasks = get_list(tasks_url, headers)

                if not tasks:
                    print("You do not have permission to access {}.".format(task_id))
                    continue

                client_name = tasks['client_name']
                project_name = tasks['project_name']
                task_title = tasks['title']
                overdue = tasks['desired_date']

                if overdue is not None:
                    overdue = datetime.fromisoformat(overdue)
                    overdue = overdue.strftime(TIME_FORMAT)

                status = tasks['task_status_name']
                time_worked = format_time(tasks['time_worked']) if tasks['time_worked'] is not None else "00:00"
                time_pending = format_time(tasks['time_pending']) if tasks['time_pending'] is not None else "00:00"
                time_progress = "{:.0%}".format(tasks['time_progress'] / 100) if tasks['time_progress'] is not None else "0%"
                responsible = tasks['responsible_name']
                obs = tasks['tag_list']

                writer.writerow([client_name, project_name, task_title, overdue, status,time_progress, time_worked, time_pending, responsible, obs])

    print(f"Data saved in {file_name}.csv")

# Function to generate project report (From client)
def generate_project_csv(list, file_name):
    headers = start_process(6)

    # Preparing the file
    with open(f"{file_name}.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Client", "Title", "Overdue", "Tasks", "Progress","Time Spent", "Time Pending", "Cost Progress", "Cost Spent", "Cost Pending"])

        # For each project id
        for project_id, (title, count) in list.items():
            project_url = f"https://runrun.it/api/v1.0/projects/{project_id}"
            projects = get_list(project_url, headers)

            if not projects:
                print("You do not have permission to access {}.".format(project_id))
                continue

            client_name = projects['client_name']
            project_title = projects['name']
            overdue = projects['desired_date']

            if overdue is not None:
                overdue = datetime.fromisoformat(overdue)
                overdue = overdue.strftime(TIME_FORMAT)

            tasks_count = projects['tasks_count']
            time_progress = "{:.0%}".format(float(projects['time_progress']) / 100) if projects['time_progress'] is not None else "0%"
            time_worked = format_time(projects['time_worked']) if projects['time_worked'] is not None else "00:00"
            time_pending = format_time(projects['time_pending']) if projects['time_pending'] is not None else "00:00"
            cost_progress = "{:.0%}".format(projects['cost_progress'] / 100) if projects['cost_progress'] is not None else "0%"
            cost_worked = "R$ {:,.2f}".format(projects['cost_worked']).replace(',', '#').replace('.', ',').replace('#', '.') if projects['cost_worked'] is not None else "R$ 0,00"
            cost_pending = "R$ {:.2f}".format(projects['cost_pending']).replace(',', '#').replace('.', ',').replace('#', '.') if projects['cost_pending'] is not None else "R$ 0,00"

            writer.writerow([client_name, project_title, overdue, tasks_count, time_progress,
                             time_worked, time_pending, cost_progress, cost_worked, cost_pending])

    print(f"Data saved in {file_name}.csv")

# Append the delivered tasks to the log file
def log_task(command, data):
    now = datetime.now()
    today = now.strftime("%d-%m-%Y %H:%M:%S")
    username = getpass.getuser()

    log_file_path = LOG_FILE_PATHS[command]

    fieldnames = ["Date", "Username", "Title", "Hours Added", "IDs"]

    # Will create the file if doesn't exist
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w", newline="") as log_file:
            writer = csv.DictWriter(log_file, fieldnames=fieldnames)
            writer.writeheader()

    with open(log_file_path, "a", newline="") as log_file:
        writer = csv.DictWriter(log_file, fieldnames=fieldnames)

        for title, (hours_added, ids) in data.items():
            ids_str = ', '.join(str(task_id) for task_id in ids)
            writer.writerow({
                "Date": today,
                "Username": username,
                "Title": title,
                "Hours Added": (hours_added / 3600),
                "IDs": ids_str
            })

    print("Data registered. You can see the log in {}".format(log_file_path))

# Append the created projects to the log file
def log_project(command, data):
    now = datetime.now()
    today = now.strftime("%d-%m-%Y %H:%M:%S")
    username = getpass.getuser()

    log_file_path = LOG_FILE_PATHS[command]

    fieldnames = ["Date", "Username", "Title", "Name", "ID"]

    # Will create the file if doesn't exist
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w", newline="") as log_file:
            writer = csv.DictWriter(log_file, fieldnames=fieldnames)
            writer.writeheader()

    with open(log_file_path, "a", newline="") as log_file:
        writer = csv.DictWriter(log_file, fieldnames=fieldnames)

        for project_id, (name, client_id) in data.items():
            writer.writerow({
                "Date": today,
                "Username": username,
                "Title": project_id,
                "Name": name,
                "ID": client_id
            })

    print("Data registered. You can see the log in {}".format(log_file_path))
