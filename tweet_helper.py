#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

# Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import dateutil.parser
import json
import sys

from pymongo import MongoClient

class TweetHelper:
        def __init__(self):
                self.client = MongoClient()
                self.db = self.client.twitter
                self.tweets = self.db.tweets
                self.raw = self.db.raw

        def copy_from_raw(self):
                print >> sys.stderr, "Dropping Tweet Collection"
                self.tweets.drop()
                print >> sys.stderr, "Creating Tweet Collection From Raw Collection"
                cursor = self.raw.find({})
                i = 0
                for tweet in cursor:
                        self.insert_tweet(tweet)
                        i = i + 1
                        if i % 100 == 0: sys.stderr.write("#")

        def generate_doc(self, tweet):
                doc = {}
                doc["id"] = tweet["id"]
                doc["user"] = {
                        "id": tweet["user"]["id"],
                        "name": tweet["user"]["name"],
                        "screen_name": tweet["user"]["screen_name"],
                        "description": tweet["user"]["description"],
                        "lang": tweet["user"]["lang"],
                        "location": tweet["user"]["location"],
                        "created_at": dateutil.parser.parse(tweet["user"]["created_at"])
                }
                doc["geo"] = tweet["geo"]
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
                if not "user" in tweet: return True
                sys.stderr.write(".")
                self.raw.insert(tweet)
                self.insert_tweet(tweet)
