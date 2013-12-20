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

from seshat.actions import NotFound
from errors.general import NotFoundError

from models.rethink.container import containerModel as cm


@login(["admin"])
@autoRoute()
class view(MixedObject):
    _title = "Containers"
    _default_tmpl = "admin/containers/view"
    def GET(self):
        try:
            con = cm.Container(self.request.id)
        except NotFoundError:
            return NotFound()

        self.view.title = con.name

        self.view.data = {"container": con}

        return self.view
