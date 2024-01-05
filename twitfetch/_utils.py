import re
from typing import List, Optional, Union
from datetime import datetime

import pytz

from twitfetch._constants import DATE_FORMAT

def convert_string_to_datetime(date: Optional[str]) -> datetime:
    """
    Convert parameter string into localized datetime object.
    """

    if date is None: return None
    return pytz.utc.localize(
        datetime.strptime(date, DATE_FORMAT)
    )

def clean_text(text: str) -> str:
    """
    Given a block of text, all new lines and extra spaces are removed.
    """

    # Replace new lines and tabs with a space
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    
    # Replace multiple spaces with a single space
    text = re.sub(' +', ' ', text).strip()

    return text

def from_iso_format(date: str) -> datetime:
    """
    Convert Twitter formatted ISO string date into datetime object.
    """

    # Remove the 'Z' at the end, which indicates Zulu (UTC) time
    date_str = date.replace('Z', '+00:00')

    # Convert to datetime object
    date_time = datetime.fromisoformat(date_str)

    return date_time

def find_key_in_dict(obj: Union[dict, list], key: str) -> List[dict]:
    """
    Find all values of a given key within a nested dict or list of dicts.
    """

    def helper(obj: Union[dict, list], key: str, lst: list) -> list:
        if not obj:
            return lst

        if isinstance(obj, list):
            for e in obj:
                lst.extend(helper(e, key, []))
            return lst

        if isinstance(obj, dict) and obj.get(key):
            lst.append(obj[key])

        if isinstance(obj, dict) and obj:
            for k in obj:
                lst.extend(helper(obj[k], key, []))
        return lst

    return helper(obj, key, [])