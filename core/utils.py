import hashlib
import re
from configparser import RawConfigParser
from datetime import datetime, timedelta
from typing import List


def time_now() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")


def expand_date(date: str, increment: bool = False) -> str:

    if increment:
        return (
            (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1))
            .astimezone()
            .strftime("%Y-%m-%d %H:%M:%S %z")
        )

    return (
        datetime.strptime(date, "%Y-%m-%d")
        .astimezone()
        .strftime("%Y-%m-%d %H:%M:%S %z")
    )


def date_filter(date_from: str, date_to: str) -> dict:

    if date_from is None and date_to is None:
        return None

    if date_to is None:
        return {"range": {"tweeted_at": {"gte": expand_date(date_from)}}}

    if date_from is None:
        return {"range": {"tweeted_at": {"lte": expand_date(date_to, increment=True)}}}

    return {
        "range": {
            "tweeted_at": {
                "gte": expand_date(date_from),
                "lte": expand_date(date_to, increment=True),
            }
        }
    }


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


def sentiment_to_str(sentiment: int) -> str:
    mapping = {-1: "negative", 0: "neutral", 1: "positive"}
    return mapping[sentiment]


def get_config(section: str, key: str):

    config = RawConfigParser()
    config.read("api.cfg")

    if not config.has_section(section):
        raise KeyError(f"Section does not exist: {section}.")

    if not config.has_option(section, key):
        raise KeyError(f"Key does not exist: {key}.")

    return config.get(section, key)
