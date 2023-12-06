import json
from typing import List, Optional
import time

from bs4 import BeautifulSoup

from twitfetch._browser import PlaywrightBrowser
from twitfetch._utils import (
    clean_text,
    convert_string_to_datetime,
    from_iso_format
)
from twitfetch._static import (
    ATTRIBUTE_DATETIME,
    ATTRIBUTE_TEXT,
    ATTRIBUTE_TEXT_RESULT,
    ATTRIBUTE_TEXT_SHOW_MORE,
    LOGIN_INFO_TAG,
    TAG_TIME,
    TAG_TWEET,
    URL_TWITTER_LOGIN
)

class TwitFetch:
    """"""
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
            content = self._browser.page_to_dom()

            # Parse and find label
            soup = BeautifulSoup(content, "html.parser")
            element = soup.find(LOGIN_INFO_TAG)
            element_attr = ' '.join(element.get('class'))
            time.sleep(2)

            self._browser.type_input(
                tag='input',
                text=info, 
                selector=f'class="{element_attr}"'
            )
            
            # Wait some time after logging in
            time.sleep(2)
        
    def _collect_raw_tweets(self) -> List[BeautifulSoup]:
        """
        Scroll down in account page until appropiate datetime is reached.
        """

        dates_parsed = []
        tweets_collected = []
        
        while True:
            content = self._browser.page_to_dom()
            soup = BeautifulSoup(content, "html.parser")

            tweets: List[BeautifulSoup] = soup.find_all(TAG_TWEET)

            for tweet in tweets:
                if self._account_at in tweet.text and 'Pinned' not in tweet.text:
                    date_tags: List[BeautifulSoup] = tweet.find_all(TAG_TIME)
                    date = from_iso_format(
                        date=date_tags[0].get(ATTRIBUTE_DATETIME)
                    )

                    if date not in dates_parsed:

                        # Detect if tweet is cut-off
                        show_more_element = tweet.find('div', {ATTRIBUTE_TEXT: ATTRIBUTE_TEXT_SHOW_MORE})

                        # If so, then go to full-length tweet
                        if show_more_element is not None:
                            a_tags: List[BeautifulSoup] = tweet.find_all('a')
                            href_attributes = [i.get('href') for i in a_tags if i is not None]
                            post_link = [i for i in href_attributes if '/status/' in i][0]

                            # Click on href link
                            self._browser.click_on_selection(selector=f'a[href="{post_link}"]')
                            
                            content = self._browser.page_to_dom()
                            soup = BeautifulSoup(content, "html.parser")
                            tweet = soup.find(TAG_TWEET)

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

        # Login to Twitter account
        self._twitter_login()
        self._browser.go_to_page(self._account_url)
        time.sleep(1)

        tweets = self._collect_raw_tweets()
        for tweet in tweets:
            date_tags: List[BeautifulSoup] = tweet.find_all(TAG_TIME)
            date_posted = from_iso_format(
                date=date_tags[-1].get(ATTRIBUTE_DATETIME)
            )
            
            text_element = tweet.find('div', {ATTRIBUTE_TEXT: ATTRIBUTE_TEXT_RESULT})

            if text_element is not None:
                text = text_element.text
            else:
                text = ''

            # Consolidate tweet info
            tweet_info = {
                'author': self.account,
                'date_posted': date_posted,
                'content': clean_text(text=text)
            }

            if tweet_info not in tweets_scraped:
                tweets_scraped.append(tweet_info)

        return tweets_scraped