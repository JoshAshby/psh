#!/usr/bin/env python
"""

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
from seshat.route import autoRoute
from seshat.baseObject import HTMLObject


@autoRoute()
class about(HTMLObject):
    """
    """
    _title = "about"
    _defaultTmpl = "public/about/about"
    def GET(self):
        self.view.data = {"header": "<h1>About Psh PaaS</h1>"}
        return self.view
