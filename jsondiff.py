#!/usr/bin/python

import sys
import json

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: %s fileA.json fileB.json" % sys.argv[0])
        sys.exit(1)

    with open(sys.argv[1]) as file_a:
        json_a = json.load(file_a)
    with open(sys.argv[2]) as file_b:
        json_b = json.load(file_b)

    print("Total keys in %s: %d" % (sys.argv[1], len(json_a)))
    print("Total keys in %s: %d" % (sys.argv[2], len(json_b)))

    in_a = []
    in_b = []
    in_both = []
    identical = []
    for key in json_a:
        if key in json_b:
            in_both.append(key)
            if json_a[key] == json_b[key]:
                identical.append(key)
        else:
            in_a.append(key)

    for key in json_b:
        if key not in json_a:
            in_b.append(key)

    print("Keys in both: %d" % (len(in_both)))
    print(" * Identical values: %d" % (len(identical)))
    print("Keys only in %s: %d" % (sys.argv[1], len(in_a)))
    print("Keys only in %s: %d" % (sys.argv[2], len(in_b)))
