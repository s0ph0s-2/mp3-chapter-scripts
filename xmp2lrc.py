"""Convert XMP track data to an LRC file for Plex"""
#!/usr/bin/python3
# Program:       xmp2lrc.py
# Purpose:       Convert XMP chapter marker data from Adobe Audition into an LRC file with
#                track names in it
# Author:        s0ph0s
# Creation Date: 2017-04-14

# Needed for arguments
import sys
# needed for floor
import math
# XMP is xml, regrettably.
from bs4 import BeautifulSoup
# JSON files
import json

def ms_to_minsec(msec):
    """Convert milliseconds to mm:ss.ss"""
    # Convert the milliseconds of time to seconds
    allsecs = msec / 1000
    # Calculate the minute length of the provided time
    mins = math.floor(allsecs / 60)
    # Calculate how many seconds over the minute length it is
    secs = allsecs % 60
    # Format it as a string. 2 digit minutes; 5 character wide, 0-padded, 2 decimal seconds
    return "%02d:%05.2f" % (mins, secs)


class XMPTracklist:
    """An XMP tracklist parser"""
    def __init__(self, xml_fp):
        """Initialize this tracklist parser"""
        self.xml_fp = xml_fp
        self.soup = None
        self.framerate = None
        self.tracklist = []
        self.make_soup()
        self.find_framerate()
        self.read_tracks()

    def make_soup(self):
        """Make a BeautifulSoup object out of the provided XMP stuff"""
        self.soup = BeautifulSoup(self.xml_fp, 'lxml-xml')
        self.xml_fp.close()

    def find_framerate(self):
        """Locate the framerate tag in the XMP soup
        Necessary for converting times from difficult-to-use frame numbers to
        easily-applicable millisecond counts"""
        tracks_tag = self.soup.find_all("Tracks")[0]
        frame_str = tracks_tag.find_all("frameRate")[0].contents[0]
        frame_list = frame_str.split("f")
        self.framerate = float(frame_list[1]) / 1000.0

    def find_track_holder(self):
        """Find the tag that holds the track markers"""
        return self.soup.find_all("Tracks")[0].find_all("Seq")[0]

    def number_normalizer(self, number_as_str):
        """Normalizes the weird frame numbers into milliseconds."""
        if number_as_str.isnumeric() is False:
            return number_as_str

        return int(round(float(number_as_str) / self.framerate))

    def read_tracks(self):
        """Parse and pull out the tracks"""
        # Each track is a bs4 Tag object
        track_soup = self.find_track_holder()
        data_attrs = ["startTime", "duration", "name"]
        for track in track_soup.children:
            # Initialize data storage
            data_keys = []
            data_vals = []
            if track.name is None:
                continue
            # For each of the child elements in the track,
            for child in track.children:
                # If the name isn't None (emptystr) and the name starts with
                # "xmpdm:", the prefix on all of the data tags,
                if child.name is not None and child.name in data_attrs:
                    # Append the name (minus the prefix) to the keys list
                    data_keys.append(child.name.lower())
                    # Append the value to the values list
                    data_vals.append(
                        self.number_normalizer(child.contents[0])
                    )
                    # if child.name == "xmpdm:name":
                    #     print("Reading %s..." % child.contents[0])
            # This looks like
            # {
            #     'name':'Wolfgun - Road to Jupiter',
            #     'starttime':10300,
            #     'duration':347000
            # }
            data = dict(zip(data_keys, data_vals))
            self.tracklist.append(data)

# Somewhat-useful usage message
if len(sys.argv) != 3:
    print("Usage: xmp2lrc.py (infile.xmp|infile.json) outfile.lrc")
    exit(1)
# Read the show number from the terminal
SHOWNUM = input("Episode number: ")
# Read the show title from the terminal
SHOWNAME = input("Show title: ")
# The artist will pretty much always be XBN
ARTIST = "..::XANA Creations::.."
# And the album will always be this
ALBUM = "The Friday Night Tech Podcast"
IS_JSON = False
# Open the input and output files
infile = open(sys.argv[1], "r")
outfile = open(sys.argv[2], "w")
# Parse the input file into a tracklist
tracklist = None
if sys.argv[1][-3:] == "xmp":
    tracklist = XMPTracklist(infile).tracklist
    IS_JSON = False
elif sys.argv[1][-4:] == "json":
    tracklist = json.load(infile)
    IS_JSON = True
infile.close()

# Title tag for LRC format
outfile.write("[ti:FNT-%s %s]\n" % (SHOWNUM, SHOWNAME))
# Artist tag for LRC format
outfile.write("[ar:%s]\n" % (ARTIST,))
# Album tag for LRC format
outfile.write("[al:%s]\n" % (ALBUM,))

# Loop over all of the tracks
for track in tracklist:
    # Write the track to the output file
    outfile.write("[%s]%s\n" % (
        # Convert the millisecond time to minutes and seconds
        ms_to_minsec(track['starttime']) if not IS_JSON else ms_to_minsec(track[1]),
        # Just the track name
        track['name'] if not IS_JSON else track[0]
    ))
# Close the output file
outfile.close()
