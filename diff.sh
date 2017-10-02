#!/usr/bin/env bash

JSON_A="./data/text-tlch-cz.json"
JSON_B="./data/text-anniversary-en.json"

./jsondiff.py $JSON_A $JSON_B
