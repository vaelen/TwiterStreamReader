#!/usr/bin/env python3
# -*- coding: utf-8; python-indent-guess-indent-offset: nil; python-indent-offset: 2; -*-

# This file is part of TwitterStreamReader.
# Copyright 2016 Andrew Young
#
# TwitterStreamReader is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TwitterStreamReader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for moAre details.
#
# You should have received a copy of the GNU General Public License
# along with TwitterStreamReader.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import json
import argparse
import dateutil.parser
import progressbar

from pymongo import MongoClient
from configparser import RawConfigParser
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

def log(*messages):
  print(*messages, file=sys.stderr)

class TweetHelper:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.twitter
        self.tweets = self.db.tweets
        self.raw = self.db.raw

    def copy_from_raw(self):
        log("Dropping Tweet Collection")
        self.tweets.drop()
        log("Creating Tweet Collection From Raw Collection")
        total = self.raw.count()
        cursor = self.raw.find({})
        i = 0
        with progressbar.ProgressBar(max_value=total) as bar:
          for tweet in cursor:
            self.insert_tweet(tweet)
            i = i + 1
            # if i % 100 == 0: sys.stderr.write("#")
            bar.update(i)

    def generate_doc(self, tweet):
        doc = {}
        doc["id"] = tweet["id_str"]
        doc["user"] = {
            "id": tweet["user"]["id_str"],
            "name": tweet["user"]["name"],
            "screen_name": tweet["user"]["screen_name"],
            "description": tweet["user"]["description"],
            "lang": tweet["user"]["lang"],
            "location": tweet["user"]["location"],
            "created_at": dateutil.parser.parse(tweet["user"]["created_at"])
        }
        doc["coordinates"] = tweet["coordinates"]
        doc["place"] = tweet["place"]
        doc["text"] = tweet["text"]
        doc["lang"] = tweet["lang"]
        doc["created_at"] = dateutil.parser.parse(tweet["created_at"])
        if "retweeted_status" in tweet:
            doc["retweeted_status"] = self.generate_doc(tweet["retweeted_status"])
        if "quoted_status" in tweet:
            doc["quoted_status"] = self.generate_doc(tweet["quoted_status"])
        return doc
                
    def insert_tweet(self, tweet):
        if not "user" in tweet: return True
        # Insert data
        doc = self.generate_doc(tweet)
        self.tweets.insert(doc)
        return True

    def parse_json(self, data):
        tweet = json.loads(data)
        if not "user" in tweet: return False
        sys.stderr.write(".")
        self.raw.insert(tweet)
        self.insert_tweet(tweet)
        return True

# This is an abstract listener that implements
class BaseListener(StreamListener):
  def __init__(self, total):
    self.i = 0
    self.total = total
      
# This is a listener that stores tweets in MongoDB
class IngestListener(BaseListener):
  def __init__(self, total):
    super().__init__(total)
    self.tweet_helper = TweetHelper()
    if total < 1:
      self.bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength,redirect_stderr=True)
    else:
      self.bar = progressbar.ProgressBar(max_value=total,redirect_stderr=True)
      
  def on_data(self, data):
    if self.tweet_helper.parse_json(data):
      self.i = self.i + 1
      self.bar.update(self.i)
    if self.total > 0 and self.i >= self.total: return False
    return True

  def on_error(self, status):
    log("Error: ", status)

# This is a listener that just prints received tweets to stdout.
class WatchListener(BaseListener):
  def __init__(self, total):
    super().__init__(total)

  def on_data(self, data):
    tweet = json.loads(data)
    if not "user" in tweet: return True
    if not "text" in tweet: return True
    self.i = self.i + 1
    print("User: ", tweet["user"]["name"])
    print("Description: ", tweet["user"]["description"])
    print("Tweet: ", tweet["text"])
    print("------------------------------------------------------------")
    if self.total > 0 and self.i >= self.total: return False
    return True

  def on_error(self, status):
    log("Error: ", status)
    
def parse_arguments():
  parser = argparse.ArgumentParser(description='Reads a stream of tweets from Twitter and stores them in MongoDB.',
                                   epilog='By default a random sampling of tweets will be collected and stored in two collections: "raw" and "tweets".  '
                                   + ' The "raw" collection contains the raw tweet data.  The "tweets" collection contains a subset of this data.')
  parser.add_argument('-t', '--topics', metavar='TOPIC', nargs='*', help='Track the given topics. This disables random sampling.')
  parser.add_argument('-m', '--max', metavar='COUNT', default=0, type=int, help='Stop after COUNT tweets.')
  parser.add_argument('-w', '--watch', action='store_true', help='Watch stream. This will print tweets to standard out instead of storing them in MongoDB.')
  parser.add_argument('-c', '--convert', action='store_true', help='Convert tweets. This will re-process all tweets in the raw collection instead of reading new tweets.')
  parser.add_argument('-f', '--config', metavar='FILE', default='twitter.cfg', help='Config file. Default: twitter.cfg')
  return parser.parse_args()
  
def main():

  options = parse_arguments()

  if options.convert:
    h = TweetHelper()
    h.copy_from_raw()
  else:
    if not os.path.isfile(options.config):
      log("Config file not found: ", options.config)
      exit(1)
      
    config = RawConfigParser()
    config.read(options.config)
  
    # Variables that contains the user credentials to access Twitter API
    access_token = config.get("Twitter", "access_token")
    access_token_secret = config.get("Twitter", "access_token_secret")
    consumer_key = config.get("Twitter", "consumer_key")
    consumer_secret = config.get("Twitter", "consumer_secret")

    # Determine which listener to use
    listener = None
    if options.watch:
      listener = WatchListener(options.max)
      log("Watching instead of storing tweets.")
    else:
      listener = IngestListener(options.max)
    
    # This handles Twitter authetification and the connection to Twitter Streaming API
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, listener)

    if options.topics:
      log("Tracking tweets with these topics: ", options.topics)
      stream.filter(track=options.topics)
    else:
      log("Reading a random sample of tweets.")
      stream.sample()

if __name__ == '__main__': main()
