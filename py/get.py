import requests

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
        task_dict.update({task["id"]: (task["title"], task["state"], task["current_estimate_seconds"], task["time_worked"]) for task in tasks})
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