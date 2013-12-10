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
from seshat.objectMods import login


@login(["admin"])
@autoRoute()
class index(HTMLObject):
    _title = "Admin Home"
    _defaultTmpl = "admin/index/index"
    def GET(self):
        return self.view
