from typing import List, Optional
import time

from playwright.sync_api import Response

from twitfetch.errors import InvalidLoginError
from twitfetch._utils import (
    convert_string_to_datetime,
    generate_url,
    parse_json
)
from twitfetch._browser import PlaywrightBrowser
from twitfetch._parse import (
    ParseDOM,
    parse_tweets_response
)
from twitfetch.typing import Tweets
from twitfetch._constants import (
    Endpoints,
    GRAPHQL_ENDPOINT,
    LOGIN,
    LOGIN_ERROR,
    URL_TWITTER,
    URL_TWITTER_LISTS,
    URL_TWITTER_LOGIN
)

class ResponseCallback:
    """
    Callback functionality for detecting GraphQL response.
    
    Args:
        endpoint (Endpoints): The GraphQL endpoint.
    """
    def __init__(self, endpoint: Endpoints):
        self._endpoint = endpoint
        self.responses: List[Response] = []

    def callback(self, response: Response) -> None:
        """
        Callback for interception of GraphQL response.

        Args:
            response (Response): The response from network request.
        """

        if GRAPHQL_ENDPOINT in response.url and self._endpoint.value in response.url:
            if response.status == 200:
                self.responses.append(response)

class TwitFetch:
    """
    Given a Twitter account, finds and returns all tweets within a specified time period.

    Args:
        login_username (str): .
        login_password (str): .
        time_start (Optional[str]): .
        time_end (Optional[str]): .
        tweet_limit (int): .
        headless (bool): .

    Attributes:
        _login_username (str): .
        _login_password (str): .
        account (str): .
        _time_start (Optional[str]): .
        _time_end (Optional[str]): .
        _tweet_limit (int): .
        _time_start_datetime (datetime): .
        _time_end_datetime (datetime): .
        _browser (PlaywrightBrowser): .
    """
    def __init__(
        self, 
        login_username: str,
        login_password: str,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        tweet_limit: int = 10,
        headless: bool = False
    ):
        self._login_username = login_username
        self._login_password = login_password
        self._time_start = time_start
        self._time_end = time_end
        self._tweet_limit = tweet_limit

        # Convert times into datetime
        self._time_start_datetime = convert_string_to_datetime(date=self._time_start)
        self._time_end_datetime = convert_string_to_datetime(date=self._time_end)

        # Instantiate playwright browser
        self._browser = PlaywrightBrowser(headless=headless)

        # Login using account into Twitter
        self.twitter_login()

    def list_latest_tweets(self, list_id: str) -> None:
        """
        Access the ListLatestTweetsTimeline endpoint to grab latest tweets from a Twitter list.
        
        Args:
            list_id (str): A string being the ID of the Twitter list.
        """

        list_url = generate_url(url=URL_TWITTER_LISTS, path=list_id)
        response = self._query(url=list_url, endpoint=Endpoints.ListLatestTweetsTimeline)

    def user_tweets(self, account: str) -> Tweets:
        """
        Access the UserTweets endpoint to grab latest tweets from a Twitter account.

        Args:
            account (str): A string being the screen name of a Twitter account.
        """

        account_url = generate_url(url=URL_TWITTER, path=account)
        response = self._query(url=account_url, endpoint=Endpoints.UserTweets)

        # Parse response to extract tweets and details
        tweets = parse_tweets_response(
            tweets=response,
            users=[account],
            do_remove_retweets=True
        )

        return tweets
    
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
            page_source = self._browser.page_to_dom()

            # Parse and find label
            parser = ParseDOM(page_source=page_source)
            element = parser.find_attribute(element=LOGIN)
            time.sleep(2)

            # Generate CSS selector and type in input text
            selector = parser.css_selector(element=element)
            self._browser.type_input(text=info, selector=selector)
            time.sleep(1)

            # Retrieve page source for comparisons
            time.sleep(3)
            page_source_new = self._browser.page_to_dom()

            # Check for error element in new page source
            alerts = ParseDOM(page_source=page_source_new).find_element(
                element=LOGIN_ERROR
            )

            if alerts:
                raise InvalidLoginError()

    def _query(self, url: str, endpoint: Endpoints) -> List[Response]:
        """
        Given an endpoint, will query and retrieve response from GraphQL.

        Args:
            url (str): The url to navigate where tweets will be populated.
            endpoint (Endpoints): The GraphQL endpoint.

        Returns:
            dict: The GraphQL response as a dictionary.
        """

        response_callback = ResponseCallback(endpoint=endpoint)
        self._browser.page.on('response', response_callback.callback)

        # Go to account page
        self._browser.go_to_page(url=url, wait_for_tweet=True)

        # Loop until the response is found
        while not response_callback.responses:
            time.sleep(0.2)

        # Parse response and extract JSON
        response = parse_json(responses=response_callback.responses)
        return response
        