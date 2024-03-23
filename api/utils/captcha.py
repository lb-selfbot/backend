"""
Captcha utils
"""

import os
import time

import requests


def create_task_recaptchav2(url: str, site_key: str) -> str:
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

    task_id = resp.json()["taskId"]
    if not task_id:
        raise Exception("Failed to create task")

    return str(task_id)


def get_task_status(task_id: str) -> str:
    """
    Get task status
    """
    payload = {
        "clientKey": os.environ.get("CAPMONSTER_API_KEY", ""),
        "taskId": task_id,
    }

    resp = requests.get(
        f"https://api.capmonster.cloud/getTaskResult",
        json=payload,
        timeout=10,
    )

    status = {"status": resp.json()["status"], "solution": ""}

    if resp.json()["status"] == "ready":
        status["solution"] = resp.json()["solution"]["gRecaptchaResponse"]

    return status
