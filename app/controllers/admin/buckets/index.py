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

from utils.paginate import Paginate


@login(["admin"])
@autoRoute()
class index(HTMLObject):
    _title = "Buckets"
    _defaultTmpl = "admin/buckets/index"
    def GET(self):
        page = Paginate(self.request.buckets.list, self.request)
        f = page.pail

        self.view.data = {"buckets": f, "page": page}
        self.view.scripts = ["admin/bucket"]

        return self.view
