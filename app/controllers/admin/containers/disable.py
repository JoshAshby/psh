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
class disable(MixedObject):
    def POST(self):
        if not self.request.id:
            return Redirect("/admin/containers")

        try:
            con = cm.Container(self.request.id)
        except NotFoundError:
            return NotFound()

        con.disable = not con.disable
        con.queue_action("stop")
        con.save()

        status = "disabled" if con.disable else "enabled"
        return {"status": status}
