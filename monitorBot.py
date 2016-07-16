import login
import time
import email
import datetime

r = login.reddit_login()
desired_items = ["xg270hu", "mg278q", "xl2730z"]


def run_bot():
    subreddit = r.get_subreddit('buildapcsales')
    new_submissions = subreddit.get_new(limit=5)
    print "    ---------------- Current Submissions ----------------"
    try:
        with open('cache.txt') as f:
            cacheFileData = f.readlines()
    except:
        cacheFileData = []

    for submission in new_submissions:
        print "    " + str(submission)
        foundMatch = any(string.lower() in str(submission).lower() for string in desired_items)

        if foundMatch and str(submission.id + "\n") not in cacheFileData:
            print "    ^^^^^^^^ FOUND A MATCH ^^^^^^^^^^^^^^"

            url = "https://www.reddit.com/r/buildapcsales/comments/" + str(submission.id)
            msg = email.message.Message()
            msg.set_payload(url)
            gm = login.gmail_login()
            gm.send(msg, ['sasonreza@gmail.com'])
            print "    E-mail sent"

            with open('cache.txt', 'a+') as cacheFile:
                cacheFile.write(str(submission.id) + "\n")
                print "    Added to cache\n"


while True:
    try:
        print "{:%Y-%m-%d %H:%M:%S}".format(datetime.datetime.now())
        run_bot()
        print
        print
    except:
        print "Something went wrong..."
        pass

    time.sleep(20)
