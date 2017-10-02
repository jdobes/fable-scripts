#!/usr/bin/python

import sys
import json

from binary_file import BinaryTextFile
from config import DEBUG
from utils import validate_items


if __name__ == "__main__":
    bf = BinaryTextFile(sys.stdin.read())
    if DEBUG:
        print(bf.get_header())
        print(bf.get_index())
    translations = bf.get_items()
    if validate_items(translations):
        if not DEBUG:
            print(json.dumps(translations, indent=4, ensure_ascii=False, sort_keys=False).encode("utf_8"))
    else:
        sys.exit(1)
