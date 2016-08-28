import time
import datetime
import praw
from login import reddit_login

"""
TODO:
    - Allow bot to run for certain # of cycles, then clean memory after # of cycles to prevent eating of memory
    - Add customizable bot options for potential future users/developers?
    - Create functionality for users to reply to bot and ask for a specific flair
"""

subreddit_name = "NosasFlairTest"
removed_submissions_filename = "removed_submissions.txt"
processed_submissions_filename = "processed_submissions.txt"

remove_post_subject = "Your post requires a flair."
remove_post_body = "[Your recent post]({0}) in /r/{1} does not have any flair and has been removed. " \
                    "Please add flair to the post and [message the moderators with this message.]({2})"

mod_mail_subject = "Flair Added"


class Bot:
    # Global variables to keep track of submissions that are removed/resolved
    removed_submissions = []
    processed_submissions = []

    # Initialize Reddit
    r = praw.Reddit(user_agent="A flair mod by /u/nosas for /r/NosasFlairTest")
    print "Logging in ...\n"
    reddit_login(r)
    subreddit = r.get_subreddit(subreddit_name)

    # Grab the 10 most recent posts on the subreddit and check the submissions for flairs
    def check_new_submissions(self):
        # Grab the 10 most recent submissions
        print "    Getting new submissions ..."
        for submission in self.subreddit.get_new(limit=10):
            # If the current post hasn't been processed yet, then see if the OP has a flair
            if submission.id not in self.processed_submissions:
                # If OP has no flair, remove submission, notify user of removal, and add ID to removed_submission list
                if submission.author_flair_text is None:
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
                    self.r.send_message(author, remove_post_subject, remove_post_body.format(
                        submission.url, subreddit_name, self.create_mod_mail_url(submission.url)))
                    print "    Sending message to author ..."

        print "    Finished new submissions"

    # Check the removed submissions to see if they've added flairs yet. If they have, then approve the submission.
    def check_removed_submissions(self):
        # Check each post from the removed_submissions list for flairs
        for submission_id in self.removed_submissions:
            # Create a url with the subreddit and post ID in order to obtain PRAW's submission object
            url = "https://www.reddit.com/r/{0}/comments/{1}".format(subreddit_name, submission_id)
            submission = self.r.get_submission(url=url)

            # If OP has a flair now, approve their post, add the ID to processed_submissions list
            # This will prevent it from being processed/removed again.
            if submission.author_flair_text is not None:
                submission.approve()
                print "    Approved submission: {0}".format(submission)
                self.processed_submissions.append(submission_id)

        print "    Finished removed submissions"

    @staticmethod
    # Method to create a URL that the user can easily send to mods' mailboxes to access their removed submission
    def create_mod_mail_url(submission_url):
        mod_mail_url = "http://www.reddit.com/message/compose/?to=/r/{0}&subject={1}&message={2}"\
                        .format(subreddit_name, mod_mail_subject, submission_url)
        return mod_mail_url

    # Will remove IDs from removed_submissions list if they've been processed/approved
    def update_removed_submissions(self):
        new_removed_submissions = [item for item in self.removed_submissions if item not in self.processed_submissions]
        self.removed_submissions = new_removed_submissions

    @staticmethod
    # Opens a file and reads the list from it in order to retrieve the removed/processed_submissions list
    def open_submissions_list(submissions_file):
        try:
            with open(submissions_file, 'r') as f:
                try:
                    # Read file. If text inside is a list, proceed. Else, raise error and default the variable to list.
                    submissions_list = eval(f.read())
                    if not isinstance(submissions_list, list):
                        raise SyntaxError
                except SyntaxError:
                    submissions_list = []
        # If it doesn't exist, then create it
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
        print "Retrieving removed submissions from file ..."
        self.removed_submissions = self.open_submissions_list(removed_submissions_filename)

        print "Retrieving processed submissions from file ..."
        self.processed_submissions = self.open_submissions_list(processed_submissions_filename)

        print "Checking new submissions ..."
        self.check_new_submissions()

        print "Checking removed submissions ..."
        self.check_removed_submissions()

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
        print('{:%H:%M:%S %b %d %Y}'.format(datetime.datetime.now()))
        reddit_bot.run()
        print("Sleeping for 10 minutes\n")
        print "= = " * 10
        time.sleep(600)
