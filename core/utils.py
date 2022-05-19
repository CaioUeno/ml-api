from datetime import datetime
import hashlib
import re
from typing import List
from configparser import RawConfigParser


def time_now() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")


def generate_md5(string: str) -> str:
    return hashlib.md5(string.encode()).hexdigest()


def extract_hashtags(text: str) -> List[str]:
    return re.findall(r"#[a-zA-Z]+", text)


def validate_username(text: str) -> bool:

    # first char must be a word, then words or numbers
    pattern = re.compile(r"[a-zA-Z]+[a-zA-Z0-9]+")

    # pattern matched
    if pattern.match(text):

        # check if fully or partially matched
        (_, end) = pattern.match(text).span(0)

        if end == len(text):
            return True

    return False


def get_config(section: str, key: str):

    config = RawConfigParser()
    config.read("api-config.cfg")

    if not config.has_section(section):
        raise KeyError(f"Section does not exist: {section}.")

    if not config.has_option(section, key):
        raise KeyError(f"Key does not exist: {key}.")

    return config.get(section, key)
