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
from seshat.MixedObject import MixedObject
from seshat.objectMods import login

from utils.paginate import Paginate


@login(["admin"])
@autoRoute()
class index(MixedObject):
    _title = "Buckets"
    _default_tmpl = "admin/buckets/index"
    def GET(self):
        page = Paginate(self.request.buckets.list, self.request)
        self.view.data = {"page": page}
        return self.view

    def POST(self):
        bucket_id = self.request.id
        self.request.buckets.toggle(bucket_id)
        return {"success": True, "id": bucket_id}
