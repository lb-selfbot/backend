"""
Misc utils
"""
import os
import re
import io
import random
import string
import hashlib
import datetime

import PIL
import PIL.Image

from django import http

from api.models import User, FreeTrial


def get_user_ip(request: http.HttpRequest) -> str:
    """
    Get the IP address of a user
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(",")[0]
    else:
        ip_address = request.META.get("REMOTE_ADDR")
    return ip_address


def random_string(length: int) -> str:
    """
    Generate a random string
    """
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def image_to_bytes(image: PIL.Image, format: str = "png") -> bytes:
    """
    Convert a PIL image to bytes
    """
    output = io.BytesIO()
    image.save(output, format=format)
    return output.getvalue()


def seconds_to_readable_time(seconds: int) -> str:
    """
    Convert seconds to a readable time
    """
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)

    readable_time = ""

    if days != 0:
        readable_time += f"{days}d "

    if hours != 0:
        readable_time += f"{hours}h "

    if minutes != 0:
        readable_time += f"{minutes}m "

    if seconds != 0:
        readable_time += f"{seconds}s"

    return readable_time.strip() or "0s"


def format_datetime(datetime: datetime.datetime) -> str:
    """
    Format a datetime object
    """
    if datetime is None:
        return "None"
    return datetime.strftime("%Y-%m-%d %H:%M:%S")


def get_rpm() -> int:
    """
    Get the requests per minute
    """
    if os.name == "nt":
        return 0

    nginx_access_log = "/var/log/nginx/access.log"

    with open(nginx_access_log, "r", encoding="utf8") as file:
        lines = file.readlines()[::-1][:5000]

    date_regex = re.compile(r" \[(.*?)\] \"")

    # get current date with timezone
    timezone = datetime.timezone(datetime.timedelta(hours=0))
    now = datetime.datetime.now(tz=timezone)

    requests_in_last_10_minutes = []

    for line in lines:
        date_string = date_regex.findall(line)[0]
        parsed_date = datetime.datetime.strptime(date_string, "%d/%b/%Y:%H:%M:%S %z")

        # check if parsed_date was in the last minute
        if now - parsed_date < datetime.timedelta(minutes=10):
            requests_in_last_10_minutes.append(line)

    return len(requests_in_last_10_minutes) / 10


def clean_filename(filename: str, is_folder: bool = False) -> str:
    """
    Clean a filename
    """
    pattern = r"[^a-zA-Z0-9\._-]"
    if is_folder:
        pattern = r"[^a-zA-Z0-9\._-\/]"

    # Replace invalid characters with underscores
    cleaned = re.sub(pattern, "_", filename)

    # Remove leading and trailing underscores
    cleaned = cleaned.strip("_")

    # Remove leading dot (if any)
    if cleaned.startswith("."):
        cleaned = cleaned[1:]

    # Make sure the result is not "." or ".."
    if cleaned == "" or cleaned == "." or cleaned == "..":
        cleaned = "_"

    return cleaned


def is_user_allowed_trial(
    user: User, computer_name: str, client_ip: str
) -> tuple[bool, str]:
    """
    Check if a user is allowed to use the free trial
    """
    # check if user has already used the free trial
    computer_name_hash = hashlib.sha1(computer_name.encode()).hexdigest()
    if (
        FreeTrial.objects.filter(computer_name_hash=computer_name_hash).exists()
        and computer_name != ""
    ):
        return False, "COMPUTER_NAME_MATCH"

    client_ip_hash = hashlib.sha1(client_ip.encode()).hexdigest()
    if (
        FreeTrial.objects.filter(client_ip_hash=client_ip_hash).exists()
        and client_ip != ""
    ):
        return False, "CLIENT_IP_MATCH"

    # create free trial for user
    FreeTrial.objects.create(
        user=user,
        computer_name_hash=computer_name_hash,
        client_ip_hash=client_ip_hash,
    )

    return True, ""
