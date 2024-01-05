from typing import List, Optional, Tuple
from datetime import datetime

from bs4 import BeautifulSoup

from twitfetch._utils import from_iso_format
from twitfetch._data_structures import TweetInfo
from twitfetch._constants import Element

class ParseGraphQL:
    """
    Provides a variety of helper methods for parsing the GraphQL API response.
    """
    def __init__(self, response: dict):
        self._response = response

    def parse_tweets(self) -> List[TweetInfo]:
        """
        Parse and consolidate tweet details in response.
        """

        parsed_tweets = []

        if self._response:
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

                        tweet_parsed_user_id = tweet_parsed.get(TweetKeys.USER_ID)
                        if tweet_parsed_user_id in user_ids:

                            created_at = tweet_parsed.get(TweetKeys.CREATED)
                            if created_at:
                                created_at = _format_created_at(created_at=created_at)

                                tweet_parsed[TweetKeys.CREATED] = created_at

                            if do_structured:
                                parsed_tweets.append(
                                    _consolidate_tweet_info(tweet=tweet_parsed)
                                )
                            else:
                                parsed_tweets.append(tweet_parsed)

class ParseDOM:
    """
    Provides a variety of helper methods for parsing the DOM of a webpage.
    """
    def __init__(self, page_source: Optional[str] = None):

        if page_source is not None:
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
        elif element.tag is None:
            return self._soup.find({element.attribute: element.attribute_value})
        else:
            return self._soup.find(element.tag)

    def find_elements(self, element: Element) -> List[BeautifulSoup]:
        """
        Find and return all elements for a given tag.
        """

        if element.attribute is not None and element.attribute_value is not None:
            return self._soup.find_all(element.tag, {element.attribute: element.attribute_value})
        elif element.tag is None:
            return self._soup.find_all({element.attribute: element.attribute_value})
        elif element.attribute is not None:
            return self._soup.find_all(element.tag, {element.attribute: True}) 
        else:
            return self._soup.find_all(element.tag)

    def load_element(self, element: BeautifulSoup) -> None:
        """
        Load new page source or element and overwrite soup variable.
        """

        self._soup = element

    def is_quoted_tweet(self) -> bool:
        """
        Determine if tweet is a quoted tweet and return a boolean.
        """

        number_of_instances_of_text = self.find_elements(element=TWEET_TEXT)

        return len(number_of_instances_of_text) > 1

    def find_relevant_datetime(self, element: Element) -> Tuple[BeautifulSoup, datetime]:
        """
        From time tag in each tweet, determine relevant datetime to pull.
        """

        date_tag = self.find_element(element=element)
        date_time = from_iso_format(date=date_tag.get(element.attribute))

        return date_tag, date_time
    
    def find_post_link(self, element: Element, date_tag: BeautifulSoup) -> Element:
        """
        Find post link to be able to expand and view entire content.
        """

        element.attribute_value = date_tag.get(element.attribute)
        return element
    
    def find_tweet_id(self, post_link: Element) -> int:
        """
        Based on post link we can extract the tweet id.
        """

        return post_link.attribute_value.split('/')[-1]
    
    @property
    def social_contexts(self) -> bool:
        """
        Finds the social context element and ensures that it is not a repost or pinned tweet.
        """

        social_contexts = self.find_elements(element=TWEET_SOCIAL_CONTEXT)
        is_social_context = any(
            element.text.strip().lower() in SOCIAL_CONTEXTS for element in social_contexts
            if element
        )
        return is_social_context