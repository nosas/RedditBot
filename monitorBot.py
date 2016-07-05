import praw
import login
import time
import gmail
import email

r = login.reddit_login()
gm = login.gmail_login()

desired_items = ["xg270hu", "mg278q", "xl2730z"]
cache = []


def run_bot():
    subreddit = r.get_subreddit('buildapcsales')
    new_submissions = subreddit.get_new(limit=5)
    print "---------- Current Submissions ----------"

    for submission in new_submissions:
        print str(submission)
        foundMatch = any(string in str(submission).lower() for string in desired_items)

        if foundMatch and submission not in cache:
            print "^^^^^^^^ FOUND A MATCH ^^^^^^^^^^^^^^"
            cache.append(submission)
            url = "https://www.reddit.com/r/buildapcsales/comments/" + str(submission.id)
            msg = email.message.Message()
            msg.set_payload(url)
            gm.send(msg, ['sasonreza@gmail.com'])
            print "E-mail sent\n"

        # for word in str(submission).split():
        #     """
        #     If the word is a desired item I'm looking for, and the current
        #     submission hasn't already been looked at, email the URL to myself.
        #     """
        #     if word.lower() in desired_items and submission not in cache:
        #         print "############got it"
        #


while True:
    try:
        print
        print "---" * 10
        print "Refreshing submissions..."
        print "Cache Size = " + str(len(cache))
        print "---" * 10
        print
        run_bot()
    except:
        print "Something went wrong..."
        pass

    time.sleep(60)
