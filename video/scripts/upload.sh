#!/bin/bash

youtube-upload --title="$1" --privacy="private" --description="$2" --category=Gaming --tags="$3" "$4" &
