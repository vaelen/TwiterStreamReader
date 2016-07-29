#!/usr/bin/env python

# Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import sys
import json

from pymongo import MongoClient
from tweet_helper import TweetHelper

# This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
        def __init__(self):
                self.tweet_helper = TweetHelper()
                
        def on_data(self, data):
                self.tweet_helper.parse_json(data)
                return True

        def on_error(self, status):
                print >> sys.stderr, "Error: ", status

if __name__ == '__main__':
        
        import ConfigParser

        config = ConfigParser.RawConfigParser()
        config.read('twitter.cfg')
        
        if len(sys.argv) < 2 :
                print >> sys.stderr, "Please provide at least one topic."
                exit(1)

        topics = sys.argv[1:]

        # Variables that contains the user credentials to access Twitter API
        access_token = config.get("Twitter", "access_token")
        access_token_secret = config.get("Twitter", "access_token_secret")
        consumer_key = config.get("Twitter", "consumer_key")
        consumer_secret = config.get("Twitter", "consumer_secret")

        # This handles Twitter authetification and the connection to Twitter Streaming API
        l = StdOutListener()
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        stream = Stream(auth, l)

        print >> sys.stderr, "Tracking topics: ", topics
        
        stream.filter(track=topics)

