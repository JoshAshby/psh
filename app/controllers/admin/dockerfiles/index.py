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

from models.utils import dbUtils as dbu
from utils.paginate import Paginate


@login(["admin"])
@autoRoute()
class index(MixedObject):
    _title = "Dockerfiles"
    _default_tmpl = "admin/dockerfiles/index"
    def GET(self):
        if not self.request.id:
            disabled = self.request.getParam("d", False)
            if disabled:
                q = dbu.rql_where_not(dfm.Dockerfile.table, "disable", True)
                res = RethinkCollection(dfm.Dockerfile, query=q)
            else:
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

        if self.request.command == "update":
            public = self.request.getParam("public", False)
            dockerfile.public = public
            dockerfile.save()

        if self.request.command == "rebuild":
            dockerfile.queue_build()

        if self.request.command == "disable":
            dockerfile.disable = not dockerfile.disable
            dockerfile.save()

        return Redirect("/admin/dockerfiles/"+self.request.id)
