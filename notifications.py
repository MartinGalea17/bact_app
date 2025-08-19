import json
from datetime import datetime
import os

NOTIFICATIONS_FILE = "notifications.json"

def load_notifications():
    try:
        with open(NOTIFICATIONS_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_notifications(notifications):
    with open(NOTIFICATIONS_FILE, "w") as f:
        json.dump(notifications, f, indent=4)

def add_notifications(title, main_info, notification_level, author="Admin"):
    notifications = load_notifications()
    new_id = (max([n["id"] for n in notifications], default=0) + 1)  # safer than len()
    notifications.append({
        "id": new_id,
        "title": title,
        "message": main_info,
        "level": notification_level,
        "author": author,
        "timestamp": datetime.now().isoformat()
    })
    save_notifications(notifications)

def delete_notification(note_id: int) -> bool:
    """
    Delete a notification by its id.
    Returns True if a notification was removed, False otherwise.
    """
    notifications = load_notifications()
    
    # Filter out the one to delete
    updated = [n for n in notifications if n.get("id") != note_id]

    if len(updated) == len(notifications):
        # No change means id not found
        return False  

    save_notifications(updated)
    return True

def get_notifications_by_level(level: str):
    return [n for n in load_notifications() if n["level"] == level]
