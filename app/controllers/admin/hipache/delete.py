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

from models.redis.hipache import hipacheModel as him


@login(["admin"])
@autoRoute()
class delete(MixedObject):
    def POST(self):
        him.remove_route(self.request.id)

        return {"status": "success"}
