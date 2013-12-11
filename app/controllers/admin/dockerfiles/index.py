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

from seshat.actions import NotFound, Redirect
from errors.general import NotFoundError

from rethinkORM import RethinkCollection

from models.rethink.dockerfile import dockerfileModel as dfm

from utils.paginate import Paginate


@login(["admin"])
@autoRoute()
class index(MixedObject):
    _title = "Dockerfiles"
    _default_tmpl = "admin/dockerfiles/index"
    def GET(self):
        if not self.request.id:
            res = RethinkCollection(dfm.Dockerfile)
            page = Paginate(res, self.request, "name")

            self.view.data = {"page": page}

            return self.view
        else:
            try:
                dockerfile = dfm.Dockerfile(self.request.id)
            except NotFoundError:
                return NotFound()

            self.view.template = "admin/dockerfiles/view"
            self.request.title = dockerfile.name

            self.view.data = {"dockerfile": dockerfile}

            return self.view

    def POST(self):
        if not self.request.id:
            return Redirect("/admin/dockerfiles")

        try:
            dockerfile = dfm.Dockerfile(self.request.id)
        except NotFoundError:
            return NotFound()

        public = self.request.getParam("public", False)

        dockerfile.public = public
        dockerfile.save()

        return Redirect("/admin/dockerfiles/"+self.request.id_extended)
