from typing import Optional
from datetime import datetime

from dataclasses import dataclass

@dataclass
class Element:
    """
    Data structure to hold key characteristic of significant html tags or attributes.

    Attributes:
        tag (str): The tag.
        attribute (str): The attribute.
        attribute_value (Optional[str]): The attribute value.
    """

    tag: str
    attribute: str
    attribute_value: Optional[str] = None

@dataclass
class Tweet:
    """
    Tweet details pulled from the GraphQL response.

    Attributes:
        user_name (str): The user name of a Twitter account.
        user_id (str): The user ID of a Twitter account.
        tweet_id (str): The tweet ID.
        created (datetime): The UTC datetime of tweet creation.
        content (str): The string content of the tweet.
    """

    user_name: str
    user_id: str
    tweet_id: str
    created: datetime
    content: str