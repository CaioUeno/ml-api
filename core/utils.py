from datetime import datetime
import hashlib
import re


def time_now() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")


def generate_md5(string: str):
    return hashlib.md5(string.encode()).hexdigest()


def extract_hashtags(text: str):
    return re.findall(r"#[a-zA-Z]+", text)
