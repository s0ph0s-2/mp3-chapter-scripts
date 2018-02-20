#! /usr/local/bin/python3
"""Chapter Tagger

A Python script designed to add chapter tags to an MP3 file, using time data
specified in an XMP file.
Written by William Leuschner."""

# import eyed3
from mutagen.id3 import ID3, CTOC, CHAP, TIT2, CTOCFlags
import mutagen
from bs4 import BeautifulSoup
import argparse

V4_FRAMES = {"AENC", "APIC", "ASPI", "COMM", "COMR", "ENCR", "EQU2", "ETCO", "GEOB", "GRID", "LINK", "MCDI", "MLLT", "OWNE", "PRIV", "PCNT", "POPM", "POSS", "RBUF", "RVA2", "RVRB", "SEEK", "SIGN", "SYLT", "SYTC", "TALB", "TBPM", "TCOM", "TCON", "TCOP", "TDEN", "TDLY", "TDOR", "TDRC", "TDRL", "TDTG", "TENC", "TEXT", "TFLT", "TIPL", "TIT1", "TIT2", "TIT3", "TKEY", "TLAN", "TLEN", "TMCL", "TMED", "TMOO", "TOAL", "TOFN", "TOLY", "TOPE", "TOWN", "TPE1", "TPE2", "TPE3", "TPE4", "TPOS", "TPRO", "TPUB", "TRCK", "TRSN", "TRSO", "TSOA", "TSOP", "TSOT", "TSRC", "TSSE", "TSST", "TXXX", "UFID", "USER", "USLT", "WCOM", "WCOP", "WOAF", "WOAR", "WOAS", "WORS", "WPAY", "WPUB", "WXXX",}
V3_FRAMES = {"AENC", "APIC", "COMM", "COMR", "ENCR", "EQUA", "ETCO", "GEOB", "GRID", "IPLS", "LINK", "MCDI", "MLLT", "OWNE", "PRIV", "PCNT", "POPM", "POSS", "RBUF", "RVAD", "RVRB", "SYLT", "SYTC", "TALB", "TBPM", "TCOM", "TCON", "TCOP", "TDAT", "TDLY", "TENC", "TEXT", "TFLT", "TIME", "TIT1", "TIT2", "TIT3", "TKEY", "TLAN", "TLEN", "TMED", "TOAL", "TOFN", "TOLY", "TOPE", "TORY", "TOWN", "TPE1", "TPE2", "TPE3", "TPE4", "TPOS", "TPUB", "TRCK", "TRDA", "TRSN", "TRSO", "TSIZ", "TSRC", "TSSE", "TYER", "TXXX", "UFID", "USER", "USLT", "WCOM", "WCOP", "WOAF", "WOAR", "WOAS", "WORS", "WPAY", "WPUB", "WXXX"}
V2_FRAMES = {"BUF", "CNT", "COM", "CRA", "CRM", "ETC", "EQU", "GEO", "IPL", "LNK", "MCI", "MLL", "PIC", "POP", "REV", "RVA", "SLT", "STC", "TAL", "TBP", "TCM", "TCO", "TCR", "TDA", "TDY", "TEN", "TFT", "TIM", "TKE", "TLA", "TLE", "TMT", "TOA", "TOF", "TOL", "TOR", "TOT", "TP1", "TP2", "TP3", "TP4", "TPA", "TPB", "TRC", "TRD", "TRK", "TSI", "TSS", "TT1", "TT2", "TT3", "TXT", "TXX", "TYE", "UFI", "ULT", "WAF", "WAR", "WAS", "WCM", "WCP", "WPB", "WXX"}
ID3_FRAMES = V2_FRAMES | V3_FRAMES | V4_FRAMES

class MP3File:
    """An MP3 file."""

    def __init__(self, pointer):
        self.tag = None
        self.fp = pointer
        self.load_audio_file()

    def load_audio_file(self):
        """Load the audio file at `pointer` into mutagen."""
        try:
            print("Trying to load the default way")
            self.tag = ID3(self.fp)
        except mutagen.MutagenError:
            print("Exception encountered. Creating new tag...")
            broken = mutagen.id3.ID3FileType(self.fp)
            broken.add_tags(ID3=mutagen.id3.ID3)
            self.tag = broken.ID3()

    def wipe_all_frames(self):
        self.tag.delete()


