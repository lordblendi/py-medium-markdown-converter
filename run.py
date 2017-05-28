#!/usr/bin/env python3

import downloader.main as downloader
import argparse
import os

parser = argparse.ArgumentParser(prog='run.py', description="Script to convert medium posts to markdown files")
parser.add_argument('-u', metavar='USER', help="username", required=True, type=str)
parser.add_argument('-l', metavar='LIMIT', help="Number of posts to retrieve. Integer, and the default is 10 by Medium. Zero will be swapped to one.", type=int)
args = parser.parse_args()

# creating subdirectory

medium_post_dir_markdown = "medium_posts_markdown"

if not os.path.exists(medium_post_dir_markdown):
    os.makedirs(medium_post_dir_markdown)

post_ids = downloader.get_latest_post_ids(args.u, args.l)
html_posts = downloader.download_posts_in_html(args.u, post_ids)
