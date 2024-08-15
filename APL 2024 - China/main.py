import requests
import itertools
import time
import warnings
warnings.filterwarnings("ignore")
insample_url = "https://alphaverse.alpha-grep.com/api/v1/insample"
result_url = "https://alphaverse.alpha-grep.com/api/v1/result"
submission_url = "https://alphaverse.alpha-grep.com/api/v1/outsample"
token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyMzY4NjE3NSwianRpIjoiNzMyNGU5ZWEtMmFkYS00N2FjLTk5NWEtMGFjMWRhZjI3MGI5IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InRydW5nY2hpZW4xNzFAZ21haWwuY29tIiwibmJmIjoxNzIzNjg2MTc1LCJjc3JmIjoiMDAxZjkzZmQtMzBhZC00YzdkLWFlN2YtMzBmMTllYmY4MjM5IiwiZXhwIjoxNzIzNzcyNTc1fQ.H4zwHZLt2KeXxo20MrJ4MYjID20AGt2giQAxHL-guzE" # Bearer xyz...
def simulation_flow():
    headers = {"Authorization": token}
    def generate_payloads():
        '''
        Use this to intelligently generate alphas.
        Remember - There will be API limits. 
        Use the API wisely, do not abuse it.
        '''
        # Remember, functions should only be substituted with functions that match its signature
        f1_list = ["cs_rank", "rank"] 
        f2_list = ["ts_decay_linear", "ts_decay_exp_window"]
        d1_list = ["close", "open"]
        d2_list = ["low", "high"]
        d3_list = ["high", "low"]
        d4_list = ["close", "open"]
        c1_list = [10, 5]
        dataset_list = ["CHINA500", "CHINA2000", "CHINA1000"]
        region_list = ["china"]
        truncation_list = [0.015, 0.01]
        decay_list = [0, 1]
        pasteurize_list = [False, True]
        neutral_list = ["industry", "sector"]
        competition_list = ["APL_CHINA_2024"]
        payloads = []
        for (
            f1,
            f2,
            d1,
            d2,
            d3,
            d4,
            c1,
            dataset,
            region,
            truncation,
            decay,
            pasteurize,
            neutral,
            competition,
        ) in itertools.product(
            f1_list,
            f2_list,
            d1_list,
            d2_list,
            d3_list,
            d4_list,
            c1_list,
            dataset_list,
            region_list,
            truncation_list,
            decay_list,
            pasteurize_list,
            neutral_list,
            competition_list,
        ):
            payload = {
                "code": f"alpha =  -1*{f1}({f2}(({d1} - {d2}) - ({d3} - {d4}), {c1}))",
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
    payloads = [{
        'code': 'alpha =  -1*cs_rank(ts_decay_linear((close - low) - (high - close), 10))',
        'settings': {
            'dataset': 'CHINA1000',
            'region': 'china',
            'truncation': 0.015,
            'decay': 0,
            'pasteurize': True,
            'neutral': 'sector',
        },
        'competition': 'APL_CHINA_2024',
    }]
    print(f'{len(payloads)=}')
    insample_task_ids = []
    outsample_task_ids = []
    # Corresponds to insample flow in UI
    for payload in payloads[:10]:
        response = requests.post(
            insample_url, headers=headers, json=payload, verify=False
        )
        if response.status_code == 202:
            insample_task_ids.append(response.json()['taskId'])
            print(f"✅ payload = {payload}, task_id = {response.json()['taskId']}")
        else:
            response_text = response.text.replace("\n", "\\n")
            print(f"❌ payload = {payload}, response = {response.text}")
        time.sleep(1)
    print(f"{insample_task_ids=}")
    # Corresponds to results flow in UI
    while insample_task_ids:
        task_id = insample_task_ids.pop(0)
        response = requests.get(
            result_url + f"?task_id={task_id}", headers=headers, verify=False
        )
        if response.status_code == 200:
            # 200 means simulation has completed, we can submit it (if eligible)
            result = response.json()
            # This checks if robustness checks and correlation checks pass. Only submit alphas if this is True
            is_eligible_for_submission = result['is_eligible_for_submission']
            # These are optional custom conditions created as per your alpha research. Added 2 conditions just for demo purposes.
            # You should add conditions as per your research.
            custom_condition_1 = result['stats']['SHRP']['All'] > 1.5
            custom_condition_2 = result['stats']['BPS']['All'] > 4
            if is_eligible_for_submission and custom_condition_1 and custom_condition_2:
                outsample_task_ids.append(task_id)
                print(f'✅ {task_id=} met submission criteria')
            else:
                print(f'❌ {task_id=} did not meet submission criteria')
        elif response.status_code == 202:
            # The insample simulation is still in progress, we will try again later
            print(f'🏃‍♂️ simulation still in progress for {task_id}, will check again')
            insample_task_ids.append(task_id)
        else:
            # Some error when fetching results for this task id
            response_text = response.text.replace("\n", "\\n")
            print(f'❌ Task Id = {task_id}, message = "{response_text}"')
        time.sleep(1)
    print(f"{outsample_task_ids=}")
    # Corresponds to outsample flow in UI
    for task_id in outsample_task_ids:
        submission_response = requests.post(
            submission_url, headers=headers, json={'taskId': task_id}, verify=False
        )
        if submission_response.status_code == 202:
            print(f'✅ Task Id = {task_id}, message = "Successfully submitted"')
        else:
            # some error with submission
            print(
                f'❌ Task Id = {task_id}, message = "{submission_response.json()["message"]}"'
            )
        time.sleep(1)
if __name__ == "__main__":
    simulation_flow()