#!/usr/bin/env python3

import downloader.medium as medium
import argparse

parser = argparse.ArgumentParser(prog='run.py', description="Script to convert medium posts to markdown files")
parser.add_argument('-u', metavar='USER', help="username", required=True, type=str)
parser.add_argument('-l', metavar='LIMIT', help="Number of posts to retrieve. Integer, and the default is 10 by Medium. Zero will be swapped to one.", type=int)
args = parser.parse_args()

postIDs = medium.get_latest_post_ids(args.u, args.l)
print(postIDs)
