import requests
from datetime import date
import math

def att_task(headers, task_list):
    manual_work_url = "https://runrun.it/api/v1.0/manual_work_periods"
    current_date = date.today().isoformat()

    for title, (seconds, ids) in task_list.items():
        seconds = math.ceil(float(seconds))
        seconds = int(seconds)
        for task_id in ids:
            response_2 = requests.post(f"https://runrun.it/api/v1.0/tasks/{task_id}/deliver", headers=headers)

            if response_2.status_code == 200:
                print("Task {} delivered.".format(task_id))

                response_1 = requests.get(f"https://runrun.it/api/v1.0/tasks/{task_id}", headers=headers)
                data_1 = response_1.json()

                data = {
                    "manual_work_period": {
                        "task_id": task_id,
                        "seconds": seconds,
                        "date_to_apply": current_date
                    }
                }

                response = requests.post(manual_work_url, json=data, headers=headers)

                if response.status_code == 201:
                    print("{} seconds added to {}.".format(seconds, task_id))
                else:
                    print("Failed to add manual work period to task {}. Status code: {}".format(task_id, response.status_code))
            elif response_2.status_code == 422:
                print("Warning: Failed to deliver task {}. Task may already be delivered.".format(task_id))
            else:
                print("Failed to deliver task {}. Status code: {}".format(task_id, response_2.status_code))
            
