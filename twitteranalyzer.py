import pickle
import re
import nltk
from nltk.tokenize import TweetTokenizer
import string
from textblob import TextBlob 

class twitterAnalyzer:
    """ 
    Generic class with text analysis functions specifically designed for tweets
    """
    
    def __init__(self, tweets, tweets_data=None, sentiment_data=None, positive_tweets=None, negative_tweets=None, neutral_tweets=None):
        """
        Class Constructur/Initializaiton Method
        """
        if tweets_data is None:
            tweets_data = []
        if sentiment_data is None:
            sentiment_data = []
        if positive_tweets is None:
            positive_tweets = []
        if negative_tweets is None:
            negative_tweets = []
        if neutral_tweets is None:
            neutral_tweets = []

        self.tweets = tweets
        self.tweets_data = tweets_data
        self.sentiment_data = sentiment_data
        self.positive_tweets = positive_tweets
        self.negative_tweets = negative_tweets
        self.neutral_tweets = neutral_tweets
    
    def tokenize(self):
        """
        Uses the built in tokenize function in the nltk module for tweets.
        """
        tknzr = TweetTokenizer()
        tkn = []
        for tweet in self.tweets:
            for word in tknzr.tokenize(tweet):
                tkn.append(word)
        return tkn
    
    def clean_tweet(self, tweet): 
        """ 
        This function, unlike the tokenize function from the nltk package, clean the tweet text by removing all links and special characters using regex statements.
        """
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def clean_all_tweets(self):
        """
        Cleans the list of all tweets using the regex utlity function.

        Returns a list of cleaned tweet.
        """
        clean_tweets = []
        for tweet in self.tweets:
            clean_tweets.extend(self.clean_tweet(tweet).split())
        return clean_tweets
    
    def to_lower(self, word_list):
        """
        Makes all text lowercase.

        Returns a list of words that are all lowercase.
        """
        return [word.lower() for word in word_list]
    
    def word_freq(self, word_list):
        """
        Returns a histogram of all words and their frequency from a list of words.
        """
        hist = {}
        for word in word_list:
            hist[word] = hist.get(word, 0) + 1
        return hist
    
    def print_most_common(self, hist, n=10):
        """
        Prints a list of the n most common words from a histogram.
        """
        t = []
        for word,freq in hist.items():
            t.append((freq, word))
        t.sort(reverse=True)

        for word,freq in t[:n]:
            print(word, '\t', freq)
    
    def filter_stop_words(self, word_list):
        """
        Removes all stopwords and punctuations.

        Returns a list of words without specified stopwords and punctuations.
        """
        punctuation = list(string.punctuation)
        file = open("stopwords.txt")
        stopwords = []
        strippables = string.punctuation + string.whitespace
        for line in file:
            stopwords.append(line.strip(strippables))
        stopwords.extend(punctuation)

        terms_without_stop = [word for word in word_list if word not in stopwords]

        return terms_without_stop
    
    def tweet_sentiment_analysis(self, tweet):
        """
        Return whether a tweet is positive, negative, or neutral.

        Uses the textblob module.
        TextBlob.sentiment gives a polarity and subjectivity score. Subjectivity is from 0 to 1 and determines are factual vs opinionated the statement is.

        Returns a string.
        """
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return ['Positive', analysis.sentiment.polarity, analysis.sentiment.subjectivity]
        elif analysis.sentiment.polarity == 0:
            return ['Neutral', analysis.sentiment.polarity, analysis.sentiment.subjectivity]
        else:
            return ['Negative', analysis.sentiment.polarity, analysis.sentiment.subjectivity]
    
    def do_sentiment_analysis(self):
        """
        Does sentiment analysis on all tweets

        Sets the following attributes:
        self.sentiment_data
        self.positive_tweets
        self.negative_tweets
        self.neutral_tweets

        Return a list of objects with the following form:
        {
            'text': String that is the tweet
            'sentiment': String that is 'Positive', 'Negative' or 'Neutral'
            'polarity': Float from -1 to 1
            'subjectivity': Float from 0 to 1
        }
        """

        tweets_sentiment = []

        for tweet in self.tweets:
            parsed_tweet = {}
            parsed_tweet['text'] = tweet
            sentiment_data = self.tweet_sentiment_analysis(tweet)
            parsed_tweet['sentiment'] = sentiment_data[0]
            parsed_tweet['polarity'] = sentiment_data[1]
            parsed_tweet['subjectivity'] = sentiment_data[2]

            tweets_sentiment.append(parsed_tweet)

        self.sentiment_data = tweets_sentiment
        self.positive_tweets = [tweet for tweet in self.sentiment_data if tweet['sentiment'] == 'Positive']
        self.negative_tweets = [tweet for tweet in self.sentiment_data if tweet['sentiment'] == 'Negative']
        self.neutral_tweets = [tweet for tweet in self.sentiment_data if tweet['sentiment'] == 'Neutral']

        return tweets_sentiment
    
    def print_recent_tweets(self, sentiment, count=5):
        """
        Print specifieid number of most recent tweets that are positive.

        Sentiment is a string value that must be the following:
        'positive'
        'negative'
        'neutral'

        Count is an intenger that represents the number of tweets to print; the default is 5.
        """
        print("\nMost recent {} tweets:".format(sentiment))

        def print_tweet(tweets, count):
            for tweet in tweets[:count]:
                print(tweet['text'], "\n")

        if sentiment == 'positive':
            print_tweet(self.positive_tweets, count)
        elif sentiment == 'negative':
            print_tweet(self.negative_tweets, count)
        elif sentiment == 'neutral':
            print_tweet(self.neutral_tweets, count)
        else:
            raise ValueError("Sentiment must be a string that is 'positive', 'negative', or 'neutral'.")
    
    def print_extreme_tweets(self, sentiment, count=1, num_score=False):
        """
        Prints the tweet with the largest positive or negative polarity value.

        Count is an integer that represetnts the number of tweets to print after the data is sourted; the deafult is 1.

        num_score determines whether or not to print the polarity and subjectivity score of the tweet as well.
        """
        def return_polarity(tweet):
            return tweet['polarity']
        def return_subjectivity(tweet):
            return tweet['subjectivity']

        print("The top {} most {} tweets:".format(count, sentiment))

        if sentiment == 'positive':
            sorted_tweet = sorted(self.positive_tweets, key=return_polarity, reverse=True)
        elif sentiment == 'negative':
            sorted_tweet = sorted(self.negative_tweets, key=return_polarity)
        else:
            raise ValueError("Sentiment must be a string that is either 'positive' or 'negative'.")
        
        for tweet in sorted_tweet[:count]:
            print(tweet['text'])
            if num_score:
                print("Polarity: {} | Subjectivity: {}".format(tweet['polarity'], tweet['subjectivity']), "\n")
    
    def print_objective_tweets(self, count=5, objective=True):
        """
        Print tweets with the highest or lowest level of objectivity.

        Count is an integer that determines how many tweets to print.

        Objective is a boolean value that determines whether to print highly subjective or highly objective tweets.
        """
        def return_subjectivity(tweet):
            return tweet['subjectivity']
        
        print("Most objective tweets:")
        if objective:
            sorted_objective = sorted(self.sentiment_data, key=return_subjectivity)
        elif not objective:
            sorted_objective = sorted(self.sentiment_data, key=return_subjectivity, reverse=True)
        else:
            raise ValueError('Objective must be a boolean value')

        for tweet in sorted_objective[:count]:
            print(tweet['text'])
            print("Subjectivity: {}".format(tweet['subjectivity']), "\n")

    def print_sentiment_summary(self, sentiment_data):
        """
        Print various summary statistics and example tweets based on the sentiment analysis
        """

        self.print_recent_tweets('positive')
        self.print_recent_tweets('negative')
        self.print_recent_tweets('neutral')

        self.print_extreme_tweets('positive', num_score=True)
        self.print_extreme_tweets('negative', num_score=True)

        self.print_objective_tweets(count=5)
        self.print_objective_tweets(count=5, objective=False)


    


