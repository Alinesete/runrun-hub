import requests
from datetime import date

def get_client(headers):
    client_url = "https://runrun.it/api/v1.0/clients"
    clients = get_list(client_url, headers)
    client_dict = {client["id"]: (client["name"], client["projects_count"]) for client in clients}
    return client_dict

def get_project(headers, client_id, count):
    project_url = "https://runrun.it/api/v1.0/projects"
    page = calc_page(count)
    project_dict = {}

    for page_num in range(1, page + 1):
        params = {"client_id": client_id, "page": page_num}
        projects = get_list(project_url, headers, params)
        project_dict.update({project["id"]: (project["name"], project["tasks_count"]) for project in projects})
    return project_dict

def get_tasks(headers, project_id, count):
    task_url = "https://runrun.it/api/v1.0/tasks"
    page = calc_page(count)
    task_dict = {}

    for page_num in range(1, page + 1):
        params = {"project_id": project_id, "page": page_num, "bypass_status_default" : True, "include_not_assigned" : True}
        tasks = get_list(task_url, headers, params)
        task_dict.update({task["id"]: (task["title"], task["state"]) for task in tasks})
    return task_dict

def calc_page(count):
    page = 1 + (count - 1) // 101
    return page

def get_list(url, headers, params=None):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error: {}".format(response.status_code))
        return

def max_hours(headers, task_id):
    manual_work_url = "https://runrun.it/api/v1.0/manual_work_periods"
    current_date = date.today().isoformat()

    response_1 = requests.get(f"https://runrun.it/api/v1.0/tasks/{task_id}", headers=headers)
    data_1 = response_1.json()

    data = {
        "manual_work_period": {
            "task_id": task_id,
            "seconds": data_1["current_estimate_seconds"],
            "date_to_apply": current_date
        }
    }

    response = requests.post(manual_work_url, json=data, headers=headers)

    if response.status_code == 201:
        print("{} seconds added to {}.".format(data_1["current_estimate_seconds"], task_id))
    else:
        print("Failed to add manual work period to task {}. Status code: {}".format(task_id,response.status_code))

    response_2 = requests.post(f"https://runrun.it/api/v1.0/tasks/{task_id}/deliver", headers=headers)

    if response_2.status_code == 200:
        print("Task {} delivered.".format(task_id))
    elif response_2.status_code == 422:
        print("Warning: {}".format(task_id))
    else:
        print("Failed to deliver task {}. Status code: {}".format(task_id,response_2.status_code))
    
