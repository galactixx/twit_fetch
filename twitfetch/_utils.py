from typing import List, Optional, Union
from datetime import datetime

from playwright.sync_api import Response
import pytz

from twitfetch._constants import TWEET_COLUMNS

def generate_url(url: str, path: str) -> str:
    """
    Generate URL from base URL and path.

    Args:
        url (str): The URL.
        path (str): The path to append to URL.

    Returns:
        str: The generated URL.
    """

    return f'{url}/{path}'

def remove_from_dict(dictionary: dict, columns: List[str] = TWEET_COLUMNS) -> dict:
    """
    Deletes keys that are not in the specified list of columns.

    Args:
        dictionary (dict): A dictionary.
        columns (List[str]): A list of string columns to filter the dictionary keys.

    Returns:
        dict: The dictionary with the relevant keys.
    """

    for key in list(dictionary.keys()):
        if key not in columns:
            del dictionary[key]

    return dictionary

def convert_string_to_datetime(date: Optional[str]) -> datetime:
    """
    Convert parameter string into localized datetime object.
    """

    if date is None: return None
    return pytz.utc.localize(
        datetime.strptime(date, "%Y-%m-%d")
    )

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

def _flatten(sequence: Union[list, tuple]) -> list:
    """
    Flatten list or tuple objects.

    Args:
        sequence (list | tuple): A list or a tuple.

    Returns:
        list: The flattened list or tuple returned as a list.
    """
    
    flat = []
    for e in sequence:
        if isinstance(e, (list, tuple)):
            flat.extend(_flatten(e))
        else:
            flat.append(e)
    return flat

def parse_json(responses: List[Response]) -> list:
    """
    Retrieves and loads JSON from response.

    Args:
        responses (list): A list of responses.

    Returns:
        list: The extracted list of JSON responses.
    """

    temp = responses[:]
    if any(isinstance(r, (list, tuple)) for r in responses):
        temp = _flatten(responses)
    results = []

    # Iterate through responses
    for r in temp:
        try:
            data = r.json()
            results.append(data)
        except Exception as e:
            print('Cannot parse JSON response', e)
    return results