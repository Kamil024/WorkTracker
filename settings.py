import json
import os

SETTINGS_FILE = "user_settings.json"

def save_theme_preference(theme):
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
    settings["theme"] = theme
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def load_theme_preference():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
            return settings.get("theme", "light")
    return "light"
