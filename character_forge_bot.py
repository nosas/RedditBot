"""
Author: Sason R Baghdadi
Purpose: Weekly posting script for Reddit.com/r/CharacterForge

Actions required to implement:
    1. Python 2.7 (Haven't tested it on Python 3.x yet)
    2. A Reddit account with moderator permission on your subreddit.
        2a. The account will need at least 2 link karma in order to bypass CAPTCHA requirements.
    3. The PRAW module will need to be installed on the machine running this script.
        3a. PRAW can be found here: https://praw.readthedocs.org/en/latest/
            Don't know how to install Python modules on Windows? Watch this: http://www.youtube.com/watch?v=ddpYVA-7wq4
"""

import praw
from datetime import date
import random
# TODO: Remove this import
from login import reddit_login

# TODO: Remove the following block of TODO list
"""
# - Learn how to create a sticky/announcement post
#     + Then comment on the newly created sticky/announcement
# - Choose between text file and keeping list within (Text file for sure)
# - Randomly select 2 names from a list
# - Keep track of match-ups to prevent duplicate match-ups after X amount of time
# - Read and write previous match-ups to file
# - Submit the current matchup in the post's title/body
# - Add more documentation
# - Clean up clutter
# - Allow for customization in text

v1.0 is (nearly) finished!
"""

# Global variables, set to be customizable for user
USERNAME = ""
PASSWORD = ""
SUBREDDIT_NAME = "CharacterForge"

# Alternative Titles Weekly Showdown #1: NAME1 v NAME2
# submission_title = "Weekly Showdown Thread: {:%d/%m/%Y}".format(date.today())
submission_title = "Weekly Showdown #{number}: {name1} v {name2}"
# When editing the submission text, make sure to add two \n in order to create a new line on Reddit.
submission_text = "This week's match-up is {name1} v {name2}. \n\n" \
                  "{name1} is known to be ....\n\n" \
                  "{name2} is also a ... \n\n" \
                  "STAY TUNED!"

comment_text = "# **Off-topic Discussion**"

names_list_filename = "names_list.txt"
previous_matchups_filename = "previous_matchups.txt"
max_days_since_matchup = 90


class Bot:
    def __init__(self):
        self.current_matchup = []
        self.previous_matchups = self.read_previous_matchups_from_file()

        self.name1 = ""
        self.name2 = ""

        self.names_list = self.read_names_list_from_file()

        self.r = praw.Reddit(user_agent="Automatic weekly showdown posting tool for /r/CharacterForge by /u/nosas")
        print("Logging in ...\n")
        # self.r.login(USERNAME, PASSWORD)
        # TODO: Remove the following line of code
        reddit_login(self.r)
        self.subreddit = self.r.get_subreddit(SUBREDDIT_NAME)

    # Post a new stickied submission with bottom=True because we don't want to remove the first sticky.
    # Actually, the param doesn't matter. It will never replace the top, unless the top sticky is removed.
    # However, still keeping the param there for clarity.
    def post_sticky_submission(self):
        print("Posting submission ...")

        # Post a new submission. Parameters are submit(subreddit_name, post_title, post_text (aka post_body))
        # The title and text have .format(name1=, name2=) in order to replace all instances of {name1} and {name2} in
        # the strings with the appropriate names. See submission_title for an example of how to format the string.
        new_submission = self.r.submit(SUBREDDIT_NAME,
                                       submission_title.format(number=1, name1=self.name1, name2=self.name2),
                                       submission_text.format(name1=self.name1, name2=self.name2))
        print("    Finished posting submission")

        print("Stickying submission ...")
        new_submission.sticky(bottom=True)
        print("    Finished stickying submission")

        self.post_comment(new_submission)

    @staticmethod
    # Post a comment to the newly stickied post
    def post_comment(new_submission):
        # Get the Weekly Showdown submission. It will always be the bottom sticky.
        current_sticky = new_submission

        # Reply to the submission and sticky the comment too
        print("Posting stickied comment ...")
        current_sticky.add_comment(comment_text).distinguish(sticky=True)
        print("    Finished posting comment")

    # Randomly select two names from a list of names for the weekly showdown
    def create_matchup(self):

        print ("Creating match-up")
        # Randomly select two names from a list of names. Sort the two names and then store them in a list.
        # The names are sorted in order to check if the match-up is in the previous_matchups list.
        # Prevents match-ups like  "Week 1: John v Jane"   and    "Week 2: Jane v John"
        self.current_matchup = tuple(sorted(random.sample(self.names_list, 2)))
        self.name1 = self.current_matchup[0]
        self.name2 = self.current_matchup[1]

        print "    Current match-up : {0} vs. {1}".format(self.name1, self.name2)
        # Not sure how the title wants to be formatted. Will need to create a method to increment the counter.
        print "    Current title:   : " + submission_title.format(number=1, name1=self.name1, name2=self.name2)

        # If the two haven't been matched before, continue with them as the current match-up
        if self.current_matchup not in self.previous_matchups:
            self.previous_matchups[self.current_matchup] = str(date.today())

        # Else, if the two haven't matched-up for more than X amount of days, continue when them as current match-up
        elif self.days_since_matchup(self.previous_matchups[self.current_matchup]) >= max_days_since_matchup:
            print "    It's been more than {0} since previous match-up.".format(max_days_since_matchup)
            self.previous_matchups[self.current_matchup] = str(date.today())

        # Else, they've matched up in the past X days, so find another match-up
        else:
            print("    Oops! Duplicate match-up.\n    Creating another match-up ...")
            self.create_matchup()

        # Write the previous match-ups to file
        self.write_previous_matchups_to_file()

    @staticmethod
    # This method was supposed to be basic math, however things got complicated very fast once Date was stored in a dict
    # The parameter is the value from a key (a match-up) from the previous_matchups dict
    # The key is read as a string, so it's split by the delimiter ("-") and then created into a new Date object
    # The newly created Date object is then subtracted from today's date to find how long since previous match-up
    def days_since_matchup(matchup_date):
        matchup_date = matchup_date.split("-")

        matchup_date = date(int(matchup_date[0]), int(matchup_date[1][-1]), int(matchup_date[2]))
        return (date.today() - matchup_date).days

    @staticmethod
    def read_names_list_from_file():
        try:
            with open(names_list_filename, 'r') as f:
                names_list = [name.strip() for name in f.readlines()]
                return names_list
        except IOError:
            print "ERROR: Can't open/find the names_list file!"
            print "       Please verify that \"{0}\" is in the same folder as \"character_forge_bot.py\"." \
                .format(names_list_filename)
            exit(-1)

    @staticmethod
    def read_previous_matchups_from_file():
        try:
            # Try to open the file. If it doesn't exist, create the file and set previous_matchups to an empty dict
            with open(previous_matchups_filename, 'r') as f:
                try:
                    # Try to read previous_matchups from file. If it's not a dict, set it to an empty dict
                    previous_matchups = eval(f.read())
                    if not isinstance(previous_matchups, dict):
                        raise SyntaxError
                except SyntaxError:
                    previous_matchups = {}
        except IOError:
            # Create the new previous_matchups file and set previous_matchups to an empty dict
            open(previous_matchups_filename, 'w').close()
            previous_matchups = {}

        return previous_matchups

    def write_previous_matchups_to_file(self):
        with open(previous_matchups_filename, 'w') as f:
            f.write(str(self.previous_matchups))

    def run(self):
        self.create_matchup()
        print("    Finished creating match-up")
        self.post_sticky_submission()


if __name__ == '__main__':
    cf_bot = Bot()
    cf_bot.run()
