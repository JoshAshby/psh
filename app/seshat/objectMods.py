#!/usr/bin/env python
"""
Seshat
Web App/API framework built on top of gevent
modifying decorators

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2012
http://joshashby.com
joshuaashby@joshashby.com
"""


def login(groups=[], redirect=""):
    def wrapper(HTTPObject):
        HTTPObject._login = True
        HTTPObject._groups = groups
        HTTPObject._redirect_url = redirect
        return HTTPObject
    return wrapper
