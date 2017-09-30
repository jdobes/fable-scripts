#!/usr/bin/python

import sys
import json

from bigfile import BigFile
from config import DEBUG
from utils import validate_items


if __name__ == "__main__":
    big = BigFile(sys.stdin.read())
    translations = big.get_items()

    if validate_items(translations):
        if not DEBUG:
            print(json.dumps(translations, indent=4, ensure_ascii=False, sort_keys=False).encode("utf_8"))
    else:
        sys.exit(1)
