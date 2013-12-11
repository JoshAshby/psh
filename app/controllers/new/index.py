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

from models.rethink.dockerfile import dockerfileModel as dfm

@login()
@autoRoute()
class index(HTMLObject):
    _title = "New Dockerfile"
    _defaultTmpl = "public/new/index"
    def GET(self):
        return self.view

    def POST(self):
      # TODO: name error handling
        files = self.request.getFile("file")
        name = self.request.getParam("name")
        public = self.request.getParam("public", False)

        if files:
            dockerfile = dfm.Dockerfile.new_dockerfile(self.request.session.id,
                                                       name=name,
                                                       file_obj=files,
                                                       public=public)

        return Redirect("/dockerfiles/"+dockerfile.id)
