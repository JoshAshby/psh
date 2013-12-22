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

from seshat.actions import Redirect

from models.redis.hipache import hipacheModel as him


@login(["admin"])
@autoRoute()
class new(MixedObject):
    _title = "New Hipache Route"
    _default_tmpl = "admin/hipache/new"
    def GET(self):
        return self.view

    def POST(self):
        source = self.request.getParam("source")
        route = him.Route(source)

        if route.name:
            self.request.session.push_alert("A route entry for that already exists, please edit it, or remove it before trying to make a new route with the same source.")
            return Redirect("/admin/hipache/"+source)

        domains = self.request.getParam("destination")

        name = ":".join([self.request.session.username, source])

        if type(domains) is not list:
            domains = [domains]

        domains = [ domain for domain in domains if domain ]
        domains.insert(0, name)
        route.add(domains)

        return Redirect("/admin/hipache/"+source)
