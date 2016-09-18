"""
Author: Sason R Baghdadi
Purpose: Upload the most recently recorded highlight to Streamable.com and post it to Reddit.com/r/MotoGPHighlights

Actions required to implement:
    1. Python 2.7 (Haven't tested it on Python 3.x yet)
    2. A Reddit account with moderator permission on your subreddit.
        2a. The account will need at least 2 link karma in order to bypass CAPTCHA requirements.
    3. The PRAW module will need to be installed on the machine running this script.
        3a. PRAW can be found here: https://praw.readthedocs.org/en/latest/
            Don't know how to install Python modules on Windows? Watch this: http://www.youtube.com/watch?v=ddpYVA-7wq4
"""
from Projects.RedditBot.login import *
import requests
import json
import glob
import os
import praw

# Directory where videos are stored. Make sure \\ is at the end of the string
VIDEO_DIRECTORY = "F:\\Users\\Sason\\Videos\\Recordings\\"
SUBREDDIT = "MotoGPHighlights"
REQUIRED_TAGS = ["[Moto3]", "[Moto2]", "[MotoGP]"]

# TODO: Possibly implement gfycat api?


class Bot:

    def __init__(self):
        # Returns the path of the most recently added video
        self.newest_video_path = self._find_newest_video()

    @staticmethod
    # Locates and returns the most recently added video in the given directory (VIDEO_DIRECTORY)
    def _find_newest_video():
        print "Locating newest video path ..."
        try:
            newest_video_path = max(glob.glob(VIDEO_DIRECTORY + '*.mp4'), key=os.path.getctime)
        except:
            newest_video_path = raw_input("Couldn't find any videos in that path. Please manually enter a file path:\n")

        return newest_video_path

    # Uploads the most recently added video to Streamable.com
    # Return the url of the uploaded video
    def _upload_to_streamable(self, credentials=streamable_login()):
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
    def _post_to_reddit(self):
        print "Logging in to Reddit ..."
        reddit = praw.Reddit(user_agent="Script that automatically uploads and posts to r/MotoGPHighlights by /u/nosas")
        reddit_login(reddit)

        user_input = " "
        submission_title = ""

        while user_input != "":
            submission_title = raw_input("Enter submission title: ")
            if len(submission_title) < 8 or submission_title.split()[0] not in REQUIRED_TAGS:
                print "****Make sure title starts with [Moto3], [Moto2], [MotoGP] (with a space after)"
            else:
                user_input = raw_input("    Do you want to modify the title? (leave blank for no): ")

        submission = reddit.submit(SUBREDDIT, submission_title, url=self._upload_to_streamable())
        self._set_reddit_flair(submission)

        print "\nSubmission posted: " + submission.permalink

    # Sets link flair for the submission
    def _set_reddit_flair(self, submission):
        track_dict = self._parse_reddit_flair_list(submission.get_flair_choices())
        # User selects a country from keys in track_dict. If the country is in track_dict and the country has multiple
        # tracks, list the track names corresponding the the country and allow for the user to select a track from
        # the list. Else, the country only has one track, so select that country as the flair_choice
        country_choice = ""
        track_choice = ""

        print "\nCountry List = " + ", ".join(track_dict.keys())
        while country_choice not in track_dict:
            user_choice = raw_input("Select a country: ")
            if raw_input("    Do you want to modify your choice? (Leave blank for no): ") == "":
                country_choice = user_choice

        if country_choice in track_dict:
            # If the country has one track, select that track. Else, list the track names.
            # Finally, reconstruct flair_choice to be "CountryName - TrackName"
            if len(track_dict[country_choice]) == 1:
                track_choice = track_dict[country_choice][0]
            else:
                print "Track List = " + ", ".join(track_dict[country_choice])
                while track_choice not in track_dict[country_choice]:
                    user_choice = raw_input("Select a track: ")
                    if raw_input("    Do you want to modify your choice? (Leave blank for no): ") == "":
                        track_choice = user_choice

            flair_choice = country_choice + " - " + track_choice
        else:
            # Some countries are not in CountryName - TrackName format, because they only have one track, so they
            # will not be in the track_dict.
            flair_choice = country_choice

        submission.set_flair(flair_choice)

    @staticmethod
    # Returns a dict based denoted as {CountryName:[TrackName(s)]} based on the submission's flair choices
    def _parse_reddit_flair_list(submission_flair_choices):
        # A sorted list of all the available link flairs. Some flairs are denoted as CountryName - TrackName due to
        # multiple races in the same country.
        flair_list = sorted(set([flair["flair_text"] for flair in submission_flair_choices["choices"]]))

        # Dict to be returned with format {CountryName:[TrackName(s)]}
        track_dict = {}

        for flair in flair_list:
            # If the flair has a hyphen (" - "), then split it and add the flair to the track_dict
            if " - " in flair:
                country_name, track_name = flair.split(" - ")
                # If the key isn't in track_dict, then create {key:[value]}, with value being a list of track names.
                if country_name not in track_dict:
                    track_dict[country_name] = [track_name]
                else:
                    track_dict[country_name].append(track_name)

        return track_dict

    def run(self):
        self._post_to_reddit()

if __name__ == '__main__':
    motoBot = Bot()
    motoBot.run()
