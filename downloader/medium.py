#!/usr/bin/env python3

import requests
import json

def get_latest_post_ids(user, limit):
    """
        Get latest {limit} posts from {user} in JSON format.

        If {limit} is zero, it will fetch 1 posts
        If there is no {limit}, it will fetch the default value (10)
    """
    url = "https://medium.com/@{0}/latest".format(user)

    if limit is 0:
        params = {"limit": 1}
    elif limit:
        params = {"limit": limit}
    else:
        params = {}

    headers = {'Accept': 'application/json'}

    response = requests.get(url, params, headers=headers)
    return get_post_ids(response.text)


def get_post_ids(text):
    """
        Deletes the XML snipplet from the beginning of {text},
        as the Medium API tries to avoid json hijacking

        Looks for Post IDs in {parsed_json}["payload"]["references"]["Post"],
        and if it exists, returns the keys, otherwise an empty array.
    """
    # this is needed, because the Medium API endpoint returns xml snipplet
    # before the json to avoid json hijacking
    # 2017. 06. 07.
    #
    # Takes the substring of {text} between the first occurence of { and the end
    text_without_xml = text[text.find("{"):]

    parsed_json = json.loads(text_without_xml)
    if "payload" in parsed_json:
        if "references" in parsed_json["payload"]:
            if "Post" in parsed_json["payload"]["references"]:
                return parsed_json["payload"]["references"]["Post"].keys()
    return []
