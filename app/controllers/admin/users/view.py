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
from seshat.baseObject import MixedObject
from seshat.objectMods import login
from seshat.actions import NotFound

import models.rethink.user.userModel as um
from errors.general import NotFoundError


@autoRoute()
@login(["admin"])
class view(MixedObject):
    _title = "Users"
    _defaultTmpl = "admin/users/view"
    def GET(self):
        self._type = "HTML"
        try:
            user = um.User(self.request.id)
            user.format()

            self.view.scripts = ["pillbox", "user", "lib/typeahead.min"]
            self.view.stylesheets = ["pillbox"]

            self.view.data = {"user": user}
            return self.view

        except NotFoundError:
            return NotFound()

    def POST(self):
        self._type = "JSON"
        # TODO: Update ze model
        pass
