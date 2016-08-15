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

from pymongo import MongoClient

from tweet_helper import TweetHelper

if __name__ == '__main__':
        h = TweetHelper()
        h.copy_from_raw()
