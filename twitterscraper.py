import config
import json
import pickle 
import tweepy

class TwitterClient(object):
    """
    Generic Twitter Class
    """
    def __init__(self):
        """
        Class Constructur/Initializaiton Method
        """
        CONSUMER_KEY = config.consumer_key
        CONSUMER_SECRET = config.consumer_secret
        ACCESS_TOKEN = config.access_token
        ACCESS_TOKEN_SECRET = config.access_token_secret

        try:
            self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            self.auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def get_tweets_data(self, username, number_of_tweets=200, cycles=15):
        """
        Get a specific number of a user's tweets.

        Returns a list of strings that represent a user's tweets.
        """
        self.api.wait_on_rate_limit = True

        # We will save each batch of tweets to a list
        tweets_data = []

        new_tweets = self.api.user_timeline(screen_name=username, count=number_of_tweets, tweet_mode='extended')

        tweets_data.extend(new_tweets)

        # Use oldest-tweet to get max_id
        oldest_tweet = tweets_data[-1].id - 1

        for i in range(cycles):
            # We use max_id to prevent duplicates
            new_tweets = self.api.user_timeline(screen_name=username, count=number_of_tweets, tweet_mode='extended', max_id=oldest_tweet)

            tweets_data.extend(new_tweets)

            # Id is updated to oldest tweet - 1 to keep track of tweets
            oldest_tweet = tweets_data[-1].id - 1

            print('{} tweets downloaded so far.'.format(len(tweets_data)))

        return tweets_data
    
    def get_tweet_text(self, tweets_data):
        """
        Returns a list of the text of every tweet.
        """
        
        tmp = []

        # Get only the tweet text
        tweets_for_pickle = [tweet.full_text for tweet in tweets_data]
        
        for tweet_text in tweets_for_pickle: 
            # Appending tweets data to the empty array tweets_data
            tmp.append(tweet_text)  

        return tmp

def main():
    api = TwitterClient()

    # We will get 3,000 tweets using cycles=15
    tweets_data = api.get_tweets_data(username='realDonaldTrump', number_of_tweets=200, cycles=15)

    tweets_text = api.get_tweet_text(tweets_data)

    with open('trump_tweets_data.pickle','wb') as f:
        pickle.dump(tweets_data, f)

    with open('trump_tweets_text.pickle', 'wb') as f:
        pickle.dump(tweets_text, f)

if __name__ == '__main__':
    main()