def main():
    with open('trump_tweets_text.pickle', 'rb') as input_file:
        tweets = pickle.load(input_file)
    
    with open('trump_tweets_data.pickle', 'rb') as input_file:
        tweets_data = pickle.load(input_file)


    trump = twitterAnalyzer(tweets=tweets, tweets_data=tweets_data)
    print(len(trump.tweets))

    # print(trump.tweets_data[0].full_text)

    # tokenize = trump.tokenize()
    # tokenize_lower = trump.to_lower(tokenize)
    # hist_tokenize = trump.word_freq(tokenize_lower)
    # trump.print_most_common(hist_tokenize, n=10)

    # # Let's compare nltk's tokenize designed for tweets to just stripping all words down bare:
    # clean_tweets = trump.clean_all_tweets()
    # clean_tweets = trump.to_lower(clean_tweets)
    # hist_clean_tweets = trump.word_freq(clean_tweets)
    # trump.print_most_common(hist_clean_tweets, n=10)

    # # What if we do both without stop-word?
    # print("Printing most common non-stop words with tokenize method:")
    # tokenize_lower_no_stop = trump.filter_stop_words(tokenize_lower)
    # hist_tokenize_no_stop = trump.word_freq(tokenize_lower_no_stop)
    # trump.print_most_common(hist_tokenize_no_stop, n=10)

    # print("Printing most common non-stop words with regex clean method:")
    # clean_tweets_no_stop = trump.filter_stop_words(clean_tweets)
    # hist_clean_tweets_no_stop = trump.word_freq(clean_tweets_no_stop)
    # trump.print_most_common(hist_clean_tweets_no_stop, n=10)

    # Do sentiment analysis
    sentiment_tweets = trump.do_sentiment_analysis()
    trump.print_sentiment_summary(sentiment_tweets)


if __name__ == '__main__':
    main()