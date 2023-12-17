from twitfetch.data_structures import Element

# General constants
DATE_FORMAT = "%Y-%m-%d"
URL_TWITTER_LOGIN = 'https://twitter.com/i/flow/login'
SOCIAL_CONTEXTS = ['reposted', 'pinned']

# Login element constants
LOGIN = Element(tag='input', attribute='class')
LOGIN_ERROR = Element(tag='div', attribute='role', attribute_value='alert')

# Tweet element constants
TWEET = Element(tag='article')
TWEET_DATE = Element(tag='time', attribute='datetime')
TWEET_TEXT = Element(tag='div', attribute='data-testid', attribute_value='tweetText')
TWEET_SHOW_MORE = Element(attribute='data-testid', attribute_value='tweet-text-show-more-link')
TWEET_POST_LINK = Element(tag='a', attribute='href')
TWEET_SOCIAL_CONTEXT = Element(attribute='data-testid', attribute_value='socialContext')
TWEET_ARTICLE = Element(tag='article', attribute='role', attribute_value='article')