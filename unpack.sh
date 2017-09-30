#!/usr/bin/env bash

SOURCE_FILE="tlch/data/lang/English/text.big"

# Checksum of text.big file from Czech version
SOURCE_SHA256="9babf984970dd7c9caf96a615daa69e468ee1ad1efa2b79e7c7d6455ddd5c63d"

SOURCE_SHA256_ACTUAL=$(sha256sum $SOURCE_FILE | awk '{print $1}')

if [ "$SOURCE_SHA256" == "$SOURCE_SHA256_ACTUAL" ]; then
    cat $SOURCE_FILE | ./big2json.py > texts.json
else
    echo "Checksum check failed."
fi


