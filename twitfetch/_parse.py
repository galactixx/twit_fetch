from typing import Dict, List
from datetime import datetime

from bs4 import BeautifulSoup

from twitfetch._data_structures import Tweet
from twitfetch.typing import Tweets
from twitfetch._constants import (
    Element,
    GeneralKeys,
    TweetKeys
)
from twitfetch._utils import (
    find_key_in_dict,
    remove_from_dict
)

def _format_created_at(created: str) -> datetime:
    """
    Convert created string date provided in GraphQL response to datetime.

    Args:
        created (str): The string representation of the created date field.

    Returns:
        datetime: The converted UTC datetime.
    """

    return datetime.strptime(created, "%a %b %d %H:%M:%S %z %Y")

def parse_tweets_response(
    tweets: List[dict],
    users: List[str],
    do_remove_retweets: bool = False
) -> Tweets:
    """
    Given the JSON tweet response from GraphQL, parses data and return tweets.

    Args:
        tweets (List[dict]): A list of dictionaries corresponding with the GraphQL response.
        users (Dict[str, str]): A dictionary containing the user IDs and keys and user names as values.
        do_remove_retweets (bool): A boolean indicating whether retweets should be removed.

    Returns:
        Tweets: A dictionary or Tweet dataclass containing the relevant tweet details.
    """

    parsed_tweets = []

    if tweets:
        for tweet in tweets:
            instructions = find_key_in_dict(obj=tweet, key=GeneralKeys.INSTRUCTIONS)
            entries = find_key_in_dict(obj=instructions, key=GeneralKeys.ENTRIES)

            for entry in entries:
                tweets_parsed = find_key_in_dict(obj=entry, key=GeneralKeys.LEGACY)
                
                for parse in tweets_parsed:
                    if do_remove_retweets:
                        if parse.get(GeneralKeys.RETWEET):
                            continue

                    tweet_parsed = remove_from_dict(dictionary=parse)

                    tweet_parsed_user_name = tweet_parsed.get(TweetKeys.USER_NAME)
                    if tweet_parsed_user_name:

                        if tweet_parsed_user_name in users:
                            created = tweet_parsed.get(TweetKeys.CREATED)
                            if created:
                                created = _format_created_at(created=created)

                                tweet_parsed[TweetKeys.CREATED] = created.isoformat()

                            user_name = tweet_parsed_user_name
                            user_id = tweet_parsed.get(TweetKeys.USER_ID)
                            tweet_id = tweet_parsed.get(TweetKeys.TWEET_ID)
                            created = tweet_parsed.get(TweetKeys.CREATED)
                            content = tweet_parsed.get(TweetKeys.CONTENT)

                            parsed_tweets.append(
                                Tweet(
                                    user_id=user_id,
                                    user_name=user_name,
                                    tweet_id=tweet_id,
                                    created=created,
                                    content=content
                                )
                            )

    return parsed_tweets

class ParseDOM:
    """
    Provides a variety of helper methods for parsing the DOM of a webpage.
    """
    def __init__(self, page_source: str):
        self._soup = BeautifulSoup(page_source, "html.parser")

    def css_selector(self, element: Element) -> str:
        """
        Generate CSS selector based on attribute information.
        """

        return f'{element.tag}[{element.attribute}="{element.attribute_value}"]'
            
    def find_attribute(self, element: Element) -> Element:
        """
        Find and load the result for a given attribute and tag.
        """

        element_found = self.find_element(element=element)
        attribute_value = element_found.get(element.attribute)

        if isinstance(attribute_value, list):
            attribute_value = ' '.join(attribute_value)
        
        element.attribute_value = attribute_value
        return element
    
    def find_element(self, element: Element) -> BeautifulSoup:
        """
        Find and return a single element for a given tag.
        """

        if element.attribute is not None and element.attribute_value is not None:
            return self._soup.find(element.tag, {element.attribute: element.attribute_value})
        else:
            return self._soup.find(element.tag)