#!/usr/bin/env python
"""
Utils for interacting with images.

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import cStringIO
import urlparse

import requests


def write_file(files, path):
    """
    Simply writes the files contents the disk at the given location.
    """
    with open(path, 'wb') as f:
        f.write(files.read())

    return True


def download_file(url, path):
    """
    Download the given url to the path. File extension added automatically.

    This needs to be moved into its own little thingy so it stops blocking
    """
    req = requests.get(url, stream=True)

    if req.status_code == 200:
        url_parts= urlparse.urlparse(url)

        parts = url_parts.path.rsplit(".", 1)
        if len(parts) > 1:
            extension = parts[1]

        path = ''.join([path, ".{}".format(extension)])

        fi = cStringIO.StringIO()
        for chunk in req.iter_content():
            fi.write(chunk)
        fi.seek(0)

        write_file(fi, path)

        return path

    else:
        # TODO: DO Shit
        raise Exception(req.status_code)
