from typing import Any, List, Optional, Tuple
from datetime import datetime

from bs4 import BeautifulSoup

from twitfetch._utils import from_iso_format
from twitfetch._static import (
    ATTRIBUTE_DATETIME,
    TAG_TIME
)

class Parse:
    """
    Provides a variety of helper methods for parsing the DOM of a webpage.
    """
    def __init__(self, page_source: Optional[str] = None):

        if page_source is not None:
            self._soup = BeautifulSoup(page_source, "html.parser")

    def css_selector(self, tag: str, attribute: str, result: str) -> str:
        """
        Generate CSS selector based on attribute information.
        """

        return f'{tag}[{attribute}="{result}"]'
            
    def find_attribute(self, tag: str, attribute: str) -> Tuple[str, Any]:
        """
        Find and load the result for a given attribute and tag.
        """

        element = self.find_element(tag=tag)
        result = element.get(attribute)

        if isinstance(result, list):
            result = ' '.join(result)
        
        return attribute, result
    
    def find_element(self, tag: str, attribute: Optional[dict] = None) -> BeautifulSoup:
        """
        Find and return a single element for a given tag.
        """

        if attribute is not None:
            return self._soup.find(tag, attribute)

        return self._soup.find(tag)

    def find_elements(self, tag: str) -> List[BeautifulSoup]:
        """
        Find and return all elements for a given tag.
        """
    
        return self._soup.find_all(tag)

    def load_element(self, element: BeautifulSoup) -> None:
        """
        Load given element and overwrite soup variable.
        """

        self._soup = element

    def find_show_more(self) -> str:
        """
        Find and determine appropriate show more link.
        """

        a_tags = self.find_elements(tag='a')
        href_attributes = [i.get('href') for i in a_tags if i is not None]
        show_more_link = [i for i in href_attributes if '/status/' in i][0]

        return show_more_link

    def find_relevant_datetime(self) -> datetime:
        """
        From time tag in each tweet, determine relevant datetime to pull.
        """

        date_tags = self.find_elements(tag=TAG_TIME)
        dates = [
            from_iso_format(
                date=date.get(ATTRIBUTE_DATETIME)
            ) for date in date_tags
        ]
        
        # Convert date from iso format
        date = max(dates)
        return date