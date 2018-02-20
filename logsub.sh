oldIFS=$IFS
IFS=""

for file in $1 ; do
    if [ -e  "$file" ] ; then
        # ZNC format
        # gsed -nr "s|^\[([0-9]{2}:[0-9]{2}:[0-9]{2})\] <\^_\^> Now Playing (\(Bit Perfectly\) )?on XBN: (.*)|\1;\3|p" "$file" > "$file.sed.txt"
        # Weechat format
        # gsed -nr "s|^([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\t@\^_\^\tNow Playing (\(Bit Perfectly\) )?on XBN: (.*)|\1;\3|p" "$file" > "$file.sed.txt"
        # Textual format
        gsed -nr "s|^\[([0-9:T\-]{24})\] <@\^_\^> Now Playing (\(Bit Perfectly\) )?on XBN: (.*)|\1;\3|p" "$file" > "$file.sed.txt"
    fi
done

IFS=$oldIFS

