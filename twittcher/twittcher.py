from __future__ import print_function

import os
import time
import pickle
from urllib import urlopen
import smtplib
from bs4 import BeautifulSoup

class Tweet:
    """ A class to make tweets from HTML data.
    
    Finds tweet.text, tweet.username, tweet.date, tweet.link
    from the HTML attributes of the tweet.

    See PageWatcher.get_new_tweets() to understand how it's used.
    """
    
    def __init__(self, text, attrs):
        self.text = text.encode('utf8')
        self.username = (attrs["href"].split("/")[1]).encode('utf8')
        self.date = attrs['title'].encode('utf8')
        self.link = ("https://twitter.com" + attrs["href"]).encode('utf8')
    
    def __eq__(self, other):
        """ Two tweets are the same if they have the same address."""
        return self.link == other.link

    def __str__(self):
        return ("\n".join(["%(text)s",
                           "  Author: %(username)s",
                           "  Date: %(date)s",
                           "  Link: %(link)s"])%self.__dict__)


class PageWatcher:
    """ General class for (username/search) page watchers """
    
    def __init__(self, action, database=None):
        
        self.action = action
        self.database = database
        
        if (database is not None) and os.path.exists(database):
            with open(database, 'r') as f:
                self.seen_tweets = pickle.load(f)
        else:
            self.seen_tweets = []
            

    def get_new_tweets(self):
        """ Go watch the page, return all new tweets. """

        url = urlopen(self.url)
        page = BeautifulSoup( url )
        url.close()
        
        texts = [p.text for p in page.findAll("p")
                 if ("class" in p.attrs) and
                 (self.p_class in p.attrs["class"])]
        
        attrs = [a.attrs for a in page.findAll("a")
                 if ("class" in a.attrs) and
                 (self.a_class in a.attrs["class"])]
        
        tweets = [Tweet(txt, a) for (txt, a) in zip(texts, attrs)]
        new_tweets = [t for t in tweets if t not in self.seen_tweets]

        self.seen_tweets += new_tweets

        if self.database is not None:
            with open(self.database, "w+") as f:
                pickle.dump(self.seen_tweets, f,
                            protocol = pickle.HIGHEST_PROTOCOL)
        
        return new_tweets

    def watch(self):

        for new_tweet in self.get_new_tweets():
            self.action(new_tweet)

    def watch_every(self, seconds):

        while True:
            self.watch()
            time.sleep(seconds)



class UserWatcher(PageWatcher):
    """ Gets tweets from a user page.

    >>> from twittcher import UserWatcher
    >>> def my_action(tweet):
            if tweet.username == "JohnDCook":
                print(tweet)
    >>> bot=UserWatcher("JohnDCook", action=my_action)
    >>> bot.watch_every(120)
    """

    def __init__(self, username, action=print, database=None):
        PageWatcher.__init__(self, action, database)
        self.url = "https://twitter.com/"+username
        self.username = username
        self.p_class = "ProfileTweet-text" 
        self.a_class = "ProfileTweet-timestamp"



class SearchWatcher(PageWatcher):
    """ Gets tweets from a search page.

    Examples:
    ---------

    >>> from twittcher import SearchWatcher
    >>> bot=SearchWatcher("milk chocolate")
    >>> # watch every 120s. Print all new tweets.
    >>> bot.watch_every(120)
    
    """
    
    def __init__(self, search_term, action=print, database=None):
        PageWatcher.__init__(self, action, database)
        self.url ="https://twitter.com/search?f=realtime&q="+search_term
        self.search_term = search_term
        self.p_class = "tweet-text"
        self.a_class = "tweet-timestamp"



class TweetSender:
    """ A class to make it easy to send tweets per email.

    Examples:
    ---------
    >>> from twittcher import TweetSender, SearchWatcher
    >>> sender = TweetSender(smtp="smtp.gmail.com", port=587,
                         login="mr.zulko@gmail.com",
                         password="fibo112358",
                         address="mr.zulko@gmail.com",
                         name = "milk chocolate")
    >>> bot = SearchWatcher("milk chocolate", action= sender.send)
    >>> bot.watch_every(600)
    """

    def __init__(self, smtp, port, login, password, to_addrs=None,
                 from_addrs="twittcher@noanswer.com", sender_id=""):
        # Configure the smtp, store email address
        if to_addrs is None:
            to_addrs = login
        self.server = smtplib.SMTP(smtp, port)
        self.server.starttls()
        self.server.login(login, password)
        self.to_addrs = to_addrs
        self.from_addrs = from_addrs
        self.sender_id = sender_id


    def make_message(self, tweet):
        return ("\n".join(["From: <%(from_addrs)s>",
                           "To: <%(to_addrs)s>",
                           "Subject: Twittcher[ %(sender_id)s ]: New tweet !",
                           "", str(tweet)]))%(self.__dict__)


    def send(self, tweet):
        self.server.sendmail(self.from_addrs, self.to_addrs,
                             self.make_message(tweet))
