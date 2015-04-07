__author__ = 'babya_000'
import twitter
import re
import json
import sys
import  Tkinter as tk
import threading
import time
import Queue
import ttk
from datetime import datetime
from prettytable import PrettyTable
from Tkinter import *
import tkMessageBox


class Application(Frame):
   def selection(self):
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

        count = int(self.var.get())
        if len(sys.argv) > 1:
            q = sys.argv[1]
            if len(sys.argv) > 2:
                count = sys.argv[2]
            print "Searching {0} {1} times".format(q, count)
        else:
            q = self.WRITING.get()

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
        search_results = twitter_api.search.tweets(q=q, count=count) #, result_type="popular")

        statuses = search_results['statuses']
        self.running = True
        for _ in range(int(self.multipvar.get())):

            print "Length of statuses", len(statuses)
            msg = "Length of statuses %s" % len(statuses)
            self.queue.put(msg)
            try:
                next_results = search_results['search_metadata']['next_results']
            except KeyError, e: # No more results when next_results doesn't exist
                break

            kwargs = dict([ kv.split('=') for kv in next_results[1:].split("&") ])

            search_results = twitter_api.search.tweets(**kwargs)
            statuses += search_results['statuses']
        self.running = False
        print >> tweets_file, json.dumps(statuses, indent=1)
        print "Found " + `len(statuses)` + " tweet objects"
        # informace pro twitter, jak
        retweet_uniq_text = {}
        retweets = 0
        retweets_dict = {}
        for status in statuses:
            tweet_date = datetime.strptime(status['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            tweet_dt = tweet_date.strftime("%Y-%m-%d")
            key = status['text'] + tweet_dt
            if not status.has_key('retweeted_status'):
                continue
            if not retweet_uniq_text.has_key(key):
                retweets = 1
                retweet_uniq_text[key] = True
                tweet = [status['retweet_count'],
                     status['retweeted_status']['user']['screen_name'],
                     status['text'],
                     status['id'],
                     status['created_at'],
                     retweets]
                if retweets_dict.has_key(tweet_dt):
                    retweets_dict[tweet_dt].append(tweet)
                else:
                    retweets_dict[tweet_dt] = [tweet]
            else:
                for index, atweet in enumerate(retweets_dict[tweet_dt]):
                    if atweet[2] == status['text']:
                        retweets_dict[tweet_dt][index][5] += 1
        twitter_highest_retweets = {}
        # 5 first max retweets
        sorted_retweets = {}
        retweets_ids = []
        for k, value in retweets_dict.iteritems():
            max_5retweets = sorted(value, key=lambda i: i[5], reverse=True)[:5]
            sorted_retweets[k] = max_5retweets
            # create array with ids
            for item in max_5retweets:
                retweets_ids.append(int(item[3]))

        #find corresponding tweets
        tweets_5max = []
        for status in statuses:
            tweet_id = int(status['id'])
            if tweet_id in retweets_ids:
                index = retweets_ids.index(tweet_id)
                tweets_5max.append(status)

        for status in tweets_5max:
            if status:
                myfile.write(json.dumps(status, indent = 1))

        if not len(statuses):
            print "No tweets found"
            exit(-1)

        screen_names = [ user_mention['screen_name']
                         for status in statuses
                           for user_mention in status['entities']['user_mentions'] ]

        hashtags = [ hashtag['text']
                     for status in statuses
                         for hashtag in status['entities']['hashtags'] ]
        # PrettyTalbe = z informace , top 5 twittu
        pt = PrettyTable(field_names=['Count', 'Screen Name', 'Text', 'Id', 'Time', 'Today'])
        for key, value in sorted_retweets.iteritems():
            print "Max retweets {0} for date {1}".format(len(value), key)
            for row in value:
                pt.add_row(row)

        pt.max_width['Text'] = 60
        pt.align= 'l'
        print >>table_file, pt
        tkMessageBox.showinfo( "Best 5", pt)
   def createWidgets(self):
       self.CANCEL = Button(self, bg = "red", fg = "blue")
       self.CANCEL["text"] = "Quit"
       self.CANCEL["command"] = self.quit
       self.CANCEL.grid(row = 1 , column = 1)

       self.RUN = Button(self)
       self.RUN["text"] = "Start"
       self.RUN["fg"] = "blue"
       self.RUN["command"] = self.selection
       self.RUN.grid(row = 1, column = 2)
       self.var = DoubleVar()
       self.multipvar = DoubleVar()

       self.TWEETS = Scale(self)
       self.TWEETS["variable"] = self.var
       self.TWEETS.grid(row = 1, column = 3)

       self.MULTITWEETS = Scale(self)
       self.MULTITWEETS["variable"] = self.multipvar
       self.MULTITWEETS.grid(row = 1, column = 4)

       self.WORDS = Label(self)
       self.WORDS["text"] = "Write your tweet"
       self.WORDS.grid(row = 1, column = 5)

       self.WRITING = Entry(root, bd =5)
       self.WRITING.grid(row = 1, column = 6)
   def __init__(self, master = NONE):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
        self.queue = Queue.Queue()
        self.gui = GuiPart(master, self.queue)
        threading.Thread(target=self.selection).start()
        self.periodicCall()
   def periodicCall(self):
        self.gui.processIncoming()
        if self.running:
            self.master.after(10, self.periodicCall)
class GuiPart:
    def __init__(self, master, queue):
        self.queue = queue
        self.pgBar = ttk.Progressbar(master, orient='horizontal',
                                     length=300, mode='determinate')
        self.lb = tk.Listbox(master, width=20, height=5)
        self.pgBar.grid(padx=20, pady=20)
        self.lb.grid(row=1, column=0, padx=20, pady=20)
    def processIncoming(self):
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                self.lb.insert('end', msg)
                self.pgBar.step(25)
            except Queue.Empty:
                pass

root = Tk()
app = Application(master=root)
app.size()
app.master.title("My 10/10 Application")
app.master.minsize(360,240)
app.mainloop()
root.destroy()