from typing import List

from playwright.sync_api import Response

from twitfetch._data_structures import Tweet

Tweets = List[Tweet]
GraphQLResponse = Response