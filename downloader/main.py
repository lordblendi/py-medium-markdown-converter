#!/usr/bin/env python3

import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime


def find_latest_posts(user, limit):
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
    return get_post_metadata(response.text)


def get_post_metadata(text):
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
    posts = []
    keys = []

    parsed_json = json.loads(text_without_xml)
    if "payload" in parsed_json:
        if "references" in parsed_json["payload"]:
            if "Post" in parsed_json["payload"]["references"]:
                keys =  parsed_json["payload"]["references"]["Post"].keys()

    for key in keys:
        post = parsed_json["payload"]["references"]["Post"][key]
        new_entry = {
            "id" : post["id"],
            "title" : post["title"],
            # conver the timestamps from miliseconds to seconds
            "published" : float(post["firstPublishedAt"])/1000
        }
        posts.append(new_entry)
    return posts

def download_posts_in_html(user, posts):
    """
        Download a {user}'s posts. The post ids are defined in the {posts}.

        The {posts} also contains the article's title and publish that.
        These combined will be the filename for the markdown files.
    """
    html_posts = []
    main_url = "https://medium.com/@{0}/".format(user)
    for post in posts:
        url = main_url + post["id"]

        # for the filename getting the date of the publication and
        date = datetime.fromtimestamp(post["published"])
        date = date.strftime("%Y-%m-%d")
        # dasherizing the title
        title = post["title"].lower().replace(" ", "-")
        filename = "{0}-{1}".format(date,title)
        post_file = open("medium_posts_markdown/{0}.md".format(filename), "w")

        response = requests.get(url)
        post_file.write(transform_html_to_markdown(response.text))
        post_file.close()

    return html_posts

def transform_html_to_markdown(response):
    """
        Get the article out of the {response} as html then convert it to markdown.

        I parse it as an xml. Because of this, I have to cut out the following part:

        <div class="section-divider">
            <hr class="section-divider">
        </div>

        as this is not a valid xml snipplet.
    """

    post_md = ""
    post_html = response[response.find("<div class=\"section-inner sectionLayout--insetColumn\">"):response.find("</div></section>")]
    print(post_html)
    root = ET.fromstring(post_html)

    for child in root:
        print(child)
        print(child.tag, child.attrib, child.text)

    return post_html
