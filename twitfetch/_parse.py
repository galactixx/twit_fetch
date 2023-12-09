from typing import List, Optional
from datetime import datetime

from bs4 import BeautifulSoup

from twitfetch._utils import from_iso_format
from twitfetch.static import (
    Element,
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
        else:
            return self._soup.find(element.tag)

    def find_elements(self, element: Element) -> List[BeautifulSoup]:
        """
        Find and return all elements for a given tag.
        """

        if element.attribute is not None and element.attribute_value is not None:
            return self._soup.find_all(element.tag, {element.attribute: element.attribute_value})
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

    def find_show_more(self, element: Element) -> Element:
        """
        Find and determine appropriate show more link.
        """

        a_tags = self.find_elements(element=element)
        href_attributes = [i.get(element.attribute) for i in a_tags]
        element.attribute_value = [
            i for i in href_attributes if '/status/' in i
        ][0]

        return element

    def find_relevant_datetime(self, element: Element) -> datetime:
        """
        From time tag in each tweet, determine relevant datetime to pull.
        """

        date_tags = self.find_elements(element=element)
        dates = [
            from_iso_format(date=date.get(element.attribute)
            ) for date in date_tags
        ]
        
        # Convert date from iso format
        date = max(dates)
        return date