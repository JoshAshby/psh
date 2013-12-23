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

from seshat.actions import NotFound, Redirect

from models.redis.hipache import hipacheModel as him


@login(["admin"])
@autoRoute()
class view(MixedObject):
    _title = "Hipache Route"
    _default_tmpl = "admin/hipache/view"
    def GET(self):
        self.view.partial("sidebar", "partials/admin/sidebar_links",
                          {"command": "hipache"})
        route = him.Route(self.request.id)

        if not route.domain:
            return NotFound()

        self.view.title = route.domain

        self.view.data = {"route": route}

        return self.view

    def POST(self):
        route = him.Route(self.request.id)

        if not route.domain:
            return NotFound()

        domains = self.request.getParam("domains")

        if domains:
            if type(domains) is not list:
                domains = [domains]

            domains = [ domain for domain in domains if domain ]

            route.reset(domains)

        return Redirect("/admin/hipache/"+self.request.id)
