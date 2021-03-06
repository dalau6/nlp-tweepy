import tweepy

from textblob import TextBlob
from collections import defaultdict

# simple, average a list of numbers with a guard clause to avoid division by zero
def mean(lst):
    return sum(lst)/len(lst) if len(lst) > 0 else 0

# call the textblob sentiment analysis API and noun phrases API and return it as a dict
def get_sentiment_and_np(sentence):
    blob = TextBlob(sentence)
    return{
        'sentiment': mean([s.sentiment.polarity for s in blob.sentences if s.sentiment.polarity != 0.0]),
        'noun_phrases': list(blob.noun_phrases)
    }

# use the tweepy API to get the last 50 posts from a user’s timeline
# We will want to get the full text if the text is truncated, and we will also remove retweets since they’re not tweets by that particular account.
def get_tweets(handle):
    auth = tweepy.OAuthHandler('YOUR_DEVELOPER_KEY')
    auth.set_access_token('YOUR_DEVELOPER_SECRET_KEY')
    api = tweepy.API(auth)
    tl = api.user_timeline(handle, count=50)
    tweets = []
    for tl_item in tl:
        if 'retweeted_status' in tl_item._json:
            Continue # this is a retweet
        if tl_item._json['truncated']:
            status = api.get_status(tl_item._json['id'], tweet_mode='extended') # get full text
            tweets.append(status._json['full_text'])
        else:
            tweets.append(tl_item._json['text'])
    return tweets

# http and https are sometimes recognized as noun phrases, so we filter it out.
# We also try to skip noun phrases with very short words to avoid certain false positives
# If this were a commercial app, we would want a more sophisticated filtering strategy.
def good_noun_phrase(noun_phrase):
    noun_phrase_list = noun_phrase.split(' ')
    for np in noun_phrase_list:
        if np in {'http', 'https'} or len(np) < 3:
            return False
    return True

    # reshapes the tagged tweets into dictionaries that can be easily consumed by the front-end app
def group_tweets(processed_tweets):
    # Sort it by sentiment
    sentiment_sorted = sorted(processed_tweets, key=lambda x: x['data']['sentiment'])

    # collect tweets by noun phrases. One tweet can be present in the list of more than one noun phrase, obviously.
    tweets_by_np = defaultdict(list)

    for pt in processed_tweets:
        for np in pt['data']['noun_phrases']:
            tweets_by_np[np].append(pt)
    grouped_by_np = {np.title(): tweets for np, tweets in tweets_by_np.items() if len(tweets) > 1 and good_noun_phrase(np)}
    return sentiment_sorted, grouped_by_np

# download, filter, and analyze the tweets
def download_analyze_tweets(accounts):
    processed_tweets = []
    for account in accounts:
        for tweet in get_tweets(account):
            processed_tweet = ' '.join([i for i in tweet.split(' ') if not i.startswith('@')])
            res = get_sentiment_and_np(processed_tweet)
            processed_tweets.append({
                'account': account,
                'tweet': tweet,
                'data': res
            })

    sentiment_sorted, grouped_by_np = group_tweets(processed_tweets)
    return processed_tweets, sentiment_sorted, grouped_by_np