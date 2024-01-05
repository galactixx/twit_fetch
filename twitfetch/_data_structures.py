from typing import Optional

from dataclasses import dataclass

@dataclass
class Element:
    """
    Data structure to hold key characteristic of significant html tags or attributes.
    """

    tag: Optional[str] = None
    attribute: Optional[str] = None
    attribute_value: Optional[str] = None

@dataclass
class TweetInfo:
    """
    Data structure to hold resulting tweet info pulled.
    """
    
    tweet_id: str
    author: str
    date_posted: str
    content: str
    is_quote: bool