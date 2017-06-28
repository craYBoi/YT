#!/bin/bash

# echo "ffmpeg -ss $2 -i $4/$1 -c copy -to $3 $5/$6"
ffmpeg -ss "$2" -i "$4"/"$1" -c copy -to "$3" "$5"/"$6"
