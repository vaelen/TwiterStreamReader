#!/usr/bin/env python

# Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import sys
import json

from pymongo import MongoClient

class TweetHelper:
        def __init__(self):
                self.client = MongoClient()
                self.db = self.client.twitter
                self.tweets = self.db.tweets
                self.raw = self.db.raw

        def copy_from_raw(self):
                cursor = self.raw.find({})
                for tweet in cursor:
                        self.insert_tweet(tweet)

        def generate_doc(self, tweet):
                doc = {}
                doc["id"] = tweet["id"]
                doc["user"] = {
                        "id": tweet["user"]["id"],
                        "name": tweet["user"]["name"],
                        "screen_name": tweet["user"]["screen_name"],
                        "description": tweet["user"]["description"],
                        "lang": tweet["user"]["lang"],
                        "location": tweet["user"]["location"]
                }
                doc["geo"] = tweet["geo"]
                doc["text"] = tweet["text"]
                doc["lang"] = tweet["lang"]
                if "retweeted_status" in tweet:
                        doc["retweeted_status"] = self.generate_doc(tweet["retweeted_status"])
                if "quoted_status" in tweet:
                        doc["quoted_status"] = self.generate_doc(tweet["quoted_status"])
                return doc
                
        def insert_tweet(self, tweet):
                sys.stderr.write(".")
                if not "user" in tweet: return True
                # Insert data
                doc = self.generate_doc(tweet)
                self.tweets.insert(doc)
                return True

        def parse_json(self, data):
                tweet = json.loads(data)
                if not "user" in tweet: return True
                self.raw.insert(tweet)
                self.insert_tweet(tweet)
