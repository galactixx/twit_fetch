import unittest

import validators

from twitfetch.errors import InvalidLoginError
from twitfetch.static import URL_TWITTER_LOGIN
from twitfetch.fetch import TwitFetch

class TestLoginUsername(unittest.TestCase):
    """
    Test login function and output of incorrect username.
    """

    def test_twitter_login(self):
        """
        This test case checks if the Twitter login page is valid and still exists.
        """
        
        url_exists = validators.url(URL_TWITTER_LOGIN)
        self.assertTrue(url_exists, 'Twitter login url is no longer valid')

    def test_incorrect_username(self):
        """
        This test case checks if that we can correctly detect an incorrect username.
        """

        # Instantiate TwitFetch
        twit_fetch = TwitFetch(
            login_username='not a username',
            login_password='not a password',
            account='elonmusk'
        )

        with self.assertRaises(InvalidLoginError):
            twit_fetch.twitter_login()

if __name__ == "__main__":
    unittest.main()