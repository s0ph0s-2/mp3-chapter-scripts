# MP3 Chapter Scripts

I have made a collection of scripts to help me add chapters to [a music podcast
I like](https://fridaynighttech.com).  They're gross, poorly-written, and
generally unsustainable, but they work alright so far.

## What are they?

* `chaptagger.py`: Version 1, reads a JSON file and writes it into the MP3 file.
Usage: `python3 chaptagger.py podcast.mp3 data.json`. I forget the JSON format,
will document later
* `chaptagger2.py`: Version 2, does the same thing as version 1 but less buggy.
It appears to have some debug information in it from when I was testing with
Wait Wait... Don't Tell Me!
* `chaptagger3.py`: Version 3, reads data from an Audition XMP sidecar and
writes it to an MP3 file. Usage: `python3 chaptagger3.py -m podcast.mp3 -x
metadata.xmp` (Currently the one I use)
* `chaptagger4.py`: Version 4, does the same thing as version 3 but with JSON
input instead of XMP.
* `log2json.py`: Convert all of the IRC logs in a directory to the JSON format
from v1 and v4 above
* `logsub.sh`: Read an IRC log and substitute out all of the messages from users
who aren't the track announce bot
* `mp3chapter-sopel.py`: A [Sopel](https://sopel.chat) bot to make
JSON-formatted data for v1 and v4
* `timefixer.py`: Shift times forward by the exact length of the podcast's intro
track for when I didn't get the bot recording fast enough.
* `transformer.py`: A python script to shift times by some function to fix errors
inherent in scraping from IRC. Not very good at its job.
* `xmp2lrc.py`: Convert XMP sidecars to LRC files, for a friend
