// Utility functions

var randomTweet = function () { i = db.tweets.count(); j = Math.floor(Math.random() * i); return db.tweets.find({}).skip(j).limit(1); }
