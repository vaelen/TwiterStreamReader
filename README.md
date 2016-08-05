# TwiterStreamReader
A python script for reading a twitter stream into MongoDB

You'll need to copy twitter.example.cfg to twitter.cfg and set the values in it to use the tool.

Example Usage:
```bash
# Obtain all tweets about specific topics:
./ingest_twitter_data.py trump clinton republican democrat esperanto brexit '#esperanto'

# Obtain a random sampling of all tweets: 
./ingest_twitter_data.py sample
```
