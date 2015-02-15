__author__ = 'babya_000'
import twitter

CONSUMER_KEY = '7ZRw716JhleBwLzyfkIQIEBDD'
CONSUMER_SECRET = 'pqkuqQJ5lRFoFVnrUxdaSIakKHObSRE14AFPASaFe17HFtexB2'
OAUTH_TOKEN = '2848004787-tDRwdznCnOVgZ7aY8khliHqpXZvO8hGgYvPSsza'
OAUTH_TOKEN_SECRET = 'f5yEKyekGYJZvYEMWVC0GheZbYrE0xdaIt9S9Lg5mqqLB'

auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                           CONSUMER_KEY, CONSUMER_SECRET)

twitter_api = twitter.Twitter(auth=auth)
#https://api.twitter.com/1.1/statuses/retweets/:id.json
#twitter_api.statuses


print twitter_api
#
WORLD_WOE_ID = 1
US_WOE_ID = 23424977

import json
from prettytable import PrettyTable
#

q = raw_input("Write Your Twit=")
count = 10
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


# See https://dev.twitter.com/docs/api/1.1/get/search/tweets

search_results = twitter_api.search.tweets(q=q, count=count)

statuses = search_results['statuses']

for _ in range(10):
    print "Length of statuses", len(statuses)
    try:
        next_results = search_results['search_metadata']['next_results']
    except KeyError, e: # No more results when next_results doesn't exist
        break

    kwargs = dict([ kv.split('=') for kv in next_results[1:].split("&") ])

    search_results = twitter_api.search.tweets(**kwargs)
    statuses += search_results['statuses']
    print json.dumps(statuses[0], indent=1)


# informace pro twitter, jak
retweet_uniq_text = {}
count = 0
retweets = []
for status in statuses:
    count += 1
    key = status['text']
    retweets_today = []
    if status.has_key('retweeted_status') and not retweet_uniq_text.has_key(key):
        if "Sat Feb 14 " not in status['created_at']:
            continue
        retweet_uniq_text[key] = 1
        retweets_today[count] += 1
        retweets.append([status['retweet_count'],
             status['retweeted_status']['user']['screen_name'],
             status['text'],
             status['id'],
             status['created_at'],
             retweets_today])
status_texts = [ status['text']
                 for status in statuses ]
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
    myfile.write(json.dumps(status, indent = 1))
myfile.write(json.dumps(statuses[0], indent=1))

screen_names = [ user_mention['screen_name']
                 for status in statuses
                   for user_mention in status['entities']['user_mentions'] ]

hashtags = [ hashtag['text']
             for status in statuses
                 for hashtag in status['entities']['hashtags'] ]
# PrettyTalbe = z informace , top 5 twittu
pt = PrettyTable(field_names=['Count', 'Screen Name', 'Text', 'Id', 'Time', 'Today'])
[ pt.add_row(row) for row in sorted(retweets, reverse=True)[:5] ]
pt.max_width['Text'] = 60
pt.align= 'l'
print pt
world_trends = twitter_api.trends.place(_id=WORLD_WOE_ID)
us_trends = twitter_api.trends.place(_id=US_WOE_ID)
print json.dumps(world_trends, indent=1)
print
print json.dumps(us_trends, indent=1)


#
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
