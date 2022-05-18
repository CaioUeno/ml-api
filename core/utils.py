from datetime import datetime
import hashlib
import re
from typing import List


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
