"""
Author: Sason R Baghdadi
Purpose: Check new submissions on Reddit.com/TeenWolf for users without flairs

Actions required to implement:
    1. Python 2.7 (Haven't tested it on Python 3.x yet)
    2. A Reddit account with moderator permission on your subreddit.
        2a. The account will need at least 2 link karma in order to bypass CAPTCHA requirements.
    3. The PRAW module will need to be installed on the machine running this script.
        3a. PRAW can be found here: https://praw.readthedocs.org/en/latest/
            Don't know how to install Python modules on Windows? Watch this: http://www.youtube.com/watch?v=ddpYVA-7wq4
"""
import time
from datetime import datetime
import praw
from Projects.RedditBot.login import reddit_bot_login

"""
TODO:
    - Create functionality for users to reply to bot and ask for a specific flair
    - Add signature to bot's post
    - Add customizable bot options for potential future users/developers?
    - Allow bot to run for certain # of cycles, then clean memory after # of cycles to prevent eating of memory??
"""

# Global variables, designed to be customizable for user
# SUBREDDIT_NAMES = "MotoGPHighlights+NosasFlairTest"
SUBREDDIT_NAMES = "TeenWolf+Voltron"

removed_submissions_filename = "removed_submissions.txt"
processed_submissions_filename = "processed_submissions.txt"

remove_post_subject = "Your post requires a link flair."
remove_post_body = "[Your recent post]({url}) in /r/{subreddit} does not have any link flair and has been removed. " \
                    "Please add a link flair to the post and [message the moderators with this message.]({msg})"

remove_comment_text = "/r/{subreddit} requires you to flair your submissions! This submission has been automatically " \
                      "removed but will be re-approved (and this comment deleted) once proper flair has been assigned."\
                      "\n\n To add flair, open your submission and click the button labeled \"flair\" beneath your" \
                      " title. From the menu, select the most appropriate category, and then hit save. You do not need"\
                      "to delete or re-submit your post!" \
                      "\n\n Don't blame me. I'm just a bot."


mod_mail_subject = "Flair Added"


class Bot:

    def __init__(self):
        # Initialize Reddit
        self.r = praw.Reddit(user_agent="A flair mod by /u/nosas for /r/NosasFlairTest")
        print "Logging in ...\n"
        reddit_bot_login(self.r)
        self.subreddits = self.r.get_subreddit(SUBREDDIT_NAMES)

        # Global variables to keep track of submissions that are removed/resolved
        self.removed_submissions = self.read_submission_list_from_file(removed_submissions_filename)
        self.processed_submissions = self.read_submission_list_from_file(processed_submissions_filename)

    # Grab the 10 most recent posts on the subreddit and check the submissions for flairs
    def check_new_submissions(self):
        # Grab the 10 most recent submissions
        print "    Getting new submissions ..."
        for submission in self.subreddits.get_new(limit=10):
            # If the current post hasn't been processed yet, then see if the OP has a flair
            if submission.id not in self.processed_submissions:
                # If OP has no flair, remove submission, notify user of removal, and add ID to removed_submission list
                if submission.link_flair_text is None:
                    # Make sure the author of the post isn't [deleted]
                    try:
                        author = submission.author
                        if author is None:
                            raise AttributeError
                    except AttributeError:
                        # Author is deleted. Disregard post.
                        continue

                    # Delete the post and add the ID to the removed_submissions list
                    submission.remove()
                    print "    Removed submission: {0}".format(submission)
                    self.removed_submissions.append(submission.id)
                    # Notify user why their post was deleted
                    submission.add_comment(remove_comment_text.format(subreddit=submission.subreddit))
                    print "        Posted removal comment"

        print "    Finished new submissions"

    # Check the removed submissions to see if they've added flairs yet. If they have, then approve the submission.
    def check_removed_submissions(self):
        # Check each post from the removed_submissions list for flairs
        for submission_id in self.removed_submissions:
            # Retrieve the submission with the submission_id from removed_list
            submission = self.r.get_submission(submission_id=submission_id)

            # If OP has a flair now, approve their post, add the ID to processed_submissions list, remove bot comment
            # This will prevent it from being processed/removed again.
            if submission.link_flair_text is not None:
                submission.approve()
                print "    Approved submission: {0}".format(submission)
                for comment in submission.comments:
                    if str(comment.author) == "the_flair_bot":
                        comment.delete()
                        print "        Deleted removal comment"
                self.processed_submissions.append(submission_id)

        print "    Finished removed submissions"

    @staticmethod
    # Method to create a URL that the user can easily send to mods' mailboxes to access their removed submission
    def create_mod_mail_url(submission):
        mod_mail_url = "http://www.reddit.com/message/compose/?to=/r/{0}&subject={1}&message={2}"\
                        .format(submission.subreddit, mod_mail_subject, submission.url)
        return mod_mail_url

    # Will remove IDs from removed_submissions list if they've been processed/approved
    def update_removed_submissions(self):
        new_removed_submissions = [item for item in self.removed_submissions if item not in self.processed_submissions]
        self.removed_submissions = new_removed_submissions

    @staticmethod
    # Opens a file and reads the list from it in order to retrieve the removed/processed_submissions list
    def read_submission_list_from_file(submissions_file):
        try:
            with open(submissions_file, 'r') as f:
                try:
                    # Read file. If text inside is a list, proceed. Else, raise error and default the variable to list.
                    submissions_list = eval(f.read())
                    if not isinstance(submissions_list, list):
                        raise SyntaxError
                except SyntaxError:
                    submissions_list = []
        # If the file doesn't exist, then create it
        except IOError:
            open(submissions_file, 'w').close()
            submissions_list = []

        return submissions_list

    @staticmethod
    # Write the removed/processed_submissions to their
    def write_submissions_list_to_file(submissions_list, submissions_file):
        with open(submissions_file, 'w') as f:
            f.write(str(submissions_list))

    def run(self):
        print "Checking new submissions ..."
        self.check_new_submissions()

        print "Checking removed submissions ..."
        self.check_removed_submissions()

        # TODO: Move the following 3 commands into check_removed_submissions method
        # No need for them all to be in the run method
        print "Updating removed submissions list ..."
        self.update_removed_submissions()

        print "Writing processed submissions to file ..."
        self.write_submissions_list_to_file(self.processed_submissions, processed_submissions_filename)

        print "Writing removed submissions to file ..."
        self.write_submissions_list_to_file(self.removed_submissions, removed_submissions_filename)

# Master bot process
if __name__ == '__main__':
    reddit_bot = Bot()
    while True:
        print('{:%H:%M:%S %b %d %Y}'.format(datetime.now()))
        try:
            reddit_bot.run()
            print("Sleeping for 10 minutes\n")
            print "= = " * 10
            time.sleep(60*10)
        except:
            # In rare cases where internet or RPi die turn off
            time.sleep(60*10)
