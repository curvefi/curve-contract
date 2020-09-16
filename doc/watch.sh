#!/bin/bash

# This script compiles the document as soon as all the .md files in the project are updated.
# In debian-based distros, it needs inotify-tools and (optionally) libnotify-bin

inotifywait -m -e create ./ | while read dir event file; do
    if [[ $file =~ .*\.md ]]
    then
        pandoc README.md -o readme.pdf && notify-send "Markdown compiled" || notify-send "Markdown error"
    fi
done
