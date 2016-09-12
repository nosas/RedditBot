from login import streamable_login, reddit_login
import requests
import json
import glob
import os
import praw

# Directory where videos are stored. Make sure \\ is at the end of the string
VIDEO_DIRECTORY = "C:\\Users\\Sason\\Desktop\\rec\\"
SUBREDDIT = "MotoGPHighlights"
REQUIRED_TAGS = ["[Moto3]", "[Moto2]", "[MotoGP]"]


class Bot:

    def __init__(self):
        # Returns the path of the most recently added video
        self.newest_video_path = self.find_newest_video()

    @staticmethod
    # Locates and returns the most recently added video in the given directory (VIDEO_DIRECTORY)
    def find_newest_video():
        print "Locating newest video path ..."
        try:
            newest_video_path = max(glob.glob(VIDEO_DIRECTORY + '*.mp4'), key=os.path.getctime)
        except:
            newest_video_path = raw_input("Couldn't find any videos in that path. Please manually enter a file path:\n")

        return newest_video_path

    # Uploads the most recently added video to Streamable.com
    # Return the url of the uploaded video
    def upload_to_streamable(self, credentials=streamable_login()):
        title = raw_input("\nEnter video title (leave blank for default title): ")

        print "Uploading video ..."
        # Uploads the video. Remove auth=() to upload anonymously
        streamable = requests.post("https://api.streamable.com/upload",
                                   auth=(credentials["username"], credentials["password"]),
                                   files={"file": open(self.newest_video_path, 'rb')},
                                   data={"title": title}
                                   )
        response = json.loads(streamable.content.decode())
        video_url = "https://streamable.com/" + response["shortcode"]
        print "    Uploading finished: " + video_url

        return video_url

    # Logs into Reddit and posts to the specified subreddit
    def post_to_reddit(self):
        print "Logging in to Reddit ..."
        reddit = praw.Reddit(user_agent="Script that automatically uploads and posts to /r/MotoGPHighlights by /u/nosas")
        reddit_login(reddit)

        user_input = " "
        submission_title = ""

        while user_input != "":
            submission_title = raw_input("Enter submission title: ")
            if len(submission_title) < 8 or submission_title.split()[0] not in REQUIRED_TAGS:
                print "****Make sure title starts with [Moto3], [Moto2], [MotoGP] (with a space after)"
            else:
                user_input = raw_input("    Do you want to modify the title? (leave blank for no): ")

        submission = reddit.submit(SUBREDDIT, submission_title, url=self.upload_to_streamable())
        self.set_reddit_flair(submission)

        print "\nSubmission posted: " + submission.permalink

    @staticmethod
    # Sets link flair for the submission
    def set_reddit_flair(submission):
        flair_list = [item["flair_text"] for item in submission.get_flair_choices()["choices"]]
        print "\nFlair List = " + ", ".join(flair_list)

        flair_choice = raw_input("Select a flair: ")

        while flair_choice not in flair_list:
            flair_choice = raw_input("Select a flair in the flair list: ")

        submission.set_flair(flair_choice)

    def run(self):
        self.post_to_reddit()

if __name__ == '__main__':
    motoBot = Bot()
    motoBot.run()
