from twitfetch.data_structures import Element

# General constants
DATE_FORMAT = "%Y-%m-%d"
URL_TWITTER_LOGIN = 'https://twitter.com/i/flow/login'

LOGIN = Element(tag='input', attribute='class')
LOGIN_ERROR = Element(tag='div', attribute='role', attribute_value='alert')

TWEET = Element(tag='article')
TWEET_DATE = Element(tag='time', attribute='datetime')
TWEET_TEXT = Element(tag='div', attribute='data-testid', attribute_value='tweetText')
TWEET_SHOW_MORE = Element(tag='div', attribute='data-testid', attribute_value='tweet-text-show-more-link')
TWEET_SHOW_MORE_LINK = Element(tag='a', attribute='href')
TWEET_PINNED = Element(tag='div', attribute='data-testid', attribute_value='socialContext')
TWEET_REPOST = Element(tag='span', attribute='data-testid', attribute_value='socialContext')