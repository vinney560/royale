import argparse
import json
import os
import sys
from pathlib import Path

import django
from django.db import transaction


PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))


def seed_channels(json_path):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pr_royale.settings")
    django.setup()

    from app_viulive.models import Channel

    json_path = Path(json_path).resolve()
    with json_path.open("r", encoding="utf-8") as channel_file:
        channel_data = json.load(channel_file)

    if not isinstance(channel_data, dict):
        raise ValueError("Channel JSON must contain a top-level object keyed by channel ID.")

    channels = []
    for channel_id, data in channel_data.items():
        if not isinstance(data, dict):
            raise ValueError(f"Channel '{channel_id}' must contain a JSON object.")

        urls = {
            key: value
            for key, value in data.items()
            if key.startswith("url") and isinstance(value, str) and value
        }
        channels.append(Channel(
            id=channel_id,
            name=data.get("name", "Viu"),
            logo=data.get("logo", ""),
            country=data.get("country", ""),
            access=data.get("access", ""),
            group_title=data.get("group-title", "Viu"),
            urls=urls,
        ))

    with transaction.atomic():
        deleted_count, _ = Channel.objects.all().delete()
        Channel.objects.bulk_create(channels)

    print(f"Reset complete: deleted {deleted_count} existing channel row(s).")
    print(f"Seeded {len(channels)} channel(s) from {json_path}.")


if __name__ == "__main__":
    project_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Reset and seed ViuLive channels.")
    parser.add_argument(
        "json_file",
        nargs="?",
        default=project_dir / "channels-ke.json",
        help="JSON channel file (default: app_viulive/channels-ke.json)",
    )
    args = parser.parse_args()
    seed_channels(args.json_file)
