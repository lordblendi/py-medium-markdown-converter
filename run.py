#!/usr/bin/env python3

import downloader.get_from_medium as medium
import argparse

parser = argparse.ArgumentParser(prog='run.py', description="Script to convert medium posts to markdown files")
parser.add_argument('-u', metavar='USER', help="username", required=True)
parser.add_argument('-l', metavar='LIMIT', help="Number of posts to retrieve")
args = parser.parse_args()

medium.test(args.u)
if args.l:
    print(args.l)
