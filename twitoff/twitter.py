import tweepy
import spacy
from os import getenv
from .models import DB, Tweet, User


# Get our API keys
key = getenv('TWITTER_API_KEY')
secret = getenv("TWITTER_API_KEY_SECRET")

# authenticate with Twitter
TWITTER_AUTH = tweepy.OAuthHandler(key, secret)

# open a connection to the API
TWITTER = tweepy.API(TWITTER_AUTH)

def add_or_update_user(username):
    """Add or update a user to the DB"""
    # try all of this, if no errors get thown, save the DB
    # if errors do get thrown, make
    try:
        # get the user data from twitter
        twitter_user = TWITTER.get_user(screen_name=username)
 
        # check to see if user is already in datase
        # if they're already in DB, do nothing
        # if not, insert them
        # or statement gets evaluated from left to right (works like if/else)
        # wants either of these statements to return a value that is not null
        # so, if first statement returns a user, it stops executing and returns
        # that user
        # if that returns a null value/not usable, then it continues and tries
        # second statement
        db_user = (User.query.get(twitter_user.id) or
                   User(id=twitter_user.id, username=username))

        # won't duplicate a user in DB if already exists
        DB.session.add(db_user)

        # get the user's tweets from their "timeline"
        tweets = twitter_user.timeline(count=200,
                                       exclude_replies=True,
                                       include_rts=False,
                                       tweet_mode='extended',
                                       since_id=db_user.newest_tweet_id
                                       )

        # assign newest_tweet_id
        # check to see if the newest tweet in the DB is equal to the newest
        # tweet from the Twitter API, if they're not equal then that means that
        # the user has posted new tweets that we should add to our DB.
        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        # add the individual tweets to the DB
        for tweet in tweets:
            tweet_vector = vectorize_tweet(tweet.full_text)
            db_tweet = Tweet(id=tweet.id,
                            text=tweet.full_text[:300],
                            user_id=db_user.id,
                            vect=tweet_vector)
                            # [:300] ensures we don't exceed the character count
                            # from our Tweet schema
            DB.session.add(db_tweet)

    except Exception as error:
        print(f"Error when processing {username}: {error}")
        raise error

    else:
        # final step to save DB
        DB.session.commit()


# load pretrained spacy word embeddings model
nlp = spacy.load("my_model/") 
# / indicates this is a folder

# Vectorize tweets (turn them into word embeddings)
def vectorize_tweet(tweet_text):
    """Create a word embedding for a tweet"""
    return nlp(tweet_text).vector