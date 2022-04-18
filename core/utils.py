from datetime import datetime
import hashlib


def time_now() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def generate_md5(string: str):
    return hashlib.md5(string.encode()).hexdigest()
