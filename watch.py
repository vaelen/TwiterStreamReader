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

import sys
import json

reload(sys)  
sys.setdefaultencoding('utf8')

# This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
        def on_data(self, data):
                tweet = json.loads(data)
                if not "user" in tweet: return True
                if not "text" in tweet: return True
                print "User: ", tweet["user"]["name"]
                print "Description: ", tweet["user"]["description"]
                print "Tweet: ", tweet["text"]
                print "------------------------------------------------------------"
                return True

        def on_error(self, status):
                print >> sys.stderr, "Error: ", status

if __name__ == '__main__':
        
        import ConfigParser

        config = ConfigParser.RawConfigParser()
        config.read('twitter.cfg')
        
        if len(sys.argv) < 2 :
                print >> sys.stderr, "Please provide at least one topic. Use 'sample' for a random sample."
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
˚        
        if topics[0].lower() == "sample":
                print >> sys.stderr, "Looking at a random sample of tweets."
                stream.sample()
        else:
                print >> sys.stderr, "Tracking tweets with these topics: ", topics
                stream.filter(track=topics)

