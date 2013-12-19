#!/usr/bin/env python
"""
various actions to return from an object.

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""


class BaseAction(object):
    head = ()
    def __len__(self):
        return 0

    def __str__(self):
        return ""

    def __unicode__(self):
        return ""


class Redirect(BaseAction):
    def __init__(self, loc):
        self.head = ("303 SEE OTHER", [("Location", str(loc))])


class NotFound(BaseAction):
    def __init__(self):
        self.head = ("404 NOT FOUND", [])


class Unauthorized(BaseAction):
    def __init__(self):
        self.head = ("401 UNAUTHORIZED", [])
