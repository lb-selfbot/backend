import os
import json
import datetime

import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lightningbot.settings")

django.setup()

with open(r"D:\\Downloads\\users.json", "r") as f:
    raw_users = json.load(f)

with open(r"D:\\Downloads\\keys.json", "r") as f:
    raw_keys = json.load(f)

with open(r"D:\\Downloads\\purchases.json", "r") as f:
    raw_purchases = json.load(f)

from api.utils import keys as key_utils
from api.models import User, Key, Order

user_ids = {user["id"]: user for user in raw_users}
users = {user["username"]: user for user in raw_users}

keys = {key["license_key"]: key for key in raw_keys}

orders = {order["order_id"]: order for order in raw_purchases}


User.objects.all().delete()
Key.objects.all().delete()
Order.objects.all().delete()

# first create all objects

for i, user in enumerate(raw_users):
    print(f"Creating user {i + 1}/{len(raw_users)}     ", end="\r")

    User.objects.create(
        id=int(user["id"]),
        username=user["username"],
        is_staff=user["admin"] == "1",
        is_tester=user["tester"] == "1",
        logins=int(user["logins"]),
        heartbeats=int(user["heartbeats"]),
        login_time=int(user["login_time"]),
        hwid=user["hwid"].replace("null", ""),
        hwid_resets=user["hwidresets"],
        redeemed_key=None,
        account_type=user["key_type"].replace("null", "None"),
        password="bcrypt$" + user["password"],
        created_at=datetime.datetime.fromtimestamp(
            float(user["created_at"]),
            tz=timezone.get_current_timezone(),
        ),
        last_selfbot_login=datetime.datetime.fromtimestamp(
            float(user["last_auth"]),
            tz=timezone.get_current_timezone(),
        ),
        last_selfbot_ping=datetime.datetime.fromtimestamp(
            float(user["last_heartbeat"]),
            tz=timezone.get_current_timezone(),
        ),
    )

for i, key in enumerate(raw_keys):
    print(f"Creating key {i + 1}/{len(raw_keys)}     ", end="\r")

    Key.objects.create(
        id=int(key["id"]),
        key=key["license_key"],
        created_by=key["created_by"].replace("null", ""),
        created_at=datetime.datetime.fromtimestamp(
            float(key["created_at"]),
            tz=timezone.get_current_timezone(),
        ),
        create_reason=key["create_reason"].replace("null", ""),
        redeemed_by=None,
    )

for order in raw_purchases:
    Order.objects.create(
        id=int(order["id"]),
        user=None,
        status=order["status"],
        order_id=order["order_id"],
        key=order["delivered_key"],
        raw_json=order["json_data"],
    )

# then update foreign keys

for user in raw_users:
    user_obj = User.objects.get(username=user["username"])

    if user["license_key"] == "null":
        continue

    if user["license_key"] == "ADMIN":
        key = Key.objects.create(
            key=key_utils._generate_key(),
            created_by="DB Migration",
            create_reason="Admin Key",
            redeemed_by=user_obj,
        )
    else:
        try:
            key = Key.objects.get(key=user["license_key"])
        except Key.DoesNotExist:
            key = Key.objects.create(
                key=user["license_key"],
                created_by="DB Migration",
                create_reason="Unexisting Key",
                redeemed_by=user_obj,
            )

    user_obj.redeemed_key = key
    key.redeemed_by = user_obj

    user_obj.save()
    key.save()

for order in raw_purchases:
    order_obj = Order.objects.get(order_id=order["order_id"])

    if order["user"] != "null":
        user = User.objects.get(username=order["user"])
        order_obj.user = user

        order_obj.save()
