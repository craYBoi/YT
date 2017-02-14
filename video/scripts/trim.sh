#!/bin/bash

# first arg is the vid path, second is start time of xx:xx:xx. third is end time
ffmpeg -ss "$2" -i "$4"/"$1" -vcodec copy -acodec copy -to "$3" "$5"/"$6"

