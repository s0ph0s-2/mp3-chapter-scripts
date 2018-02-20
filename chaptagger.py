#! /usr/local/bin/python
"""Chapter Tagger

A Python script designed to take two files from command line arguments, an MP3
file and a JSON file, and use time delta data in the JSON file to add chapter
markers to the MP3."""
import eyed3
import json
from sys import argv

# Usage: ./chaptagger.py mp3file.mp3 timedeltas.json


def make_timeobj(deltas, i):
    if i == len(deltas) - 1:
        # If it's the last one, make the end time 3 minutes later.
        # There isn't an easy way that I've found to get the
        # track length in milliseconds.
        # int() prevents eyed3 from crashing; the times are floats.
        # I decided that floor() was an acceptable method of rounding; better
        # to err on the side of before-the-track than during-the-track
        return eyed3.id3.frames.StartEndTuple(
            int(deltas[i][1]),
            int(deltas[i][1]) + 180000
        )
    else:
        return eyed3.id3.frames.StartEndTuple(
            int(deltas[i][1]),
            int(deltas[i + 1][1])
        )


def main():
    print("argv:", repr(argv))
    # Time deltas
    deltas = None
    # What does the chapter ID start with?
    chapter_id_start = "chp"
    # List of chapter IDs
    chapter_ids = []
    # Read in the time deltas
    with open(argv[2], "r") as datfile:
        deltas = json.load(datfile)
    # Get the audio file
    audiofile = eyed3.load(argv[1])
    # For each of the time deltas,
    for i in range(0, len(deltas)):
        # Create a start-end time object
        timeobj = make_timeobj(deltas, i)
        # Make a FrameSet object to hold the chapter title
        subframes = eyed3.id3.frames.FrameSet()
        # Get the chapter title
        subframes.setTextFrame("TIT2", deltas[i][0])
        # Make chapter ID
        chap_id = chapter_id_start + str(i)
        # Add it to the list of chapter IDs for the Table of Contents
        chapter_ids.append(chap_id)
        # Write the tag to the file
        audiofile.tag.chapters.set(
            element_id=chap_id,
            times=timeobj,
            sub_frames=subframes
        )
    # Write the table of contents to the file
    audiofile.tag.table_of_contents.set(
        element_id="toc",
        child_ids=chapter_ids,
    )
    # Save the changes to disk
    audiofile.tag.save()


if __name__ == '__main__':
    main()
