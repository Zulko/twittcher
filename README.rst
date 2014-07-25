Twittcher
==========

Twittcher (for *Twitter-watcher*) is a Python module to make bots that will watch a Twitter user page or search page, and react to the tweets.

It's simple, small (currently ~150 lines of code), and requires no account on Twitter or Twitter.dev. (it doesn't use the Twitter API, it directly parses the HTML).

Twittcher is an open-source software originally written by Zulko_, and released under the MIT licence. The project is hosted on Github_, where you can report bugs, propose impovements, etc.

Install
--------

If you have `pip`, install twittcher by typing in a terminal:
::
    (sudo) pip install twittcher

Else, download the sources (on Github_ or PyPI_), and in the same directory as the `setup.py` file, type this in a terminal:
::
    (sudo) python setup.py install

Twittcher requires the Python package bs4 (a.k.a. BeautifulSoup), which will be automatically installed when twittcher is installed.


Examples of use
----------------

For the moment there is no documentation for Twittcher (other than the docstrings of the functions) but the following examples will show everything you need to get started.

1. Print the tweets of a given user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every 120 seconds, print all the new tweets by John D. Cook:
::
    from twittcher import UserWatcher
    UserWatcher("JohnDCook").watch_every(120)

Result:
    
The default action of `UserWatcher` is to print the tweets, but you can ask any other action instead.
For instance, here is how to print only the tweets that are actually written by John D. Cook (not his retweets):
::
    from twittcher import UserWatcher
    
    def my_action(tweet):
        if tweet.username == "JohnDCook":
            print(tweet)

    UserWatcher("JohnDCook", action=my_action).watch_every(120)


2. Control a distant machine through Twitter !
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every 60 seconds, for any of my new tweets of the form `cmd: my_command`, run `my_command` in a terminal.
When this script is running on a computer, I can control that computer using tweets !
::
    import subprocess
    from twittcher import UserWatcher

    def my_action(tweet):
        """ Execute the tweet's command, if any. """
        if tweet.text.startswith("cmd: "):
            subprocess.Popen( tweet.text[5:].split(" ") )

    # Watch my account and react to my tweets
    bot = UserWatcher("Zulko___", action=my_action)
    bot.watch_every(60)

For instance, the tweet `cmd: firefox` will open Firefox on the computer, and the tweet `cmd: youtube-dl FNf-IGmxElI` will ask the computer to download this video of a tiny hamster eating a tiny pizza.


3. Watch search results and send alert mails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every 600 seconds, send me all the new tweets in the Twitter search results for `chocolate milk`.
::
    from twittcher import TweetSender, SearchWatcher

    sender = TweetSender(smtp="smtp.gmail.com", port=587,
                         login="mr.zulko@gmail.com",
                         password="fibo112358",
                         address="mr.zulko@gmail.com",
                         name = "chocolate milk")

    bot = SearchWatcher("chocolate milk", action= sender.send)
    bot.watch_every(600)


4. Multibot watching
~~~~~~~~~~~~~~~~~~~~~~~~

If you want to run several bots at once, make sure that you leave a few seconds between the requests of the different bots.
Here is how you print the new tweets of John D. Cook, Mathbabe, and Eolas. Each of them is watched every minute, with 20 seconds between the requests of two bots:
::
    import time
    import itertools
    from twittcher import UserWatcher
    
    bots = [ UserWatcher(user) for user in 
             ["JohnDCook", "mathbabedotorg",  "Maitre_Eolas"]]

    for bot in itertools.cycle(bots):
        bot.watch()
        time.sleep(20)


5. Saving the tweets
~~~~~~~~~~~~~~~~~~~~~~

A bot can save to a file the tweets that it has already seen, so that in future sessions it will remember not to process these tweets again, in case they still appear on the watched page.
::
    from twittcher import SearchWatcher
    bot = SearchWatcher("chocolate milk", database="choco.db")
    bot.watch_every(20)



.. _PyPI: https://pypi.python.org/pypi/twittcher
.. _Zulko : https://github.com/Zulko
.. _Github: https://github.com/Zulko/twittcher