import hashlib
import re
from configparser import RawConfigParser
from datetime import datetime, timedelta
from typing import Any, Dict, List

import numpy as np


def time_now() -> str:
    """Returns UTC datetime as string considering the timezone."""
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")


def expand_date(date: str, increment: bool = False) -> str:

    """
    Add time (hour, minute, second and timezone) to a date-only string. If increment=True then add 1 day to the parsed date.
    To use a date as a filter when querying Elasticsearch, date strings must match the index date format.

    Arguments:
        date (str): string represeting a date without time (2022-01-01);
        increment (bool, optional): whether to increment a day or not. Defaults to False.

    Returns:
        str: string representation of the date with time information.
    """

    as_datetime_obj = datetime.strptime(date, "%Y-%m-%d")

    if increment:
        as_datetime_obj = as_datetime_obj + timedelta(days=1)

    return as_datetime_obj.astimezone().strftime("%Y-%m-%d %H:%M:%S %z")


def date_filter(date_from: str, date_to: str) -> dict:

    """
    Parse date range to a DSL clause (Elasticsearch query).
    It increments the date_to to include the entire day.

    Arguments:
        date_from (str): date-only (no hour, minute, second and timezone) string represeting the lower date;
        date_to (str): date-only (no hour, minute, second and timezone) string represeting the higher date.

    Returns:
        dict: DSL date range clause.
    """

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
    """Generate the md5 of a string."""
    return hashlib.md5(string.encode()).hexdigest()


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from a text."""
    return re.findall(r"#[a-zA-Z]+", text)


def validate_username(text: str) -> bool:

    """
    Validate an username. It must start with a letter followed by letters and numbers only.

    Arguments:
        text (str): desired username.

    Returns:
        bool: whether username is valid or not.
    """

    # first char must be a word, then words or numbers
    pattern = re.compile(r"[a-zA-Z]+[a-zA-Z0-9]+")

    # pattern matched
    if pattern.match(text):

        (_, end) = pattern.match(text).span(0)

        # check if fully matched
        if end == len(text):
            return True

    return False


def sentiment_to_str(sentiment: int) -> str:
    mapping = {-1: "negative", 0: "neutral", 1: "positive"}
    return mapping[sentiment]


def get_config(section: str, key: str) -> Any:

    """
    Read value from configuration file(.cfg).

    Arguments:
        section (str): section name from file;
        key (str): key name to extract value.

    Raises:
        KeyError: If section name does not exist;
        KeyError: If key name does not exist;

    Returns:
        Any: value from section/key provided.
    """

    config = RawConfigParser()
    config.read("api.cfg")

    if not config.has_section(section):
        raise KeyError(f"Section does not exist: {section}.")

    if not config.has_option(section, key):
        raise KeyError(f"Key does not exist: {key}.")

    return config.get(section, key)


def adjust_quantification(estimated_rates: np.ndarray, prevalence: Dict[str, int]):

    prevalence_array = np.asarray(
        [prevalence["negative"], prevalence["neutral"], prevalence["positive"]]
    )
    prevalence_array = prevalence_array / prevalence_array.sum()

    adjusted_prevalence = {}

    try:
        adjusted_count = np.linalg.solve(estimated_rates, prevalence_array)
        # it may return values outside [0, 1] so clip it
        adjusted_count = np.clip(adjusted_count, 0, 1)

        # normalize
        adjusted_count /= adjusted_count.sum()
        # it may divide by 0
        adjusted_count = np.nan_to_num(adjusted_count)

        adjusted_prevalence["negative"] = adjusted_count[0]
        adjusted_prevalence["neutral"] = adjusted_count[1]
        adjusted_prevalence["positive"] = adjusted_count[2]

        return adjusted_prevalence

    except np.linalg.LinAlgError:
        return prevalence
