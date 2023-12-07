import json
from typing import List, Optional
import time

from bs4 import BeautifulSoup

from twitfetch._parse import Parse
from twitfetch._browser import PlaywrightBrowser
from twitfetch._utils import (
    clean_text,
    convert_string_to_datetime,
)
from twitfetch._static import (
    ATTRIBUTE_SOCIAL_CONTEXT,
    ATTRIBUTE_TEXT,
    ATTRIBUTE_TEXT_RESULT,
    ATTRIBUTE_TEXT_SHOW_MORE,
    LOGIN_INFO_TAG,
    TAG_TWEET,
    URL_TWITTER_LOGIN
)

class TwitFetch:
    """
    Given a Twitter account, finds and returns all tweets within a specified time period.
    """
    def __init__(
        self, 
        account: str, 
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        tweet_limit: int = 10,
        headless: bool = False):
        self.account = account
        self._time_start = time_start
        self._time_end = time_end
        self._tweet_limit = tweet_limit

        # Generate account url
        self._account_at = f'@{self.account}'
        self._account_url = f'https://twitter.com/{self.account}'

        # Convert times into datetime
        self._time_start_datetime = convert_string_to_datetime(date=self._time_start)
        self._time_end_datetime = convert_string_to_datetime(date=self._time_end)

        # Instantiate playwright browser
        self._browser = PlaywrightBrowser(headless=headless)

        # Load user login information
        with open('config.json', 'r') as file:
            self._login_info = json.load(file)

    def _twitter_login(self) -> None:
        """
        Login to Twitter account using information provided in config file.
        """

        login_pipeline = [
            self._login_info["username"],
            self._login_info["password"]
        ]

        # Go to Twitter login page and wait some time
        self._browser.go_to_page(url=URL_TWITTER_LOGIN)
        time.sleep(2)

        # Iterate through all login pipeline
        for info in login_pipeline:

            # Retrieve page source
            page_source = self._browser.page_to_dom()

            # Parse and find label
            parser = Parse(page_source=page_source)
            attribute, result = parser.find_attribute(tag=LOGIN_INFO_TAG, attribute='class')
            time.sleep(2)

            selector = parser.css_selector(tag='input', attribute=attribute, result=result)
            self._browser.type_input(text=info, selector=selector)
            
            # Wait some time after logging in
            time.sleep(2)
        
    def _collect_raw_tweets(self) -> List[BeautifulSoup]:
        """
        Scroll down in account page until appropiate datetime is reached.
        """

        dates_parsed = []
        tweets_collected = []
        
        while True:
            page_source = self._browser.page_to_dom()
            parser = Parse(page_source=page_source)

            # Find all tweets
            tweets = parser.find_elements(tag=TAG_TWEET)
            
            for tweet in tweets:
                parser.load_element(element=tweet)
                pinned = parser.find_element(
                    tag='div',
                    attribute={ATTRIBUTE_TEXT: ATTRIBUTE_SOCIAL_CONTEXT}
                )
                repost = parser.find_element(
                    tag='span',
                    attribute={ATTRIBUTE_TEXT: ATTRIBUTE_SOCIAL_CONTEXT}
                )

                if self._account_at in tweet.text and pinned is None and repost is None:
                    date = parser.find_relevant_datetime()

                    if date not in dates_parsed:

                        # Detect if tweet is cut-off
                        show_more_element = parser.find_element(
                            tag='div', attribute={ATTRIBUTE_TEXT: ATTRIBUTE_TEXT_SHOW_MORE}
                        )
                        
                        # If so, then go to full-length tweet
                        if show_more_element is not None:
                            show_more_link = parser.find_show_more()

                            # Click on href link
                            self._browser.click_on_selection(
                                selector=parser.css_selector(tag='a', attribute='href', result=show_more_link))
                                                            
                            # Find new tweet on "Show More" page
                            page_source_show_more = self._browser.page_to_dom()
                            parser_show_more = Parse(page_source=page_source_show_more)
                            tweet = parser_show_more.find_element(tag=TAG_TWEET)
                            
                            time.sleep(1)
                            self._browser.go_back_page()

                        dates_parsed.append(date)
                        tweets_collected.append(tweet)
            
            if min(dates_parsed) < self._time_start_datetime:
                return tweets_collected
            
            self._browser.scroll_down()
        
    def fetch_tweets(self) -> List[dict]:
        """
        Fetch all tweets within a time period from a given Twitter account.
        """
        
        tweets_scraped: List[dict] = []
        parser = Parse()

        # Login to Twitter account
        self._twitter_login()

        # Go to account page
        self._browser.go_to_page(self._account_url)
        time.sleep(1)

        # Retrieve tweets and iterate through
        tweets = self._collect_raw_tweets()
        for tweet in tweets:
            parser.load_element(element=tweet)

            # Find date posted
            date_posted = parser.find_relevant_datetime()
            
            text_element = parser.find_element(
                tag='div',
                attribute={ATTRIBUTE_TEXT: ATTRIBUTE_TEXT_RESULT}
            )
            
            if text_element is not None:
                text = text_element.text
            else:
                text = ''

            # Consolidate tweet info
            tweet_info = {
                'author': self.account,
                'date_posted': date_posted.isoformat(),
                'content': clean_text(text=text)
            }

            if tweet_info not in tweets_scraped:
                tweets_scraped.append(tweet_info)

        return tweets_scraped