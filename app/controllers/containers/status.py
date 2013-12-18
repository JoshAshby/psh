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

from seshat.actions import NotFound, Unauthorized
from errors.general import NotFoundError

from models.rethink.container import containerModel as cm


@login()
@autoRoute()
class status(MixedObject):
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

        return {"status": con.status}
