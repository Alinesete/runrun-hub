import requests
import json
import pandas as pd

project_url = "https://runrun.it/api/v1.0/projects/"

def create_project(excel_file_path, headers, secret_info):

    try:
        excel_file = pd.read_excel(excel_file_path)
    except FileNotFoundError:
        print("The file was not found.")
        return
    except Exception as e: 
        print("There has been an error reading the file: {}".format(str(e)))
        return

    if "Name" not in excel_file.columns:
        print('Excel file must have a "Name" column.')
        return
    
    tasks_template = get_template(headers)

    if not tasks_template:
        return

    excel_file.dropna(subset=["Name"], inplace=True)

    for row in excel_file.iterrows():
        project_name = row[1]["Name"]
        project_data = {
            "project": {
                "name": project_name,
                "client_id": secret_info["client_id"]
            }
        }
        project_response = requests.post(project_url, headers=headers, data=json.dumps(project_data))

        if project_response.status_code == 201:
            project_id = project_response.json()["id"]
            print("Project '{}' created sucessfully. ID: {}".format(project_name, project_id))
            set_board(headers, project_id, secret_info["board_id"])
            clone_task(headers, project_id, secret_info["board_id"], tasks_template)

        elif project_response.status_code == 422:
            print("Project '{}' cannot be created, already exists.".format(project_name))

        else:
            print("Error creating project '{}': {}".format(project_name, project_response.status_code))
            return
            
    print("\n\n")

def set_board(headers, project_id, board_id):
    project_update_url = f"https://runrun.it/api/v1.0/projects/{project_id}"
    project_update_data = {
        "project": {
            "board_id": board_id
        }
    }

    project_update_response = requests.patch(project_update_url, headers=headers, data=json.dumps(project_update_data))

    if project_update_response.status_code == 204:
        print("Board {} linked in {}.".format(board_id, project_id))
    else:
        print("Error linking board for {}: {}".format(project_id,project_update_response.status_code))

def get_template(headers):
    template_id = 000000
    url = f"https://runrun.it/api/v1.0/project_templates/{template_id}/task_templates"
    response = requests.get(url, headers=headers)

    if response.status_code == 404:
        print("Template not found.")
    elif response.status_code == 422:
        print("Error! User has no permission to see template: {}.".format(response.status_code))
        return
    elif response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error: {}".format(response.status_code))
        return


def clone_task(headers, project_id, board_id, tasks_template):

    create_tasks_url = "https://runrun.it/api/v1.0/tasks"

    for task_template in tasks_template:
        template_task_id = task_template["id"]
        tasktype_id = task_template["type_id"]

        clone_data = {
            "task": {
                "title": task_template["title"],
                "on_going": False,
                "project_id": project_id,
                "desired_date": None,
                "type_id": tasktype_id,
                "board_id": board_id,
                "queue_position": task_template["queue_position"],
                "project_template_id": task_template["project_template_id"],
                "tag_list": task_template["tag_list"],
                "tags_data": task_template["tags_data"],
                "team_name": task_template["team_name"],
                "type_name": task_template["type_name"],
                "subtasks_data": task_template["subtasks_data"],
                "assignments": task_template["assignments"],
            }
        }

        create_response = requests.post(create_tasks_url, headers=headers, data=json.dumps(clone_data))

        if create_response.status_code == 201:
            print("Task created: {}".format(task_template["title"]))
        else:
            print("Error creating task: {} {}".format(template_task_id, create_response.content))
            return
        
    return
