# Python Medium Markdown Converter

A small script to download a user's latest posts into markdown files. The files will be named with release date and dasherized title, like [Jekyll uses it](https://jekyllrb.com/docs/posts/#creating-post-files). Example: `2015-08-05-hello.md`

## Usage

```
python3 run.py -u username -l 5
```

### Parameters

The script accepts two parameters:
- `u` is for the user name. Mandatory and has to be a string.
- `l` is for limit. Number of posts to retrieve. Not mandatory. Integer and the default is 10 by Medium. Zero will be swapped to one.
