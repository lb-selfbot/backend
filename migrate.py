import os
import json
import datetime

import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lightningbot.settings")

django.setup()

with open(r"D:\\Downloads\\users.json", "r") as f:
    users = json.load(f)

from api.models import User, Key

for user in users:
    key = user["license_key"]

    if key == "null":
        key = None
    else:
        key = Key.objects.create(
            key=key,
            created_by="Database Migrate",
            create_reason="Migrated from old database"
        )

    u = User.objects.create(
        id=int(user["id"]),
        username=user["username"],
        is_staff=user["admin"] == "1",
        is_tester=user["tester"] == "1",
        logins=int(user["logins"]),
        heartbeats=int(user["heartbeats"]),
        login_time=int(user["login_time"]),
        hwid=user["hwid"].replace("null", ""),
        hwid_resets=user["hwidresets"],
        redeemed_key=key,
        account_type=user["key_type"].replace("null", "None"),
        password="bcrypt$"+user["password"],
        created_at=datetime.datetime.utcfromtimestamp(float(user["created_at"])),
        last_selfbot_login=datetime.datetime.utcfromtimestamp(float(user["last_auth"])),
        last_selfbot_ping=datetime.datetime.utcfromtimestamp(float(user["last_heartbeat"])),
    )

    if key is not None:
        key.redeemed_by = u
        key.save()
