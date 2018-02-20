#! /usr/local/bin/python
"""Chapter Tagger

A Python script designed to take two files from command line arguments, an MP3
file and a JSON file, and use time delta data in the JSON file to add chapter
markers to the MP3."""
import eyed3
import json
from sys import argv

# Usage: ./chaptagger.py mp3file.mp3 timedeltas.json


def make_timeobj(track):
    print(track)
    return eyed3.id3.frames.StartEndTuple(
        track["starttime"],
        track["starttime"] + track["duration"],
    )


def main():
    print("argv:", repr(argv))
    # Timestamps
    tracks = None
    # What does the chapter ID start with?
    chapter_id_start = "chp"
    # List of chapter IDs
    chapter_ids = []
    # Read in the time deltas
    with open(argv[2], "r") as datfile:
        tracks = json.load(datfile)
    # Get the audio file
    audiofile = eyed3.load(argv[1])
    # Create a tag in the file, if one doesn't exist:
    if type(audiofile.tag) is type(None):
        audiofile.initTag(version=(2,4,0))
    # Track number counter
    tracknum = 1
    # For each of the time deltas,
    for track in tracks:
        # Create a start-end time object
        timeobj = make_timeobj(track)
        # Make a FrameSet object to hold the chapter title
        subframes = eyed3.id3.frames.FrameSet()
        # Get the chapter title
        subframes.setTextFrame("TIT2", track["name"])
        # Make chapter ID
        chap_id = chapter_id_start + str(tracknum)
        # Add it to the list of chapter IDs for the Table of Contents
        chapter_ids.append(chap_id)
        # Write the tag to the file
        audiofile.tag.chapters.set(
            element_id=chap_id,
            times=timeobj,
            sub_frames=subframes
        )
        # Increment the track number counter
        tracknum += 1
    # Write the table of contents to the file
    audiofile.tag.table_of_contents.set(
        element_id="toc",
        child_ids=chapter_ids,
    )
    # DEBUG DO NOT USE!
    audiofile.tag.title = u"Sharon Jones"
    audiofile.tag.artist = u"NPR"
    audiofile.tag.album = u"Wait Wait... Don't Tell Me!"
    # Save the changes to disk
    audiofile.tag.save()


if __name__ == '__main__':
    main()
