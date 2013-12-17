#!/usr/bin/env python
"""
Seshat
Web App/API framework built on top of gevent
routing decorator

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2012
http://joshashby.com
joshuaashby@joshashby.com
"""
import routeTable as u

import url as bu
import logging
logger = logging.getLogger("seshat.route")


def autoRoute(urls=u.urls):
    def wrapper(HTTPObject):
        urlObject = bu.AutoURL(HTTPObject)

        urls.append(urlObject)
        logger.debug("""Auto generated route table entry for:
        Object: %(objectName)s
        Pattern: %(url)s""" % {"url": urlObject.url, "objectName": HTTPObject.__module__ + "/" + HTTPObject.__name__})
        return HTTPObject
    return wrapper
