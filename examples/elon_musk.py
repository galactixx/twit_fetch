from datetime import datetime, timedelta

from twitfetch.fetch import TwitFetch

def main():
    """
    Fetch all of Elon Musk's Tweets in the last day.
    """

    # Get today's date
    today = datetime.now()
    two_days_ago = today - timedelta(days=2)
    date_two_days_ago = two_days_ago.strftime('%Y-%m-%d')

    # Fetch all tweets
    twit_fetch = TwitFetch(account='elonmusk', time_start=date_two_days_ago)
    tweets = twit_fetch.fetch_tweets()

    for tweet in tweets:
        print(tweet)
        print('---------------------------------------')

if __name__ == "__main__":
    main()