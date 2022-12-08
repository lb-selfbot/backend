"""
GitHub utils
"""
import os
import io
import zipfile

import requests


def _get_token() -> str:
    """
    Get the GitHub token
    """
    return f"Bearer {os.environ.get('GITHUB_TOKEN')}"


def get_all_artifacts(owner: str, repo: str) -> list:
    """
    Get all artifacts
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/artifacts"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": _get_token(),
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.get(url, headers=headers, timeout=10)

    if not response.ok:
        raise Exception(f"Failed to get artifacts: {response.status_code}")

    return list(map(lambda x: x["archive_download_url"], response.json()["artifacts"]))


def get_latest_artifact(owner: str, repo: str) -> str:
    """
    Get the latest artifact
    """
    return get_all_artifacts(owner, repo)[0]


def download_artifact(url: str, path: str) -> None:
    """
    Download an artifact
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": _get_token(),
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.get(url, headers=headers, timeout=10)

    if not response.ok:
        raise Exception(f"Failed to download artifact: {response.status_code}")

    raw_zip = io.BytesIO(response.content)

    try:
        with zipfile.ZipFile(raw_zip) as zip_file:
            zip_file.extractall(path)
    except zipfile.BadZipFile as exc:
        raise Exception("Failed to extract zip file") from exc


def download_latest_artifact(owner: str, repo: str, path: str) -> None:
    """
    Download the latest artifact
    """
    download_artifact(get_latest_artifact(owner, repo), path)
