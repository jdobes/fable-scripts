#!/usr/bin/env bash

SOURCE_CZ_BIG="data/text-tlch-cz.big"
TARGET_CZ_JSON="data/text-tlch-cz.json"

SOURCE_CZ_BIG_SHA256="9babf984970dd7c9caf96a615daa69e468ee1ad1efa2b79e7c7d6455ddd5c63d"
TARGET_CZ_JSON_SHA256="32046d108940ea75327aa74e26b5e9d4e4cb23a50d1190417cb0f9163ce1a6a9"

SOURCE_CZ_BIG_SHA256_ACTUAL=$(sha256sum $SOURCE_CZ_BIG | awk '{print $1}')

if [ "$SOURCE_CZ_BIG_SHA256" == "$SOURCE_CZ_BIG_SHA256_ACTUAL" ]; then
    echo "$SOURCE_CZ_BIG checksum OK."
else
    echo "$SOURCE_CZ_BIG checksum failed."
    exit 1
fi

cat $SOURCE_CZ_BIG | ./binary2json.py > $TARGET_CZ_JSON

TARGET_CZ_JSON_SHA256_ACTUAL=$(sha256sum $TARGET_CZ_JSON | awk '{print $1}')
if [ "$TARGET_CZ_JSON_SHA256" == "$TARGET_CZ_JSON_SHA256_ACTUAL" ]; then
    echo "$TARGET_CZ_JSON file checksum OK."
else
    echo "$TARGET_CZ_JSON file checksum failed."
    exit 1
fi
