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
from seshat.baseObject import HTMLObject
from seshat.objectMods import login
from seshat.actions import Redirect

from models.rethink.containerimport containerModel as cm

from errors.general import \
      MissingError


@login()
@autoRoute()
class index(HTMLObject):
    _title = "New Dockerfile"
    _defaultTmpl = "public/new/container"
    def GET(self):
        return self.view

    def POST(self):
        self._type = "JSON"
      # TODO: name error handling
        name = self.request.getParam("name")
        ports = self.request.getParam("ports")
