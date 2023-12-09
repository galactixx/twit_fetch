import unittest

from twitfetch.errors import InvalidLoginError
from twitfetch.fetch import TwitFetch

class TestLoginPassword(unittest.TestCase):
    """
    Test output of correct username but incorrect password.
    """

    def test_incorrect_password(self):
        """
        This test case checks if that we can correctly detect an incorrect password.
        """

        # Instantiate TwitFetch
        twit_fetch = TwitFetch(
            login_username='elonmusk',
            login_password='not elons password',
            account='elonmusk')

        with self.assertRaises(InvalidLoginError):
            twit_fetch.twitter_login()

if __name__ == "__main__":
    unittest.main()