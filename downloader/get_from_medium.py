#!/usr/bin/env python3

import requests

# Get latest X posts o
def get_latest_posts(user, limit):
    """
        Get latest {limit} posts from {user} in JSON format
    """
    url = "https://medium.com/@{0}/latest".format(user)

    if limit:
        params = {"limit": limit}
    else:
        params =  {}

    headers = {'Accept': 'application/json'}

    response = requests.get(url, params, headers=headers)
    print(response.url)
    print(response.text)
