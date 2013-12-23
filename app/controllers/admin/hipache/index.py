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

from utils.paginate import Paginate


@login(["admin"])
@autoRoute()
class index(MixedObject):
    _title = "Hipache Routes"
    _default_tmpl = "admin/hipache/index"
    def GET(self):
        self.view.partial("sidebar", "partials/admin/sidebar_links",
                          {"command": "hipache"})
        letter = self.request.getParam("q")
        routes = him.routes(letter+"*")
        page = Paginate(routes, self.request, "domain")

        self.view.data = {"page": page}

        return self.view
