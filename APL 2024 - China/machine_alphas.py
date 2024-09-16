import requests
import itertools
import time
import warnings
warnings.filterwarnings("ignore")

# URLs and Authorization token
insample_url = "https://alphaverse.alpha-grep.com/api/v1/insample"
result_url = "https://alphaverse.alpha-grep.com/api/v1/result"
submission_url = "https://alphaverse.alpha-grep.com/api/v1/outsample"
token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyNjQxNjk0OCwianRpIjoiZWQwN2M2ZmUtZmZhOC00Nzk4LWEwODAtMzIxMjg4NWE2YzgwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InRydW5nY2hpZW4xNzFAZ21haWwuY29tIiwibmJmIjoxNzI2NDE2OTQ4LCJjc3JmIjoiZTlhZjFmZDItZDgxOC00YmU3LTk2ODMtMDVmYWY5MWZjOTI4IiwiZXhwIjoxNzI2NTAzMzQ4fQ.NvkLYaRohC3shP5wtT2nEyTuDPfB6kAhUz35IZVuyJ0"

def simulation_flow():
    headers = {"Authorization": token}
        
    def generate_payloads():
        t1 = [10,11,12,13,14,15]
        t2 = [10,11,12,13,14,15]
        # t3 = [5,6,7,8,9]
        # t4 = [5,6,7,8,9]
        # f1 = [0.4,0.5,0.6,0.7,0.8]
        dataset_list = ["CHINA1000"]
        region_list = ["china"]
        truncation_list = [0.015]   
        decay_list = [4]
        pasteurize_list = [False]
        neutral_list = ["industry"]
        competition_list = ["APL_CHINA_2024"]
        
        payloads = []
        for (
            t1,
            t2,
            # t3,
            # t4,
            # f1,
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
            # t3,
            # t4,
            # f1,
            dataset_list,
            region_list,
            truncation_list,
            decay_list,
            pasteurize_list,
            neutral_list,
            competition_list,
        ):
            payload = {
                "code": f'''alpha = -ts_max(close, {t1}) * ts_corr(volume, vwap, {t2})''',
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
    total_batches = len(payloads) // 30
    insample_task_ids = []
    outsample_task_ids = []

    for batch_index in range(total_batches + 1):
        current_batch = payloads[batch_index * 30:(batch_index + 1) * 30]
        if not current_batch:
            break

        for payload in current_batch:
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
        
        print(f"{len(insample_task_ids)=}")

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
            time.sleep(1)
        
        print(f"{len(outsample_task_ids)=}")

        for task_id in outsample_task_ids:
            submission_response = requests.post(
                submission_url, headers=headers, json={'taskId': task_id}, verify=False
            )
            if submission_response.status_code == 202:
                print(f'✅ Task Id = {task_id}, message = "Successfully submitted"')
            else:
                print(f'❌ Task Id = {task_id}, message = "{submission_response.json()["message"]}"')
            time.sleep(1)
        
        # Clear task lists for the next batch
        insample_task_ids.clear()
        outsample_task_ids.clear()

if __name__ == "__main__":
    simulation_flow()