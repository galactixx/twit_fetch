from typing import List, Optional, Tuple
from datetime import datetime

from bs4 import BeautifulSoup

from twitfetch._utils import from_iso_format
from twitfetch.static import (
    Element,
    SOCIAL_CONTEXTS,
    TWEET_SOCIAL_CONTEXT,
    TWEET_TEXT
)

class Parse:
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
    
    def find_post_link(self, element: Element, date_tag: BeautifulSoup) -> str:
        """
        Find post link to be able to expand and view entire content.
        """

        element.attribute_value = date_tag.get(element.attribute)
        return element
    
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