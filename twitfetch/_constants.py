from enum import Enum

from twitfetch._data_structures import Element

DATE_FORMAT = "%Y-%m-%d"
GRAPHQL_ENDPOINT = '/graphql'

RED = '\033[31m'
GREEN = '\033[32m'
WHITE = '\033[0m'

# Twitter URLs
TWITTER_LOGIN = 'https://twitter.com/i/flow/login/'
TWITTER_LISTS = 'https://twitter.com/i/lists/'

# HTML elements
LOGIN = Element(tag='input', attribute='class')
LOGIN_ERROR = Element(tag='div', attribute='role', attribute_value='alert')
TWEET_ARTICLE = Element(tag='article', attribute='role', attribute_value='article')

class Endpoints(Enum):
    """
    Store GraphQL endpoints.

    Attributes:
        UserTweets (str): Endpoint for tweets of a specific Twitter account
        ListLatestTweetsTimeline (str): Endpoint for tweets of a specific Twitter list
    """

    UserTweets = 'UserTweets'
    ListLatestTweetsTimeline = 'ListLatestTweetsTimeline'

class UserKeys:
    """
    Relevant JSON keys in User GraphQL response.

    Attributes:
        USER_ID (str): Key for the user ID.
    """

    USER_ID = 'rest_id'

class TweetKeys:
    """
    Relevant JSON keys in Tweet GraphQL response.

    Attributes:
        USER_ID (str): Key for the user ID.
        TWEET_ID (str): Key for the tweet ID.
        CREATED (str): Key for the created datetime.
        CONTENT (str): Key for the tweet content.
    """

    USER_ID = 'user_id_str'
    TWEET_ID = 'id_str'
    CREATED = 'created_at'
    CONTENT = 'full_text'

class GeneralKeys:
    """
    Relevant JSON keys appearing in a generic GraphQL response.

    Attributes:
        LEGACY (str): Key for legacy.
        MESSAGE (str): Key for the message.
        INSTRUCTIONS (str): Key for the instructinos.
        ENTRIES (str): Key for the entries.
        RETWEET (str): Key for the retweet.
    """

    LEGACY = 'legacy'
    MESSAGE = 'message'
    INSTRUCTIONS = 'instructions'
    ENTRIES = 'entries'
    RETWEET = 'retweeted_status_result'