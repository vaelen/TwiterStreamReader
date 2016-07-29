#!/usr/bin/env python

# Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import sys
import json

from pymongo import MongoClient

from tweet_helper import TweetHelper

if __name__ == '__main__':
        h = TweetHelper()
        # h.copy_from_raw()
