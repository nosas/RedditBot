import praw
from datetime import date
import random
import json
from login import reddit_login

"""
TODO:
# - Learn how to create a sticky/announcement post
#     + Then comment on the newly created sticky/announcement
# - Choose between text file and keeping list within (Text file for sure)
# - Randomly select 2 names from a list
# - Keep track of match-ups to prevent duplicate match-ups after X amount of time
# - Read and write previous match-ups to file
- Submit the current matchup in the post's title/body
- Add more documentation
- Clean up clutter

- Allow for customization in text

"""

# Global variables, set to be customizable for user
subreddit_name = "nosasflairtest"

# Alternative Titles Weekly Showdown #1: NAME1 v NAME2
submission_title = "Weekly Showdown Thread: {:%d/%m/%Y}".format(date.today())

print submission_title
submission_text = ""
comment_text = "# **Off-topic Discussion**"

names_list = ["jon", "tim", "mom", "dad", "etc", "blah", "tony"]
names_list_filename = "names_list.txt"

previous_matchups_filename = "previous_matchups.txt"
max_days_since_matchup = 90


class Bot:

    current_matchup = []
    previous_matchups = {}

    # r = praw.Reddit(user_agent="Automatic showdown posting tool for /r/CharacterForge by /u/nosas")
    print("Logging in ...\n")
    # reddit_login(r)
    # subreddit = r.get_subreddit(subreddit_name)

    # Create a new stickied submission with bottom=True because we don't want to remove the first sticky
    # Actually, the param doesn't matter. It will never replace the top unless the top sticky is removed
    # However, still keeping the param there for clarity.
    def create_sticky_submission(self):
        print("Posting submission ...")
        new_submission = self.r.submit(subreddit_name, submission_title, submission_text)
        print("    Finished posting submission")

        print("Stickying submission ...")
        new_submission.sticky(bottom=True)
        print("    Finished stickying submission")

    # Post a comment to the newly stickied post
    def post_comment(self):
        current_sticky = self.subreddit.get_sticky(bottom=True)

        # Reply to the submission and sticky the comment too
        print("Posting stickied comment ...")
        current_sticky.add_comment(comment_text).distinguish(sticky=True)
        print("    Finished posting comment")

    # Randomly select two names from a list of names for the weekly showdown
    def create_matchup(self):

        print ("Creating match-up")
        self.current_matchup = tuple(sorted(random.sample(names_list, 2)))
        print "    Current match-up : {0} vs. {1}".format(self.current_matchup[0], self.current_matchup[1])

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


        self.write_previous_matchups_to_file()

    @staticmethod
    def days_since_matchup(matchup_date):
        matchup_date = matchup_date.split("-")

        matchup_date = date(int(matchup_date[0]), int(matchup_date[1][-1]), int(matchup_date[2]))
        return (date.today() - matchup_date).days

    def read_previous_matchups_from_file(self):
        try:
            with open(previous_matchups_filename, 'r') as f:
                try:
                    self.previous_matchups = eval(f.read())
                    if not isinstance(self.previous_matchups, dict):
                        raise SyntaxError
                except SyntaxError:
                    self.previous_matchups = {}
        except IOError:
            open(previous_matchups_filename, 'w').close()
            self.previous_matchups = {}

    def write_previous_matchups_to_file(self):
        with open(previous_matchups_filename, 'w') as f:
            f.write(str(self.previous_matchups))

    def run(self):
        self.read_previous_matchups_from_file()

        self.create_matchup()
        print("    Finished creating match-up")
        # self.create_sticky_submission()
        # self.write_previous_matchups_to_file()

if __name__ == '__main__':
    cf_bot = Bot()

    cf_bot.run()
