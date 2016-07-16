import praw
import gmail


def reddit_login():
    r = praw.Reddit(user_agent="Finding monitor sales by /u/nosas")
    # r.login = ("lol_persia", "nice89")
    return r


def gmail_login():
    gm = gmail.GMail('nosas.bot@gmail.com', 'BoT#69Pass')
    gm.connect()
    return gm