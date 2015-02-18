__author__ = 'babya_000'
import twitter
import re
import json
import sys
from prettytable import PrettyTable

with open("settings.ini") as f:
    lines = f.readlines()
    CONSUMER_KEY = re.search("=\s*'(.*)'", lines[0]).group(1)
    CONSUMER_SECRET = re.search("=\s*'(.*)'", lines[1]).group(1)
    OAUTH_TOKEN = re.search("=\s*'(.*)'", lines[2]).group(1)
    OAUTH_TOKEN_SECRET = re.search("=\s*'(.*)'", lines[3]).group(1)

auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                           CONSUMER_KEY, CONSUMER_SECRET)

twitter_api = twitter.Twitter(auth=auth)
print twitter_api
#
WORLD_WOE_ID = 1
US_WOE_ID = 23424977

if len(sys.argv) > 1:
    q = sys.argv[1]
    print "Searching " + q
else:
    q = raw_input("Write Your Twit=")

i = 1
Filelife = True
while Filelife is True:
    Filelife = True
    try: myfile = open('Test(' + str(i) + str(q) + ').dat', 'r+')
    except IOError: Filelife = False
    if Filelife is True:
        i += 1
        continue
    print i
myfile = open('Test(' + str(i) + str(q) + ').dat', 'w+')
tweets_file = open("tweets_bodies.txt", "w+")
table_file = open("tweets_table.txt", "w+")

# See https://dev.twitter.com/docs/api/1.1/get/search/tweets
count = 10
search_results = twitter_api.search.tweets(q=q, count=count) #, result_type="popular")

statuses = search_results['statuses']

for _ in range(50):
    print "Length of statuses", len(statuses)
    try:
        next_results = search_results['search_metadata']['next_results']
    except KeyError, e: # No more results when next_results doesn't exist
        break

    kwargs = dict([ kv.split('=') for kv in next_results[1:].split("&") ])

    search_results = twitter_api.search.tweets(**kwargs)
    statuses += search_results['statuses']

print >> tweets_file, json.dumps(statuses, indent=1)
print "Found " + `len(statuses)` + " tweet objects"
# informace pro twitter, jak
retweet_uniq_text = {}
count = 0
retweets = []
for status in statuses:
    count += 1
    key = status['text']
    if status.has_key('retweeted_status') and not retweet_uniq_text.has_key(key):
        if "Mon Feb 16 " not in status['created_at']:
            pass
        retweet_uniq_text[key] = 1
        retweets.append([status['retweet_count'],
             status['retweeted_status']['user']['screen_name'],
             status['text'],
             status['id'],
             status['created_at']])

print "Found " + `len(retweets)` + " retweets"
twitter_highest_retweets = {}
# 5 first max retweets
sorted_retweets = sorted(retweets, reverse=True)[:5]
retweets_ids = []
# create array with ids
for item in sorted_retweets:
    retweets_ids.append(int(item[3]))

#find corresponding tweets
tweets_5max = [None]*5
for status in statuses:
    tweet_id = int(status['id'])
    if tweet_id in retweets_ids:
        index = retweets_ids.index(tweet_id)
        tweets_5max[index] = status

for status in tweets_5max:
    if status:
        myfile.write(json.dumps(status, indent = 1))

if not len(statuses):
    print "No tweets found"
    exit(-1)

myfile.write(json.dumps(statuses[0], indent=1))

screen_names = [ user_mention['screen_name']
                 for status in statuses
                   for user_mention in status['entities']['user_mentions'] ]

hashtags = [ hashtag['text']
             for status in statuses
                 for hashtag in status['entities']['hashtags'] ]
# PrettyTalbe = z informace , top 5 twittu
pt = PrettyTable(field_names=['Count', 'Screen Name', 'Text', 'Id', 'Time'])
[ pt.add_row(row) for row in sorted(retweets, reverse=True)[:5] ]
pt.max_width['Text'] = 60
pt.align= 'l'
print >>table_file, pt

if True:
    exit(0)

world_trends = twitter_api.trends.place(_id=WORLD_WOE_ID)
us_trends = twitter_api.trends.place(_id=US_WOE_ID)
print json.dumps(world_trends, indent=1)
print
print json.dumps(us_trends, indent=1)

status_texts = [ status['text']
                 for status in statuses ]
words = [ w
          for t in status_texts
              for w in t.split() ]

# ..
print
print 'status:'
print json.dumps(status_texts[0:5], indent=1)
print
print 'names:'
print json.dumps(screen_names[0:5], indent=1)
print
print 'hashtags:'
print json.dumps(hashtags[0:5], indent=1)
print json.dumps(words[0:5], indent=1)
from collections import Counter

for item in [words, screen_names, hashtags]:
    c = Counter(item)
    print c.most_common()[:4] # top 4
    print