class XMPTracklist:
    def __init__(self, xml_fp):
        self.xml_fp = xml_fp
        self.soup = None
        self.framerate = None
        self.tracklist = []
        self.make_soup()
        self.find_framerate()
        self.read_tracks()

    def make_soup(self):
        self.soup = BeautifulSoup(self.xml_fp, 'lxml-xml')
        self.xml_fp.close()

    def find_framerate(self):
        tracks_tag = self.soup.find_all("Tracks")[0]
        frame_str = tracks_tag.find_all("frameRate")[0].contents[0]
        frame_list = frame_str.split("f")
        self.framerate = float(frame_list[1]) / 1000.0

    def find_track_holder(self):
        return self.soup.find_all("Tracks")[0].find_all("Seq")[0]

    def number_normalizer(self, number_as_str):
        """Normalizes the weird frame numbers into milliseconds."""

        if number_as_str.isnumeric() is False:
            return number_as_str

        return int(round(float(number_as_str) / self.framerate))

    def read_tracks(self):
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
                # If the name isn't None (emptystr) and the name is in the list
                # of data elements,
                if child.name is not None and child.name in data_attrs:
                    # Append the name (minus the prefix) to the keys list
                    data_keys.append(child.name.lower())
                    # Append the value to the values list
                    data_vals.append(
                        self.number_normalizer(child.contents[0])
                    )
                    # if child.name == "name":
                    #     print("Reading %s..." % child.contents[0])
            data = dict(zip(data_keys, data_vals))
            self.tracklist.append(data)


def id_list_gen(up_to):
    l = []
    for i in range(1, up_to + 1):
        l += [u"chp"+str(i), ]
    return l


def generate_ctoc(num_chaps):
    """Generates a CTOC frame for `num_chaps` chapters."""
    return CTOC(
        element_id=u"toc",
        flags=CTOCFlags.TOP_LEVEL | CTOCFlags.ORDERED,
        child_element_ids=id_list_gen(num_chaps),
        sub_frames=[
            TIT2(text=u"Primary Chapter List"),
        ]
    )


def generate_chap(name, start, end, eid):
    """Generate a CHAP frame that starts at `start`, ends at `end`, has frame ID
    `id`, and contains a TIT2 frame with the text `name`."""
    return CHAP(
        element_id=eid,
        start_time=start,
        end_time=end,
        sub_frames=[
            TIT2(text=name),
        ]
    )


def generate_chaplist(dict_list):
    """Generate a list of CHAP objects from the dicts in `dict_list`."""
    chap_list = []
    for d, i in zip(dict_list, range(len(dict_list))):
        chap_list.append(generate_chap(d["name"], d["starttime"],
                                       d["starttime"] +
                                       d["duration"], u"chp" + str(i + 1)))
    return chap_list


def no_padding(arg):
    return 0


def main():
    parser = argparse.ArgumentParser(description="Add chapters to an MP3 file.")
    parser.add_argument("-m", "--mp3", action="store", required=True, nargs=1,
                        dest="mp3", help="MP3 file to add chapters to.")
    parser.add_argument("-x", "--xmp", action="store", required=True, nargs=1,
                        type=argparse.FileType("r"), dest="xmp",
                        help="XMP file to read chapters from.")
    parser.add_argument("-d", "--drop-frametype", action="append", type=str,
                        dest="drop_type", nargs="*", choices=ID3_FRAMES,
                        help="Drop frames of given type in existing ID3 tag.")
    parser.add_argument("--drop-all", action="store_true", dest="drop_all",
                        help="Remove all frames currently in the tag.")
    parser.add_argument("-v", "--verbose", action="store_true", dest="v")
    namespace = parser.parse_args()
    # Timestamps
    xmp = XMPTracklist(namespace.xmp[0])
    tracks = xmp.tracklist
    # Get the audio file
    mp3 = MP3File(namespace.mp3[0])
    if namespace.drop_all:
        if namespace.v:
            print("Deleting all existing frames...")
        mp3.wipe_all_frames()
    if namespace.drop_type is not None and len(namespace.drop_type) > 0:
        for frametype in namespace.drop_type:
            if namespace.v:
                print("Deleting %s frames..." % frametype[0])
            mp3.tag.delall(frametype[0])
    # Create and add the TOC
    if namespace.v:
        print("Generating CTOC (table of contents) frame...")
    mp3.tag.add(generate_ctoc(len(tracks)))
    # Create and add the chapters
    for chap in generate_chaplist(tracks):
        if namespace.v:
            print(
                "Adding CHAP frame for %s..." % chap.sub_frames["TIT2"].text[0]
            )
        mp3.tag.add(chap)
    # Save the changes to disk
    if namespace.v:
        print("Writing to disk...")
    # This line's important. After significant testing, I determined that most
    # podcast clients don't like v2.4 tags yet. Or padding.
    mp3.tag.update_to_v23()
    mp3.tag.save(mp3.fp, v2_version=3, padding=no_padding)
    print("Done!")


if __name__ == '__main__':
    main()
