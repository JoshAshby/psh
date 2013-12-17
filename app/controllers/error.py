#!/usr/bin/env python
"""
main error pages

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
from seshat.MixedObject import MixedObject


class error404(MixedObject):
    """
    Returns base 404 error page.
    """
    _title = "404 NOT FOUND"
    _default_tmpl = "error/404"
    def GET(self):
        """
        """
        self.head = ("404 NOT FOUND", [("Content-Type", "text/html")])
        return self.view


class error401(MixedObject):
    """
    Returns base 401 error page.
    """
    _title = "401 UNAUTHORIZED"
    _default_tmpl = "error/401"
    def GET(self):
        """
        """
        self.head = ("401 UNAUTHORIZED", [("Content-Type", "text/html")])
        return self.view


class error500(MixedObject):
    """
    Returns base 500 error page.
    """
    _title = "500 INTERNAL SERVER ERROR"
    _default_tmpl = "error/500"
    def GET(self):
        """
        """
        self.head = ("500 INTERNAL SERVER ERROR", [("Content-Type", "text/html")])
        self.view.data = {"error": self.request.error[0], "tb": self.request.error[1]}
        return self.view
