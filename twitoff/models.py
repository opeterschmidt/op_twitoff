"""SQLAlchemy User and Tweet models for our database"""

from flask_sqlalchemy import SQLAlchemy


# create a DB Object from SQLAlchemy class
DB = SQLAlchemy()


# Make User table
# not sure how .Model operates as an attribute of DB
class User(DB.Model):
    '''Creates a User table with SQLAlchemy'''
    # id column
    # basically creating a column attribute for DB class (?)
    # not sure how BigInteger and String operate as attributes of DB class
    id = DB.Column(DB.BigInteger, primary_key=True)

    # username column
    username = DB.Column(DB.String, nullable=False)

    # tweets = (comes from DB.backref)
    # newest tweet id
    # makes it so we only query for tweets that are more recent than this tweet ID
    # keeps track of id for newest tweet by user
    newest_tweet_id = DB.Column(DB.BigInteger)

    def __repr__(self):
        return f"user: {self.username}"


# Make Tweet table
class Tweet(DB.Model):
    '''Keeps track of tweets for each user'''
    # id
    id = DB.Column(DB.BigInteger, primary_key=True)

    # tweet text
    # Unicode allows for emojis, links, and other symbols
    # limited to 300 characters (to be extra sure we capture all potential 280 
    # characters in any given tweet)
    text = DB.Column(DB.Unicode(300))

    # ForeignKey tells us this lives in another table, and what it matches
    # in this case, Tweet.user_id = User.id
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey("user.id"), nullable=False)

    # user
    # makes a two-way relationship between our user and our tweet
    # adds an attribute to both tables, in this case User.tweet or Tweet.tweet 
    # (confirm on Tweet.tweet)
    # The relationship between tables is what we call one to many—
    # one user can have many tweets, there is a user associated with each tweet,
    # and a tweet associated with each user (check this last part??)
    # as if there was an imaginary tweets attribute to User class
    user = DB.relationship("User", backref=DB.backref("tweets", lazy=True))

    # place to store our word embeddigns/vectorization
    # PickleType allows us to store numpy arrays in a DB
    vect = DB.Column(DB.PickleType, nullable=False)

    def __repr__(self):
        return f"Tweet: {self.text}"