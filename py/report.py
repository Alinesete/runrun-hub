from py.get import *
from py.start import start_process
import csv
from datetime import datetime
from datetime import date

def time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"'{hours:02d}:{minutes:02d}"

def generate(command, list, fileName):
    headers = start_process(6)
    if command == 1:

        with open(f"{fileName}.csv", "w", newline="") as arquivo_csv:
            writer = csv.writer(arquivo_csv)
            writer.writerow(["Client","Project","Task","Overdue","Status","Progress","Time Worked", "Time Pending","Responsible", "Obs"])
            
            for title, (num1, num2, state, ids) in list.items():
                for id in ids:
                    tasks_url = f"https://runrun.it/api/v1.0/tasks/{id}"
                    tasks = get_list(tasks_url, headers)
                    
                    if not tasks:
                        print("You do not have permission to access {}.".format(id))
                        continue
                    
                    client_name = tasks['client_name']
                    project_name = tasks['project_name']
                    title = tasks['title']
                    overdue = tasks['desired_date']
                    if overdue is not None:
                        overdue = datetime.fromisoformat(overdue)
                        overdue = overdue.strftime("%d/%m/%Y")
                    status = tasks['task_status_name']
                    time_worked = time(tasks['time_worked']) if tasks['time_worked'] is not None else "00:00"
                    time_pending = time(tasks['time_pending']) if tasks['time_pending'] is not None else "00:00"
                    time_progress = "{:.0%}".format(tasks['time_progress'] / 100) if tasks['time_progress'] is not None else "0%"
                    responsible = tasks['responsible_name']
                    obs = tasks['tag_list']
                    
                    writer.writerow([client_name, project_name, title, overdue, status, time_progress, time_worked, time_pending, responsible, obs])

    if command == 2:
        with open(f"{fileName}.csv", "w", newline="") as arquivo_csv:
            writer = csv.writer(arquivo_csv)

            writer.writerow(["Client", "Title", "Overdue", "Tasks", "Progress", "Time Spent", "Time Pending", "Cost Progress", "Cost Spent", "Cost Pending"])

            for id, (title, count) in list.items():
                project_url = f"https://runrun.it/api/v1.0/projects/{id}"
                projects = get_list(project_url, headers)

                if not projects:
                    print("You do not have permission to access {}.".format(id))
                    pass
                
                client_name = projects['client_name']
                project_title = projects['name']
                overdue = projects['desired_date']
                if overdue is not None:
                        overdue = datetime.fromisoformat(overdue)
                        overdue = overdue.strftime("%d/%m/%Y")
                tasks_count = projects['tasks_count']
                time_progress = "{:.0%}".format(float(projects['time_progress']) / 100) if projects['time_progress'] is not None else "0%"
                time_worked = time(projects['time_worked']) if projects['time_worked'] is not None else "00:00"
                time_pending = time(projects['time_pending']) if projects['time_pending'] is not None else "00:00"
                cost_progress = "{:.0%}".format(projects['cost_progress'] / 100) if projects['cost_progress'] is not None else "0%"
                cost_worked = "R$ {:,.2f}".format(projects['cost_worked']).replace(',', '#').replace('.', ',').replace('#', '.') if projects['cost_worked'] is not None else "R$ 0,00"
                cost_pending = "R$ {:.2f}".format(projects['cost_pending']).replace(',', '#').replace('.', ',').replace('#', '.') if projects['cost_pending'] is not None else "R$ 0,00"

                writer.writerow([client_name, project_title, overdue, tasks_count, time_progress, time_worked, time_pending, cost_progress, cost_worked, cost_pending])

    print(f"Data saved in {fileName}.csv")

import os

def log(command, data):
    today = date.today().strftime("%d-%m-%Y")
    
    log_file_path = "tasklog.txt" if command == 1 else "newlog.txt"
    
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as log_file:
            log_file.write("Date, Title, Hours Added, IDs\n")
    
    with open(log_file_path, "a") as log_file:
        if command == 1:
            for title, (hours_added, ids) in data.items():
                ids_str = ', '.join(str(id) for id in ids)
                log_file.write(f"{today}, {title}, {hours_added}, {ids_str}\n")
        elif command == 2:
            for project, (name, client_id) in data.items():
                log_file.write(f"{today}, {project}, {name}, {client_id}\n")

    print("Data appended to log.")