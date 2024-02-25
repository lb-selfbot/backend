"""
Captcha utils
"""

import os
import time

import requests

MAX_TRIES = 20


def solve_recaptchav2(url: str, site_key: str) -> str:
    """
    Solve reCAPTCHA v2
    """
    payload = {
        "clientKey": os.environ.get("CAPMONSTER_API_KEY", ""),
        "task": {
            "type": "RecaptchaV2TaskProxyless",
            "websiteURL": url,
            "websiteKey": site_key,
        },
    }

    resp = requests.post(
        "https://api.capmonster.cloud/createTask", json=payload, timeout=10
    )

    print(resp.status_code, resp.text)

    task_id = resp.json()["taskId"]
    if not task_id:
        raise Exception("Failed to create task")

    payload = {
        "clientKey": os.environ.get("CAPMONSTER_API_KEY", ""),
        "taskId": task_id,
    }

    # Wait for the task to be solved
    for i in range(MAX_TRIES):
        time.sleep(2 + i * 0.5)

        resp = requests.get(
            f"https://api.capmonster.cloud/getTaskResult",
            json=payload,
            timeout=10,
        )

        print(resp.status_code, resp.text)

        if resp.json()["status"] == "ready":
            return resp.json()["solution"]["gRecaptchaResponse"]

    raise Exception("Failed to solve task")
