import os
import toml
from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent

CONFIG_FILE_PATH = os.path.join(ROOT_PATH, "configs/config.toml")
VERSION_PATH = os.path.join(ROOT_PATH, "VERSION")
CHANGELOG_PATH = os.path.join(ROOT_PATH, "CHANGELOG.md")

configs = toml.load(CONFIG_FILE_PATH)

MODEL = configs.get("model")
API_BASE = configs.get("api_base")
API_KEY = configs.get("api_key")
POE_KEY = configs.get("poe_key")
HISTORY_LENGTH = configs.get("history_length")

VERSION: str = "0.0.0"
with open(VERSION_PATH, "r") as file:
    VERSION = file.read()
    
CHANGELOG: str = ""
with open(CHANGELOG_PATH, "r") as file:
    CHANGELOG = file.read()