"""Token SAving tools """

import json


def token_saver(token):
    """Save token"""
    with open("token.json", "w", encoding="utf-8") as file:
        json.dump(token, file, indent=4)


def token_fetcher():
    """Fetch Token"""
    try:
        with open("token.json", "r", encoding="utf-8") as file:
            token = json.load(file)
            return token
    # pylint: disable=W0718
    except Exception:
        return None
