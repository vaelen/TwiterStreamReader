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

# Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import os
import sys
import json

from pymongo import MongoClient
from ingest_listener import IngestListener
from watch_listener import WatchListener
from tweet_helper import TweetHelper
from util import log

from configparser import RawConfigParser

import argparse

def parse_arguments():
  parser = argparse.ArgumentParser(description='Reads a stream of tweets from Twitter and stores them in MongoDB.',
                                   epilog='By default a random sampling of tweets will be collected and stored in two collections: "raw" and "tweets".  '
                                   + ' The "raw" collection contains the raw tweet data.  The "tweets" collection contains a subset of this data.')
  parser.add_argument('-t', '--topics', metavar='TOPIC', nargs='*', help='Track the given topics. This disables random sampling.')
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
      listener = WatchListener()
      log("Watching instead of storing tweets.")
    else:
      listener = IngestListener()
    
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
