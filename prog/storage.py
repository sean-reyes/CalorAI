import json
from pathlib import Path


DATA_DIRECTORY = Path(__file__).resolve().parent
MENUS_FILE = DATA_DIRECTORY / "menus.json"
SELECTIONS_FILE = DATA_DIRECTORY / "last_selections.json"


def load_menus(path=MENUS_FILE):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_menus(menus, path=MENUS_FILE):
    with path.open("w", encoding="utf-8") as file:
        json.dump(menus, file, indent=4)


def load_selections(path=SELECTIONS_FILE):
    try:
        with path.open("r", encoding="utf-8") as file:
            selections = json.load(file)
    except (OSError, json.JSONDecodeError):
        return []
    return selections if isinstance(selections, list) else []


def save_selections(selections, path=SELECTIONS_FILE):
    with path.open("w", encoding="utf-8") as file:
        json.dump(selections, file)
