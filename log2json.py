#!/usr/local/bin/python3
# Convert a semicolon-delimited text file to a JSON file
# Very specific and hacked-together, could be much better.
import os
import sys
import json

# Get the directory specified on the command line.
directory = sys.argv[1]
# If it's a directory, go on.
if os.path.isdir(directory):
    # Get all of the files in the directory, using list comprehension magic
    files = [f for f in os.listdir(directory)
             if os.path.isfile(os.path.join(directory, f))]
    # For each file in that array, do the following
    for semicolons in files:
        # If it ends with ".txt" and it's larger than 1024 KB, do the following
        if (
            semicolons.endswith(".txt") and
            os.path.getsize(os.path.join(directory, semicolons)) > 1024
        ):
            # Use "in_data" as the file
            with open(os.path.join(directory, semicolons), "r") as in_data:
                # Initialize a variable to hold the data
                times = []
                # Iterate over the lines in the file and
                for line in in_data:
                    # Split it at the semicolons,
                    splitline = line.split(";")
                    # And add it to the list, minus the \n at the end
                    times.append([splitline[1][:-1], splitline[0]])
                # Write the JSON data to file.
                with open(os.path.join(
                    directory,
                    semicolons[:-4] + ".json"
                ), "w") as outfile:
                    json.dump(times, outfile)
            # Tell the user what was done.
            print("JSON-ified", semicolons)
