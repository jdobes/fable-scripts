#!/usr/bin/env bash

SOURCE_CZ_BIG="data/text-tlch-cz.big"
TARGET_CZ_JSON="data/text-tlch-cz.json"
SOURCE_EN_BBB="data/text-anniversary-en.bbb"
TARGET_EN_JSON="data/text-anniversary-en.json"

SOURCE_CZ_BIG_SHA256="9babf984970dd7c9caf96a615daa69e468ee1ad1efa2b79e7c7d6455ddd5c63d"
TARGET_CZ_JSON_SHA256="0fab1243d0e8061638fb83931a909ce371f32615a98f5bd0f6f2131c39c1f0c7"
SOURCE_EN_BBB_SHA256="4bfecd59ecf143f9c48762281c79756e3162acb69e5110ef06be7cbb27404771"
TARGET_EN_JSON_SHA256="57bb97c0cbabb803e5676fbb1c92b965c35e7142842884b811c77714eb717b38"

SOURCE_CZ_BIG_SHA256_ACTUAL=$(sha256sum $SOURCE_CZ_BIG | awk '{print $1}')
SOURCE_EN_BBB_SHA256_ACTUAL=$(sha256sum $SOURCE_EN_BBB | awk '{print $1}')

# CZ TLCH BIG
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

# EN ANNIVERSARY BBB
if [ "$SOURCE_EN_BBB_SHA256" == "$SOURCE_EN_BBB_SHA256_ACTUAL" ]; then
    echo "$SOURCE_EN_BBB checksum OK."
else
    echo "$SOURCE_EN_BBB checksum failed."
    exit 1
fi

cat $SOURCE_EN_BBB | ./binary2json.py > $TARGET_EN_JSON

TARGET_EN_JSON_SHA256_ACTUAL=$(sha256sum $TARGET_EN_JSON | awk '{print $1}')
if [ "$TARGET_EN_JSON_SHA256" == "$TARGET_EN_JSON_SHA256_ACTUAL" ]; then
    echo "$TARGET_EN_JSON file checksum OK."
else
    echo "$TARGET_EN_JSON file checksum failed."
    exit 1
fi
