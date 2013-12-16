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

import tempfile
import shutil


def write_file(path, files):
    """
    Simply writes the files contents the disk at the given location.
    """
    with open(path, 'w+b') as f:
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

        write_file(path, fi)

        return path

    else:
        # TODO: DO Shit
        raise Exception(req.status_code)


class TemporaryDirectory(object):
    def __init__(self, suffix="", prefix="tmp_", dir=None):
        self.tmp = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)

    def __enter__(self):
        return self.tmp

    def __exit__(self, *errors):
        return self.destroy()

    def destroy(self):
        if self.tmp:
            shutil.rmtree(self.tmp)
        self.tmp = ""

    def __del__(self):
        if "tmp" in self.__dict__:
            self.__exit__(None, None, None)

    def __str__(self):
        if self.name:
            return "< TemporaryDirectory at: %s >" % (self.name)
        else:
            return "< Deleted TemporaryDirectory >"
