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

import rethinkdb as r
from rethinkORM import RethinkCollection

from models.rethink.dockerfile import dockerfileModel as dfm

from utils.paginate import Paginate

commands = [
    None,
    "copy"
    ]


@autoRoute()
class index(MixedObject):
    _title = "Dockerfiles"
    _default_tmpl = "public/dockerfiles/index"
    def GET(self):
        if not self.request.id:
            q = r.table(dfm.Dockerfile.table).filter({"public": True})
            res = RethinkCollection(dfm.Dockerfile, query=q)
            page = Paginate(res, self.request, "name")

            self.view.data = {"page": page}

            return self.view
        else:
            try:
                dockerfile = dfm.Dockerfile(self.request.id)

            except NotFoundError:
                return NotFound()

            if not self.request.session.has_admin and \
                (dockerfile.user != self.request.session.id and \
                not dockerfile.public):
                  return Unauthorized()

            if self.request.command not in commands:
                return NotFound()

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

        return Redirect("/dockerfiles/"+self.request.id_extended)
