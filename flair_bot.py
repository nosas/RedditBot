import time
import praw


no_flairs = []
removed_submissions = []



def login(r):
    r.login("the_flair_bot", "pass", disable_warning=True)
    return r


def main():
    r = praw.Reddit(user_agent="A flair mod by /u/nosas for /r/NosasFlairTest")
    subreddit = r.get_subreddit("NosasFlairTest")

    for submission in subreddit.get_new():
        if submission.author_flair_text is not None: # link_flair_text for submission flairs
            author = submission.author

            login(r)
            r.send_message(author, "You need a flair.", "Your post has been removed until you've put on a flair")
            removed_submissions.append(submission)
            submission.remove()

main()
