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

from seshat.actions import NotFound, Unauthorized
from errors.general import NotFoundError

from models.rethink.container import containerModel as cm


@login()
@autoRoute()
class view(MixedObject):
    _title = "Containers"
    _default_tmpl = "public/containers/view"
    def GET(self):
        try:
            con = cm.Container(self.request.id)
        except NotFoundError:
            return NotFound()

        if not self.request.session.has_admin or \
            (con.user_id!=self.request.session.id):
              return Unauthorized()

        if con.disable:
            self.view.template = "public/containers/disabled"
            return self.view

        self.view.title = con.name

        self.view.data = {"container": con}

        return self.view

    def POST(self):
        try:
            con = cm.Container(self.request.id)
        except NotFoundError:
            return NotFound()

        if not self.request.session.has_admin or \
            (con.user_id!=self.request.session.id):
              return Unauthorized()

        if con.disable:
            self.view.template = "public/containers/disabled"
            return self.view

        domains = self.request.getParam("domains", "")
        http_port = self.request.getParam("http_port")

        if domains or http_port:
            if type(domains) is not list:
                domains = [domains]

            con.update_http_port(http_port, domains)

        return Redirect("/containers/"+con.id)
