# Imports
import tweepy
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from flask import Flask, render_template
import re

# Configuring Sentiment Intensity Analyzer
sia = SentimentIntensityAnalyzer()

def is_positive(tweet: str) -> bool:
    return sia.polarity_scores(tweet)["compound"] > 0
def is_negative(tweet: str) -> bool:
    return sia.polarity_scores(tweet)["compound"] < 0
def is_neutral(tweet: str) -> bool:
    return sia.polarity_scores(tweet)["compound"] == 0

# Authentication Keys
API_Key = ("e5Y9nYJT9h5zbQvTK0GOEukt3")
API_Key_S = ("LymzvJvR8qNPZcF5VTfsh34YFdQUbHVuVp3UkWDCg7D6SJGS7A")
ACC_Token = ("972186091750154241-0e0Hb2D6sKd6AHGoTfFGY34bgAVx0sW")
ACC_Token_S = ("rGA1BxibuH1VzMx8fljPzJFZINHKA6HKJX9Eum6pZLqqG")

# Authenticate to Twitter
auth = tweepy.OAuthHandler(API_Key, API_Key_S)
auth.set_access_token(ACC_Token, ACC_Token_S)
api = tweepy.API(auth)

# Get Tweet data to dashboard
def analyseTweets(searchQuery):
    if searchQuery == "favicon.ico":
        return None
    else:
        print(searchQuery)
        # Variables
        topicScorePos = 0
        topicScoreNeg = 0
        global posList 
        global negList 
        posList = []
        negList = []

        allTweets = tweepy.Cursor(api.search_tweets,
                            q=searchQuery,
                            count = 500,
                            result_type="recent",
                            tweet_mode="extended",
                            include_entities=False,
                            lang="en").items(500) # Get 500 tweets
        # Check each tweet
        for tweet in allTweets:
            tokens = nltk.sent_tokenize(tweet.full_text) # Seperate Tweets Into Sentences
            for x in tokens:
                # Remove RT @Username:
                result = re.search('RT @(.*):', x)
                if result == None:
                    x_ = x
                else:
                    x_ = x.replace(('RT @' + result.group(1) + ":"), "")
                if is_positive(x_):
                    topicScorePos += 1
                    posList.append(x_)
                elif is_negative(x_):
                    topicScoreNeg -= 1
                    negList.append(x_)
                else:
                    pass
        totalScore = round(topicScorePos/(topicScoreNeg * -1), 2)
        """
        print()
        print("PositveScore: " + str(topicScorePos))
        print("NegativeScore: " + str(topicScoreNeg))
        print("Positive/Negative = " + str(totalScore))
        """
        if totalScore <= 1.2 and totalScore >= 0.8:
            print("neutral sentiment")
            return '0'
        elif totalScore > 1.2 and totalScore <= 2:
            print("positive sentiment")
            return '1'
        elif totalScore > 2 and totalScore <= 3:
            print("really positive sentiment")
            return '2'
        elif totalScore > 3:
            print("overwhelmingly positive sentiment")
            return '3'
        elif totalScore >= 0.5:
            print("negative sentiment")
            return '-1'
        elif totalScore >= 0.33:
            print("very negative sentiment")
            return '-2'
        elif totalScore < 0.33:
            print("overwhelmingly negative sentiment")
            return '-3'
        else:
            return None

# Webapp route
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<term>')
def x(term):
    term_ = term.replace("~"," ")
    return render_template('page.html', sent=(analyseTweets(term_)), pos = posList, neg = negList)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')