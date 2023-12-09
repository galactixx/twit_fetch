import re
from typing import Optional
from datetime import datetime

import pytz

from twitfetch.static import DATE_FORMAT

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