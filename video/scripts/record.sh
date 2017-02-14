#!/bin/bash

# ffmpeg -f x11grab -s 1920x1080 -r 60 -i :0.0 -f pulse -ac 2 -i default -t 00:50:00 -strict -2 "/hdd/things/captures/$1"

# ffmpeg -f x11grab -s 1920x1080 -r 60 -i :0.0 -f pulse -ac 2 -i default -t 00:50:00 "/hdd/things/captures/$1"
#=preset ultrafast

ffmpeg -s 1920x1080 -r 60 -f x11grab -i :0.0 -f pulse -ac 2 -i default -preset ultrafast -t 00:55:00 "/hdd/things/captures/$1"

# ffmpeg -f x11grab -s 1920x1080 -r 45 -i :0.0 -f pulse -ac 2 -i default -qscale 0 -vcodec huffyuv -t 00:50:00 "/hdd/things/captures/$1"