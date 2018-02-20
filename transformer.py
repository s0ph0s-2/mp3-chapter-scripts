# Apply a transformation function to every track in the json file.
import json
import sys


# Edit this one to make the transformation happen.
def transformer(in_data):
    return [in_data[0], in_data[1] + (284498 - 105670.016879)]


def main(filename):
    old_json = None
    with open(filename, "r") as infile:
        old_json = json.load(infile)
    new_json = []
    for track in old_json:
        new_json.append(transformer(track))
    with open(filename[:-5] + ".fix.json", "w") as outfile:
        json.dump(new_json, outfile)


if __name__ == "__main__":
    main(sys.argv[1])
