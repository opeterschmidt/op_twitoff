"""Create our flask app"""

from re import DEBUG
from os import getenv
from flask import Flask, render_template, request
from .models import DB, User, Tweet
from .twitter import add_or_update_user
from .predict import predict_user

def create_app():
    """Main app function that creates app"""
    # initialize app
    app = Flask(__name__)

    # Database configuration
    # tell our app where to find our database (basically, give it the file path)
    # "regestering" our database with the app
    # best practice is to obsfuscate where your database is, 
    # so we're grabbing from our environment variables
    app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URI")
    # specifying don't keep track of changes; otherwise can prompt
    # warning in terminal
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # actually connect database and app
    DB.init_app(app)

    # remember @ is a decorator that adds functionality to a function
    @app.route("/")
    # when a person visits this url, then this function is going to be triggered
    def home():
        # return all users on homepage
        users = User.query.all()
        # jinja2 inserts the variables into the html
        return render_template("base.html", title="Home", users=users)


    @app.route("/reset")
    def reset():
        # drop our DB tables
        DB.drop_all()
        # creates tables based on our classes' schemas in .models
        DB.create_all()
        return render_template('base.html', title='Reset DB')


    @app.route("/update")
    def update():
        '''Updates all users'''
        usernames = [user.username for user in User.query.all()]
        for username in usernames:
            add_or_update_user(username)
        return render_template("base.html", title="Update")


    @app.route("/user", methods=["POST"])
    @app.route("/user/<username>", methods=["GET"])
    def user(username=None, message=""):
        """Add users via webpage form"""
        # either take username that was entered or we pull a username from
        # our request.values, whcih would be accessed through the 
        # user submission
        if request.method == "GET":
            tweets = User.query.filter(User.username == username).one().tweets
        
        if request.method == "POST":
            tweets = []
            try:
                username = request.values["user_name"]
                add_or_update_user(username)
                message = f'User "{username}" was successfully added!'
            except Exception as e:
                message = f'Error adding "{username}": {e}'

        return render_template("user.html",
                                title=username,
                                tweets=tweets,
                                message=message)


    @app.route("/compare", methods=["POST"])
    def compare():
        """Compare tweets and predict a user"""
        # user0 and user1 are pulled from forms, 
        # labels are confirmed in base.html
        user0 = request.values["user0"]
        user1 = request.values["user1"]

        if user0 == user1:
            message = "Cannot compare a user to themselves."

        else:
            text = request.values["tweet_text"]
            prediction = predict_user(user0, user1, text)

            message = '"{}" is more likely to be said by {} than {}!'.format(
                        text,
                        # if the predition is user1, then put user1 in space 2
                        # and user0 in space 3
                        # and vice versa
                        user1 if prediction else user0,
                        user0 if prediction else user1
                        )
   
        return render_template("prediction.html",
                               title="Prediction",
                               message=message)


    return app
