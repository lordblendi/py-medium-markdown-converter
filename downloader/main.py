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
    # Takes the substring of {text} between the first occurence of { and the
    # end
    text_without_xml = text[text.find("{"):]
    posts = []
    keys = []

    parsed_json = json.loads(text_without_xml)
    if "payload" in parsed_json:
        if "references" in parsed_json["payload"]:
            if "Post" in parsed_json["payload"]["references"]:
                keys = parsed_json["payload"]["references"]["Post"].keys()

    for key in keys:
        post = parsed_json["payload"]["references"]["Post"][key]
        new_entry = {
            "id": post["id"],
            "title": post["title"],
            # conver the timestamps from miliseconds to seconds
            "published": float(post["firstPublishedAt"]) / 1000
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
    print("Downloading posts from user {0}.\n".format(user))

    for post in posts:
        url = main_url + post["id"]

        # for the filename getting the date of the publication and
        date = datetime.fromtimestamp(post["published"])
        date = date.strftime("%Y-%m-%d")
        # dasherizing the title
        title = post["title"].lower().replace(" ", "-")
        filename = "{0}-{1}".format(date, title)
        print("Saving post {0} - {1} into {2}...\t".format(post["id"],post["title"], filename), end="")
        try:
            post_file = open("medium_posts_markdown/{0}.md".format(filename), "w")


            response = requests.get(url)
            post_file.write(transform_html_to_markdown(response.text))
            post_file.close()
            print("done")
        except ET.ParseError:
            print("Something went wrong during the parsing of this post.")
            print(response.text[response.text.find(
                "<div class=\"section-inner sectionLayout--insetColumn\">"):response.text.find("</div></section>")])

    print("\nThe files can be found in the medium_posts_markdown folder.")
    return html_posts


def tag_handler(tag, separator, post_html):
    """
    This function switches from a specific {tag} to a specific
    markdown {separator}

    Example 1: <em>text</em> => *text*
    Example 2: <strong>text</strong> => **text**
    """
    old_tag = tag
    close_tag = "</{0}>".format(tag)
    tag = "<{0}".format(tag)

    start = post_html.find(tag)
    end = post_html.find(close_tag) + len(close_tag)
    start_text = post_html.find(">", post_html.find(tag)) + 1
    end_text = post_html.find(close_tag)

    text = post_html[start_text:end_text]
    new_text = "{1}{0}{1}".format(text, separator)
    post_html = post_html[:start] + new_text + post_html[end:]
    if (post_html.find(tag) >= 0):
        post_html = tag_handler(old_tag, separator, post_html)
    return post_html


def picture_handler(tag, separator, post_html):
    """
    This function switches from a specific {tag} to a specific
    markdown image syntax

    Example:
    <figure>
        <img src="PATH_TO_IMG">
        <figcaption class="imageCaption">CAPTION</figcaption></figure>
    </figure>

    => ![CAPTION](PATH_TO_IMG)
    """
    old_tag = tag
    close_tag = "</{0}>".format(tag)
    tag = "<{0}".format(tag)

    start = post_html.find(tag)
    end = post_html.find(close_tag) + len(close_tag)
    picture_html = post_html[start:end]

    caption = ""
    link = ""
    picture_markdown = ""

    if picture_html.find("src=") >= 0:
        link = picture_html[picture_html.find(
            "src=") + 5:picture_html.find("jpeg\">") + 4]
    if picture_html.find("<figcaption") >= 0:
        caption = picture_html[picture_html.find(
            "<figcaption class=\"imageCaption\">") + 33: picture_html.find("</figcaption>")]

    if len(link) > 0:
        picture_markdown = "<{2}>![{0}]({1})</{2}>".format(caption,
                                                           link, separator)
    post_html = post_html[:start] + picture_markdown + post_html[end:]

    if (post_html.find(tag) >= 0):
        post_html = picture_handler(old_tag, separator, post_html)
    return post_html


def link_handler(tag, post_html):
    """
    This function switches from a specific {tag} to a specific
    markdown link syntax

    Example:
    <a href=URL>CAPTION</a> => [CAPTION](URL)
    """
    old_tag = tag
    close_tag = "</{0}>".format(tag)
    tag = "<{0}".format(tag)

    start = post_html.find(tag)
    end = post_html.find(close_tag) + len(close_tag)
    link_html = post_html[start:end]

    link_markdown = ""
    link = ""
    caption = ""

    caption = link_html[link_html.find(">") + 1: link_html.find("</a>")]
    if link_html.find("href=") >= 0:
        link = link_html[link_html.find(
            "href=") + 6:link_html.find("\" data-href=")]

    if len(caption) == 0:
        caption = link

    if len(link) > 0:
        link_markdown = "[{0}]({1})".format(caption, link)
    post_html = post_html[:start] + link_markdown + post_html[end:]

    if (post_html.find(tag) >= 0):
        post_html = link_handler(old_tag, post_html)
    return post_html


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
    post_html = response[response.find(
        "<div class=\"section-inner sectionLayout--insetColumn\">"):response.find("</div></section>")]

    if post_html.find("<strong") >= 0:
        post_html = tag_handler("strong", "**", post_html)

    if post_html.find("<em") >= 0:
        post_html = tag_handler("em", "*", post_html)

    if post_html.find("<figure") >= 0:
        post_html = picture_handler("figure", "p", post_html)

    if post_html.find("<a") >= 0:
        post_html = link_handler("a", post_html)

    root = ET.fromstring(post_html)

    for child in root:
        if child.tag == "h1":
            post_md += "# {0}".format(child.text)
        elif child.tag == "h2":
            post_md += "## {0}".format(child.text)
        elif child.tag == "h3":
            post_md += "### {0}".format(child.text)
        elif child.tag == "p":
            # TODO: links
            post_md += "\n\n{0}".format(child.text)
        elif child.tag == "ul":
            for item in child:
                post_md += "\n - {0}".format(item.text)
        elif child.tag == "ol":
            for index, item in enumerate(child, start=1):
                post_md += "\n {1}. {0}".format(item.text, index)
        else:
            print("unkown tag: ", child.tag, child.text)

    return post_md
