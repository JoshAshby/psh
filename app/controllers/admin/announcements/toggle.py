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
        announcement_id = self.request.id

        self.request.announcements.toggle_announcement(announcement_id)
        return {"success": True, "id": announcement_id}
