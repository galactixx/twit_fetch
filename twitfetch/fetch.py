from typing import Dict, List, Optional
import time

from twitfetch.data_structures import TweetInfo
from twitfetch.errors import InvalidLoginError
from twitfetch._parse import Parse
from twitfetch._browser import PlaywrightBrowser
from twitfetch._utils import (
    clean_text,
    convert_string_to_datetime,
)
from twitfetch.static import (
    LOGIN,
    LOGIN_ERROR,
    TWEET,
    TWEET_DATE,
    TWEET_PINNED,
    TWEET_REPOST,
    TWEET_SHOW_MORE,
    TWEET_SHOW_MORE_LINK,
    TWEET_TEXT,
    URL_TWITTER_LOGIN
)

class TwitFetch:
    """
    Given a Twitter account, finds and returns all tweets within a specified time period.
    """
    def __init__(
        self, 
        login_username: str,
        login_password: str,
        account: str,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        tweet_limit: int = 10,
        headless: bool = False):
        self._login_username = login_username
        self._login_password = login_password
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

        self.tweets: List[Dict[str, str]] = []

    def twitter_login(self) -> None:
        """
        Login to Twitter account using information provided in config file.
        """

        login_pipeline = [
            self._login_username,
            self._login_password
        ]

        # Go to Twitter login page and wait some time
        self._browser.go_to_page(url=URL_TWITTER_LOGIN)
        time.sleep(2)

        # Iterate through login pipeline
        for info in login_pipeline:

            # Retrieve page source
            page_source = self._browser.page_to_dom()

            # Parse and find label
            parser = Parse(page_source=page_source)
            element = parser.find_attribute(element=LOGIN)
            time.sleep(2)

            # Generate CSS selector and type in input text
            selector = parser.css_selector(element=element)
            self._browser.type_input(text=info, selector=selector)
            
            # Wait some time
            time.sleep(1)

            # Retrieve page source for comparisons
            page_source_new = self._browser.page_to_dom()

            # Check for error element in new page source
            alerts = Parse(page_source=page_source_new).find_element(
                element=LOGIN_ERROR
            )

            if alerts:
                raise InvalidLoginError()
    
    def _collect_raw_tweets(self) -> List[Dict[str, str]]:
        """
        Collect all raw tweets by scrolling down until appropriate datetime or limit is reached.
        """

        dates_parsed = []
        tweets_collected = []
        
        while True:
            page_source = self._browser.page_to_dom()
            parser = Parse(page_source=page_source)

            # Find all tweets
            tweets = parser.find_elements(element=TWEET)
            
            for tweet in tweets:
                parser.load_element(element=tweet)

                # Detect irellevant tweets to ignore
                pinned = parser.find_element(element=TWEET_PINNED)
                repost = parser.find_element(element=TWEET_REPOST)

                if self._account_at in tweet.text and pinned is None and repost is None:
                    date_posted = parser.find_relevant_datetime(element=TWEET_DATE)
                    text_element = parser.find_element(element=TWEET_TEXT)

                    if date_posted not in dates_parsed:

                        # Detect if tweet is cut-off
                        show_more_element = parser.find_element(element=TWEET_SHOW_MORE)

                        # If so, then go to full-length tweet
                        if show_more_element is not None:
                            share_parent = show_more_element.parent == text_element.parent
                            if share_parent:
                                
                                element = parser.find_show_more(element=TWEET_SHOW_MORE_LINK)

                                # Click on href link
                                self._browser.click_on_selection(
                                    selector=parser.css_selector(element=element)
                                )
                                                                
                                # Find new tweet on "Show More" page
                                page_source_show_more = self._browser.page_to_dom()
                                parser_show_more = Parse(page_source=page_source_show_more)
                                tweet = parser_show_more.find_element(element=TWEET)
                                text_element = parser_show_more.find_element(element=TWEET_TEXT)
                                
                                time.sleep(1)
                                self._browser.go_back_page()

                        # Generate consolidated tweet info
                        if text_element is not None:
                            text = text_element.text
                        else:
                            text = ''

                        dates_parsed.append(date_posted)
                        tweets_collected.append(
                            TweetInfo(
                                author=self.account,
                                date_posted=date_posted.isoformat(),
                                content=clean_text(text=text),
                                is_quote=parser.is_quoted_tweet()
                            )
                        )

            if dates_parsed:
                if min(dates_parsed) < self._time_start_datetime:
                    return tweets_collected
            
            self._browser.scroll_down()
                
    def fetch_tweets(self) -> None:
        """
        Fetch all tweets within a time period from a given Twitter account.
        """

        # Login to Twitter account
        self.twitter_login()

        # Go to account page
        self._browser.go_to_page(url=self._account_url)
        time.sleep(1)

        # Collect and load tweets
        self.tweets = self._collect_raw_tweets()