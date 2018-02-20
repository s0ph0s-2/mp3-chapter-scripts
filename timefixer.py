#!/usr/local/bin/python3
# Convert output from log2json.py into the format required by chaptagger.py
import json
import sys
import os
import datetime

INTRO_LENGTH = 105670


# Do the actual conversion
def convert_to_deltas(json_object, time_mode):
    # Initialize an array to hold the output
    deltas = []
    # Initialize a variable to hold the start time
    intro_time = datetime.timedelta
    # Initialize a boolean to hold the found_intro state
    found_intro = False
    # Set time format string based on time_mode
    time_fmt_str = ""
    if time_mode == "weechat":
        time_fmt_str = "%Y-%m-%d %H:%M:%S"
    elif time_mode == "znc":
        time_fmt_str = "%H:%M:%S"
    elif time_mode == "textual":
        time_fmt_str = "%Y-%m-%dT%H:%M:%S%z"

    intro_index = -1
    for i in range(0, len(json_object)):
        if json_object[i][0].startswith("fnt-"):
            intro_index = i

    # If we have an intro track, use it as the first time.
    if intro_index >= 0:
        intro_time = datetime.datetime.strptime(
            json_object[intro_index][1],
            time_fmt_str
        )
    # Otherwise, assume the user has removed erroneous tracks from the start of
    # the tracklist and use the first track (minus the length of the intro) as
    # the starting time.
    else:
        intro_time = datetime.datetime.strptime(
            json_object[0][1],
            time_fmt_str
        ) - datetime.timedelta(milliseconds=INTRO_LENGTH)

    # For each datapoint in the json object, do the following
    start = intro_index if intro_index > 0 else 0
    for datapoint in json_object[start:]:
        # Calculate the time delta
        timeobj = datetime.datetime.strptime(datapoint[1], time_fmt_str)
        # Handle next-day times
        if datapoint[1].startswith("00"):
            timeobj = timeobj + datetime.timedelta(days=1)
        timedelta = timeobj - intro_time
        # Append the object to the list
        deltas.append([datapoint[0], timedelta.total_seconds() * 1000])
    # Return the list of titles with times
    return deltas


# Main method
def main(directory, time_mode):
    # If the path specified is a directory
    if os.path.isdir(directory):
        # Get all of the files in it
        files = [f for f in os.listdir(directory)
                 if os.path.isfile(os.path.join(directory, f))]
        # For each file,
        for filename in files:
            # Check to see if it ends with ".json"
            if filename.endswith(".json"):
                # If it does, open the file and read its contents into
                # json_object, then process them
                deltas = []
                with open(os.path.join(directory, filename), "r") as filedata:
                    json_object = json.load(filedata)
                    try:
                        deltas = convert_to_deltas(json_object, time_mode)
                    except IndexError:
                        print("Starting title not found in", filename)
                # Then, write the processed data out to the same filename,
                # but with ".fix.json"
                with open(os.path.join(
                    directory,
                    filename[:-5] + ".fix.json"
                ), "w") as outfile:
                    json.dump(deltas, outfile)

# If it's the main method, read sys.argv and pass it to main
if __name__ == "__main__":
    directory = sys.argv[1]
    time_mode = ""
    if len(sys.argv) > 2:
        if sys.argv[2] == "--weechat":
            print("Setting time mode to weechat.")
            time_mode = "weechat"
        elif sys.argv[2] == "--znc":
            print("Setting time mode to znc.")
            time_mode = "znc"
        elif sys.argv[2] == "--textual":
            print("Setting the time mode to textual.")
            time_mode = "textual"
    else:
        print("Setting time mode to znc.")
        time_mode = "znc"
    main(directory, time_mode)
