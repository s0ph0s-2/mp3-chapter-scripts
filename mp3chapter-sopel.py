"""MP3 Chapter Tagger Sopel Plugin

This module provides Sopel with the capability of listening to a channel and
recording the timestamps of when certain messages are posted. Specifically, it
enables a user to add MP3 Chapters to a music podcast at every song beginning.
"""
import sopel.module
import datetime
import json

# What nick announces the tracks?
# watch_nick = "^_^"
watch_nick = "s0ph0s"
# What channel do I listen in?
watch_channel = "#FNT"
# Who do I NOTICE when I record a track?
notice_nick = "s0ph0s"
# Am I currently recording?
is_recording = False
# Dictionary to hold the track times
time_stack = []
# Length of the intro track
intro_length = 105670
# Have I recorded the first track yet?
recorded_first_track = False
# When did I start recording?
record_start_time = None
# JSON data directory
# json_dir = "/srv/http/etc/fntTimeDeltas/"
json_dir = "/Users/notch/Desktop/"


# Did someone say something that looks like a track announcement?
@sopel.module.rule(r"Now Playing (\(Bit Perfectly\) )?on XBN: (.+)")
def save_timestamp(bot, trigger):
    global is_recording
    global record_start_time
    global time_stack
    global recorded_first_track
    intro_offset_correction = 0
    # If the sender of the message is the bot and I'm supposed to record,
    # (Do I care?)
    if (
        trigger.nick == watch_nick and
        is_recording is True and
        trigger.sender == watch_channel
    ):
        # If I haven't yet recorded the first track,
        if recorded_first_track is False:
            # Get the start time
            record_start_time = datetime.datetime.now()
            # and record that I've recorded the first track
            recorded_first_track = True
            # Check to see if it's the intro or not
            if trigger.group(2).startswith("fnt-") is True:
                # It's the intro.
                intro_offset_correction = 0
            else:
                # It's not the intro.
                intro_offset_correction = intro_length

        # Append the following tuple to the time stack:
        # (track title, #seconds since start of podcast)
        # The * 1000 is because eyed3 expects millisecond
        # offsets.
        time_stack.append((
            trigger.group(2),
            (
                datetime.datetime.now() -
                record_start_time
            ).total_seconds() * 1000 + intro_offset_correction
        ))
        # Tell the admin that I recorded a track time
        bot.notice(
            "Recorded \"%s\"." % trigger.group(2),
            destination=notice_nick
        )


@sopel.module.commands("begin_recording")
@sopel.module.require_admin("Nope.")
@sopel.module.require_privmsg()
def begin_recording(bot, trigger):
    global is_recording
    is_recording = True
    bot.notice(
        "I'll start timing when %s announces the first track." % watch_nick,
        destination=trigger.sender
    )


@sopel.module.commands("end_recording")
@sopel.module.require_admin()
@sopel.module.require_privmsg()
def end_recording(bot, trigger):
    global is_recording
    global recorded_first_track
    is_recording = False
    recorded_first_track = False
    datestr = datetime.datetime.now().date().isoformat()
    with open(json_dir + "fnt" + datestr + ".json", "w") as datfile:
        json.dump(time_stack, datfile)
    bot.notice(
        "I'm done recording and I've exported the timedelta data to JSON.",
        destination=trigger.sender
    )


@sopel.module.commands("reset_times")
@sopel.module.require_admin()
@sopel.module.require_privmsg()
def reset_times(bot, trigger):
    global time_stack
    global recorded_first_track
    global record_start_time
    global is_recording
    recorded_first_track = False
    record_start_time = None
    time_stack = []
    is_recording = False
    bot.notice(
        "All of the times have been reset.",
        destination=trigger.sender
    )
