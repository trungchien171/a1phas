import requests
import itertools
import time
import warnings
warnings.filterwarnings("ignore")

# URLs and Authorization token
insample_url = "https://alphaverse.alpha-grep.com/api/v1/insample"
result_url = "https://alphaverse.alpha-grep.com/api/v1/result"
submission_url = "https://alphaverse.alpha-grep.com/api/v1/outsample"
token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyNDk0NzQ4MCwianRpIjoiZmI4MzdlODItZjE1Yy00N2Y2LWI1MDUtMDI4ZjMyMzNjYjk3IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InRydW5nY2hpZW4xNzFAZ21haWwuY29tIiwibmJmIjoxNzI0OTQ3NDgwLCJjc3JmIjoiNDBhZDgzNjctMGY2ZS00Y2I4LWI5OTktZDYyODQwNzQ0YjU4IiwiZXhwIjoxNzI1MDMzODgwfQ.5AN92mlHg6blYxEbBgq7yS6u0fxQZ94SOg9yaY6isuE"

def simulation_flow():
    headers = {"Authorization": token}
        
    def generate_payloads():
        t1 = [1,2, 3, 4, 5, 6, 7, 8, 9, 10]
        t2 = [1,2, 3, 4, 5, 6, 7, 8, 9, 10]
        f1 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        # t3 = [1,2, 3, 4, 5, 6, 7, 8, 9, 10]
        # t4 = [1,2, 3, 4, 5, 6, 7, 8, 9, 10]
        # t5 = [1,2, 3, 4, 5, 6, 7, 8, 9, 10]
        # t6 = [1,2, 3, 4, 5, 6, 7, 8, 9, 10]
        dataset_list = ["CHINA5000"]
        region_list = ["china"]
        truncation_list = [0.015]
        decay_list = [3]
        pasteurize_list = [False]
        neutral_list = ["industry"]
        competition_list = ["APL_CHINA_2024"]
        
        payloads = []
        for (
            t1,
            t2,
            f1,
            # t3,
            # t4,
            # t5,
            # t6,
            dataset,
            region,
            truncation,
            decay,
            pasteurize,
            neutral,
            competition,
        ) in itertools.product(
            t1,
            t2,
            f1,
            # t3,
            # t4,
            # t5,
            # t6,
            dataset_list,
            region_list,
            truncation_list,
            decay_list,
            pasteurize_list,
            neutral_list,
            competition_list,
        ):
            payload = {
                "code": f'''alpha = -cs_zscore(
            ts_mean(
                log(risk_BETA * risk_LIQUIDTY) 
                - ts_decay_exp_window(risk_SIZE, window={t1}, factor={f1})
            , window={t2})
        )
''',
                "settings": {
                    "dataset": dataset,
                    "region": region,
                    "truncation": truncation,
                    "decay": decay,
                    "pasteurize": pasteurize,

                    "neutral": neutral,
                },
                "competition": competition,
            }
            payloads.append(payload)
        return payloads

    
    payloads = generate_payloads()
    print(f'{len(payloads)=}')
    insample_task_ids = []
    outsample_task_ids = []
    
    # Submit all generated payloads for insample simulation
    for payload in payloads[:61]:
        response = requests.post(
            insample_url, headers=headers, json=payload, verify=False
        )
        if response.status_code == 202:
            insample_task_ids.append(response.json()['taskId'])
            print(f"✅ payload = {payload}, task_id = {response.json()['taskId']}")
        else:
            response_text = response.text.replace("\n", "\\n")
            print(f"❌ payload = {payload}, response = {response.text}")
        time.sleep(1)  # To avoid hitting API limits
    
    print(f"{insample_task_ids=}")
    
    # Check the results of the insample simulations and collect eligible task IDs
    while insample_task_ids:
        task_id = insample_task_ids.pop(0)
        response = requests.get(
            result_url + f"?task_id={task_id}", headers=headers, verify=False
        )
        if response.status_code == 200:
            result = response.json()
            is_eligible_for_submission = result['is_eligible_for_submission']
            custom_condition_1 = result['stats']['SHRP']['All'] > 1.5
            custom_condition_2 = result['stats']['BPS']['All'] > 4
            if is_eligible_for_submission and custom_condition_1 and custom_condition_2:
                outsample_task_ids.append(task_id)
                print(f'✅ {task_id=} met submission criteria')
            else:
                print(f'❌ {task_id=} did not meet submission criteria')
        elif response.status_code == 202:
            print(f'🏃‍♂️ simulation still in progress for {task_id}, will check again')
            insample_task_ids.append(task_id)
        else:
            response_text = response.text.replace("\n", "\\n")
            print(f'❌ Task Id = {task_id}, message = "{response_text}"')
        time.sleep(1)  # To avoid hitting API limits
    
    print(f"{outsample_task_ids=}")
    
    # Submit eligible task IDs for outsample evaluation
    for task_id in outsample_task_ids:
        submission_response = requests.post(
            submission_url, headers=headers, json={'taskId': task_id}, verify=False
        )
        if submission_response.status_code == 202:
            print(f'✅ Task Id = {task_id}, message = "Successfully submitted"')
        else:
            print(f'❌ Task Id = {task_id}, message = "{submission_response.json()["message"]}"')
        time.sleep(1)  # To avoid hitting API limits

if __name__ == "__main__":
    simulation_flow()


