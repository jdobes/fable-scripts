#!/usr/bin/env bash

SOURCE_FILE="data/text-tlch-cz.big"
TARGET_FILE="data/text-tlch-cz.json"

SOURCE_SHA256="9babf984970dd7c9caf96a615daa69e468ee1ad1efa2b79e7c7d6455ddd5c63d"

SOURCE_SHA256_ACTUAL=$(sha256sum $SOURCE_FILE | awk '{print $1}')

if [ "$SOURCE_SHA256" == "$SOURCE_SHA256_ACTUAL" ]; then
    echo "Source file checksum OK."
else
    echo "Source file checksum failed."
    exit 1
fi

cat $SOURCE_FILE | ./big2json.py > $TARGET_FILE

TARGET_SHA256="32046d108940ea75327aa74e26b5e9d4e4cb23a50d1190417cb0f9163ce1a6a9"

TARGET_SHA256_ACTUAL=$(sha256sum $TARGET_FILE | awk '{print $1}')
if [ "$TARGET_SHA256" == "$TARGET_SHA256_ACTUAL" ]; then
    echo "Target file checksum OK."
else
    echo "Target file checksum failed."
    exit 1
fi
