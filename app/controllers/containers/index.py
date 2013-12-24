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

from rethinkORM import RethinkCollection
from models.rethink.container import containerModel as cm

from models.utils import dbUtils as dbu
from utils.paginate import Paginate


@login()
@autoRoute()
class index(MixedObject):
    _title = "Containers"
    _default_tmpl = "public/containers/index"
    def GET(self):
        self.view.partial("sidebar", "partials/public/sidebar_links",
                          {"command": "containers"})
        q = dbu.rql_where_not(cm.Container.table, "disable", True)\
            .filter({"user_id": self.request.session.id})

        res = RethinkCollection(cm.Container, query=q)
        page = Paginate(res, self.request, "name")

        self.view.data = {"page": page}

        return self.view
