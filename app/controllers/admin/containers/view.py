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
from errors.general import NotFoundError

from models.rethink.container import containerModel as cm


@login(["admin"])
@autoRoute()
class view(MixedObject):
    _title = "Containers"
    _default_tmpl = "admin/containers/view"
    def GET(self):
        self.view.partial("sidebar", "partials/admin/sidebar_links",
                          {"command": "containers"})
        try:
            con = cm.Container(self.request.id)
        except NotFoundError:
            return NotFound()

        self.view.title = con.name

        self.view.data = {"container": con}

        return self.view

    def POST(self):
        if not self.request.id:
            return Redirect("/admin/containers")

        try:
            con = cm.Container(self.request.id)
        except NotFoundError:
            return NotFound()

        domains = self.request.getParam("domains", "")
        http_port = self.request.getParam("http_port")

        if domains or http_port:
            if type(domains) is not list:
                domains = [domains]

            domains = [ domain for domain in domains if domain ]

            con.update_http_port(http_port, domains)

        return Redirect("/admin/containers/"+self.request.id)
