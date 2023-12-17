from typing import Dict, List

from playwright.sync_api import Response

Tweet = List[Dict[str, str]]
GraphQLResponse = Response