"""
Hosting API Utils
"""

import os
from enum import Enum

import requests


class WorkerStatus(Enum):
    """
    Worker status
    """

    stopped = 0
    running = 1


def get_worker_status() -> WorkerStatus:
    """
    Get the worker status
    """
    try:
        response = requests.get(
            os.environ.get("HOSTING_API_URL") + "/api/v1/status",
            headers={"Authorization": os.environ.get("HOSTING_API_KEY")},
            timeout=5,
        )

        return WorkerStatus(int(response.text))
    except Exception:
        return WorkerStatus.stopped


def list_files(user_id: str) -> dict:
    """
    List files
    """
    try:
        response = requests.get(
            os.environ.get("HOSTING_API_URL") + "/api/v1/list-files",
            headers={
                "Authorization": os.environ.get("HOSTING_API_KEY"),
                "User-Id": user_id,
            },
            timeout=5,
        )

        return response.json()
    except Exception:
        return []


def delete_folder(user_id: str, folder_path: str) -> dict:
    """
    Delete a folder
    """
    try:
        response = requests.post(
            os.environ.get("HOSTING_API_URL") + "/api/v1/delete-folder",
            headers={
                "Authorization": os.environ.get("HOSTING_API_KEY"),
                "User-Id": user_id,
            },
            data={
                "folder_path": folder_path,
            },
            timeout=5,
        )

        return response.json()
    except Exception:
        return []


def delete_file(user_id: str, file_path: str) -> dict:
    """
    Delete a file
    """
    try:
        response = requests.post(
            os.environ.get("HOSTING_API_URL") + "/api/v1/delete-folder",
            headers={
                "Authorization": os.environ.get("HOSTING_API_KEY"),
                "User-Id": user_id,
            },
            data={
                "file_path": file_path,
            },
            timeout=5,
        )

        return response.json()
    except Exception:
        return []


def download_file(user_id: str, file_path: str) -> requests.Response:
    """
    Delete a file
    """
    response = requests.get(
        os.environ.get("HOSTING_API_URL") + "/api/v1/delete-folder",
        headers={
            "Authorization": os.environ.get("HOSTING_API_KEY"),
            "User-Id": user_id,
        },
        params={
            "file_path": file_path,
        },
        timeout=5,
        stream=True,
    )

    response.raise_for_status()

    return response
