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

import sys
import json

from util import log

# This is a basic listener that just prints received tweets to stdout.
class WatchListener(StreamListener):
  def on_data(self, data):
    tweet = json.loads(data)
    if not "user" in tweet: return True
    if not "text" in tweet: return True
    print("User: ", tweet["user"]["name"])
    print("Description: ", tweet["user"]["description"])
    print("Tweet: ", tweet["text"])
    print("------------------------------------------------------------")
    return True

  def on_error(self, status):
    log("Error: ", status)
