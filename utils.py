import re


def validate_items(translation_dict):
    success = True
    label_pattern = re.compile("^[A-Z0-9_]+$")
    for key, value in translation_dict.items():
        if not label_pattern.match(key):
            print("Invalid key: '%s'" % key)
            success = False
    return success
