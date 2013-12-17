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


@login(["admin"])
@autoRoute()
class toggle(MixedObject):
    def POST(self):
        self._type = "JSON"
        bucket_id = self.request.id

        self.request.buckets.toggle(bucket_id)
        return {"success": True, "id": bucket_id}
