import time
import praw
from login import reddit_login

"""
TODO:
    # - Figure out how to approve posts
    # - Create message outline to send to user (probably copy from old flair bot)
    # - Add some proper documentation
    # - Push to GitHub/fix Repo
    - Need cleaner, more informative documentation
    - Fix the removal of post IDs from removed_submissions list
    - Automate the process
    - Add customizable bot options for potentional future users
"""

subreddit_name = "NosasFlairTest"

add_flair_subject = ""
add_flair_body = ""

remove_post_subject = "Your post requires a flair."
remove_post_body = "[Your recent post]({0}) in /r/{1} does not have any flair and has been removed. " \
                    "Please add flair to the post and [message the moderators]({2}) with a link to your post."

mod_mail_subject = "Flair Added"
mod_mail_body = "Replace this text with your post's url."


class Bot():
    # Global variables to keep track of submissions that are removed/resolved
    removed_submissions = []
    finished_submissions = []

    # Initialize Reddit
    r = praw.Reddit(user_agent="A flair mod by /u/nosas for /r/NosasFlairTest")
    reddit_login(r)
    subreddit = r.get_subreddit(subreddit_name)

    # Grab the 10 most recent posts on the subreddit and check the submissions for flairs
    def check_new_submissions(self):
        # Grab the 10 most recents submissions
        for submission in self.subreddit.get_new(limit=1):
            print "---" * 6
            print submission

            # If the current post hasn't been processed yet, then see if the OP has a flair
            if submission.id not in self.finished_submissions:
                # If OP has no flair, remove submission, notify user of removal, and add ID to removed_submission list
                #TODO: Change to None instead of not None
                if submission.author_flair_text is not None:
                    author = submission.author
                    #TODO: Send a more elegant message
                    self.r.send_message(author, remove_post_subject, remove_post_body.format(
                        submission.url, subreddit_name, self.create_mod_mail_url(submission.url)
                    ))
                    # self.r.send_message(author, "Post removed.", "Your post has been removed until you've put on a flair")
                    submission.remove()
                    self.removed_submissions.append(submission.id)
                    print "Removed {0} \n ID: {1}".format(submission.title, submission.id)

    # Check the removed submission to see if they've added flairs yet
    # If they have, then approve the submission.
    def check_removed_submissions(self):
        # Check each post from the removed_submissions list for flairs
        for submission_id in self.removed_submissions:
            # Create a url with the subreddit and post ID in order to obtain PRAW's submission object
            url = "https://www.reddit.com/r/{0}/comments/{1}".format(subreddit_name, submission_id)
            submission = self.r.get_submission(url=url)

            print "---" * 6
            print submission

            # If OP has a flair now, approve their post, add the ID to finished_submissions list
            # This will prevent it from being processed/removed again.
            #TODO: Change to None instead of not None
            if submission.author_flair_text is not None:
                submission.approve()
                self.finished_submissions.append(submission_id)
                print "Approved " + str(submission)

    def create_mod_mail_url(self, post_url):
        mod_mail_url = "http://www.reddit.com/message/compose/?to=/r/{0}&subject={1}&message={2}"\
                        .format(subreddit_name, mod_mail_subject, mod_mail_body)
        remove_post_message = "[Your recent post]({0}) in /r/{1} still does not have any flair and has been removed. " \
                              "Please add flair to the post and [message the moderators]({2}) with a link to your post."\
                              .format(post_url, subreddit_name, mod_mail_url)
        return mod_mail_url

    def run(self):
        self.check_new_submissions()
        self.check_removed_submissions()


# Master bot process
if __name__ == '__main__':
    reddit_bot = Bot()

    reddit_bot.run()


# main()
#
#
# new_removed_submissions = [item for item in removed_submissions if item not in finished_submissions]
# removed_submissions = new_removed_submissions
# print "Finished : " + str(finished_submissions)
# print "New List : " + str(new_removed_submissions)
# print "Removed  : " + str(removed_submissions)
