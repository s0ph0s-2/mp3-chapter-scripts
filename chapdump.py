import sys
import mutagen
import datetime
from mutagen.id3 import ID3


FORMAT_CHAP = "{id}\t{start}\t{end}"
FORMAT_SUBFRAME = "\t{frametype}\t{text}"


def main():
    with open(sys.argv[1], "rb") as fp:
        try:
            tag = ID3(fp)
        except mutagen.MutagenError:
            print("No ID3 tag present.")
        chapters = tag.getall("CHAP")
        for chap in chapters:
            start = string_time(chap.start_time)
            end = string_time(chap.end_time)
            print(FORMAT_CHAP.format(
                id=chap.element_id,
                start=start,
                end=end
            ))
            for key, value in chap.sub_frames.items():
                print(string_subframe(key, value))
        mllt = tag.getall("MLLT")
        print("MLLT:", mllt)
        tlen = tag.getall("TLEN")
        print("TLEN:", tlen)


def string_time(time: int) -> str:
    return str(datetime.timedelta(seconds=time/1000.0))


def string_subframe(name, subframe) -> str:
    if name == 'TIT2':
        text = subframe.text
    elif name == 'TIT3':
        text = subframe.text
    elif name.startswith('APIC'):
        text = subframe.mime
    elif name.startswith('WXXX'):
        text = subframe.url
    else:
        text = "unexpected subframe type"
    return FORMAT_SUBFRAME.format(frametype=name, text=text)


if __name__ == "__main__":
    main()
