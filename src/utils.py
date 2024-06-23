import json, pathlib
from datetime import datetime

CONFIG_PATH = str(pathlib.Path(__file__).parent.absolute()) + "/data/configs.json"
STRIKES_PATH = str(pathlib.Path(__file__).parent.absolute()) + "/data/strikes.json"

OPERATOR_ROLE_ID = 1167687375913234464
ALT_ROLE_ID = 1212783196920356965

def get_current_time() -> str:
    return datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f")

def log_command_call(command_name: str, caller: str, is_slash_command: bool = True) -> str:
    prefix = "/" if is_slash_command else "!"

    current_time = get_current_time()

    return f"{current_time} | \033[1;33m{prefix}{command_name}\033[0;0m: Called by \033[0;32m'{caller}'\033[0;0m"

def log_message(command_name: str, message: str, is_slash_command: bool) -> str:
    prefix = "/" if is_slash_command else "!"

    current_time = get_current_time()

    header = f"\033[1;33m{prefix}{command_name}\033[0;0m:"

    return f"{current_time} | {header} {message}"

def load_config() -> dict:
    with open(CONFIG_PATH, "r") as config_file:
        return json.load(config_file)

def refresh_config(new_configs: dict) -> None:
    config_file = open(CONFIG_PATH, "w")

    json.dump(new_configs, config_file, indent=4)

def get_strikes() -> dict:
    with open(STRIKES_PATH, "r") as strike_file:
        return json.load(strike_file)

def update_strikes(updated_strikes: dict) -> None:
    strike_file = open(STRIKES_PATH, "w")

    json.dump(updated_strikes, strike_file, indent=4)