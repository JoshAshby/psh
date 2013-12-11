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

import rethinkdb as r
from rethinkORM import RethinkCollection

from models.rethink.dockerfile import dockerfileModel as dfm

from utils.paginate import Paginate


@login()
@autoRoute()
class mine(MixedObject):
    _title = "My Dockerfiles"
    _default_tmpl = "public/dockerfiles/mine"
    def GET(self):
        q = r.table(dfm.Dockerfile.table).filter({"user": self.request.session.id})
        res = RethinkCollection(dfm.Dockerfile, query=q)
        page = Paginate(res, self.request, "name")

        self.view.data = {"page": page}

        return self.view