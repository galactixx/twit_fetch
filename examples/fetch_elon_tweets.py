import json

from datetime import datetime, timedelta

from twitfetch.fetch import TwitFetch

def main(username: str, password: str) -> None:
    """
    Fetch all of Elon Musk's Tweets in the last two days.
    """

    # Get date two days ago
    today = datetime.now()
    two_days_ago = today - timedelta(days=2)
    date_two_days_ago = two_days_ago.strftime('%Y-%m-%d')

    # Fetch all tweets
    twit_fetch = TwitFetch(
        login_username=username,
        login_password=password,
        time_start=date_two_days_ago
    )
    
    twit_fetch.user_tweets(account='elonmusk')

    for tweet in twit_fetch.tweets:
        print(tweet)
        print('---------------------------------------')

if __name__ == "__main__":

    # Load in username and password from config.json
    with open('config.json') as f:
        config = json.load(f)

    main(
        username=config['username'],
        password=config['password']
    )