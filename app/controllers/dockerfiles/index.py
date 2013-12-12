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

from seshat.actions import NotFound, Redirect, Unauthorized
from errors.general import NotFoundError

from rethinkORM import RethinkCollection

from models.rethink.dockerfile import dockerfileModel as dfm

from models.utils import dbUtils as dbu
from utils.paginate import Paginate

commands = [
    None,
    "copy",
    "update",
    "rebuild"
    ]


@autoRoute()
class index(MixedObject):
    _title = "Dockerfiles"
    _default_tmpl = "public/dockerfiles/index"
    def GET(self):
        if not self.request.id:
            q = dbu.rql_where_not(dfm.Dockerfile.table, "disable", True).filter({"public": True})
            res = RethinkCollection(dfm.Dockerfile, query=q)
            page = Paginate(res, self.request, "name")

            self.view.data = {"page": page}

            return self.view
        else:
            try:
                dockerfile = dfm.Dockerfile(self.request.id)
            except NotFoundError:
                return NotFound()

            if not self.request.session.has_admin or \
                (dockerfile.user != self.request.session.id and \
                not dockerfile.public):
                  return Unauthorized()

            if self.request.command not in commands:
                return NotFound()

            if dockerfile.disable:
                self.view.template = "public/dockerfiles/disabled"
                return self.view

            if not self.request.command:
                self.view.template = "public/dockerfiles/view"
            else:
                self.view.template = "public/dockerfiles/"+self.request.command

            self.request.title = dockerfile.name

            self.view.data = {"dockerfile": dockerfile}

            return self.view

    def POST(self):
        if not self.request.id:
            return Redirect("/dockerfiles")

        if self.request.command not in commands:
            return NotFound()

        try:
            dockerfile = dfm.Dockerfile(self.request.id)
        except NotFoundError:
            return NotFound()

        if dockerfile.disable:
            self.view.template = "public/dockerfiles/disabled"
            return self.view

        if self.request.command == "copy":
            new_dock = dockerfile
            del new_dock.id
            new_dock.user = self.request.session.id

            new_dock.save()

            return Redirect("/dockerfiles/"+new_dock.id)

        else:
            if not self.request.session.has_admin or \
                (dockerfile.user != self.request.session.id and \
                not dockerfile.public):
                  return Unauthorized()

            if self.request.command == "update":
                public = self.request.getParam("public", False)

                dockerfile.public = public
                dockerfile.save()

            elif self.request.command == "rebuild":
                dockerfile.queue_build()

            return Redirect("/dockerfiles/"+self.request.id)
