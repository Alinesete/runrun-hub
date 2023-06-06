import requests

CLIENT_URL = "https://runrun.it/api/v1.0/clients"
PROJECT_URL = "https://runrun.it/api/v1.0/projects"
TASK_URL = "https://runrun.it/api/v1.0/tasks"

def get_client_dict(headers):
    clients = get_list(CLIENT_URL, headers)
    client_dict = {client["id"]: (client["name"], client["projects_count"]) for client in clients}
    return client_dict

def get_project_dict(headers, client_id, count):
    page = calc_page(count)
    project_dict = {}

    for page_num in range(1, page + 1):
        params = {"client_id": client_id, "page": page_num}
        projects = get_list(PROJECT_URL, headers, params)
        project_dict.update({project["id"]: (project["name"], project["tasks_count"]) for project in projects})
    return project_dict

def get_tasks_dict(headers, project_id, count):
    page = calc_page(count)
    task_dict = {}

    for page_num in range(1, page + 1):
        params = {"project_id": project_id, "page": page_num, "bypass_status_default" : True, "include_not_assigned" : True}
        tasks = get_list(TASK_URL, headers, params)
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
        raise Exception("Error: {}".format(response.status_code))
